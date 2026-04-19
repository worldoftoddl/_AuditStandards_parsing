"""Command-line entry for the parsing → embedding → pgvector pipeline.

Subcommands:
    parse   — DOCX → JSON IR (``parsed/doc.json``)
    render  — JSON IR → per-ISA Markdown (``parsed/md/*.md``)
    chunk   — JSON IR → chunks JSONL (``parsed/chunks.jsonl``)
    embed   — chunks JSONL → cached vectors
    upsert  — chunks JSONL + cache → pgvector
    search  — query → top-k from pgvector
    profile — style-distribution stats (reproduces Phase 1 counts)

Each subcommand is intentionally cheap and local; the full pipeline
composes them rather than running a single monolithic command.
"""

from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

from .chunk import chunk_document
from .docx_reader import read_docx
from .embed import (
    DEFAULT_DIM,
    DEFAULT_QUERY_MODEL,
    BgeEmbedder,
    EmbedCache,
    EmbedRequest,
    UpstageEmbedder,
    embed_with_cache,
)
from .ir import Block, Chunk, Document, Standard
from .markdown import render_document
from .structure import build_document

app = typer.Typer(help="KICPA 감사인증기준 DOCX → pgvector pipeline")
console = Console()


def _make_embedder(kind: str = "passage") -> Any:
    """Pick an embedder based on ``EMBED_PROVIDER`` env.

    ``kind="passage"`` for ingestion (store vectors) and ``kind="query"``
    for search-time embeddings. Upstage uses different endpoints; BGE
    uses the same model for both but normalizes the same way.
    """
    provider = os.environ.get("EMBED_PROVIDER", "bge").lower()
    if provider == "upstage":
        if kind == "query":
            return UpstageEmbedder(passage_model=DEFAULT_QUERY_MODEL)
        return UpstageEmbedder()
    if provider == "bge":
        return BgeEmbedder()
    raise typer.BadParameter(f"Unknown EMBED_PROVIDER={provider!r} (use 'bge' or 'upstage')")


def _resolve_dsn(explicit: str | None) -> str:
    """Return a Postgres DSN in precedence order:
    explicit CLI flag > PG_DSN env > assembled PG_HOST/PORT/DATABASE/USER/PASSWORD.

    User and password are URL-quoted so ``@``, ``:``, ``/``, or non-ASCII
    characters in secrets do not break the DSN.
    """
    from urllib.parse import quote

    if explicit:
        return explicit
    dsn = os.environ.get("PG_DSN")
    if dsn:
        return dsn
    host = os.environ.get("PG_HOST")
    db = os.environ.get("PG_DATABASE")
    user = os.environ.get("PG_USER")
    if not (host and db and user):
        raise typer.BadParameter(
            "No DSN configured. Set --dsn, PG_DSN, or PG_HOST/PG_DATABASE/PG_USER."
        )
    port = os.environ.get("PG_PORT", "5432")
    password = os.environ.get("PG_PASSWORD", "")
    user_q = quote(user, safe="")
    auth = f"{user_q}:{quote(password, safe='')}" if password else user_q
    return f"postgresql://{auth}@{host}:{port}/{db}"


# ── Serialization helpers ───────────────────────────────────────────────────
def _block_to_dict(b: Block) -> dict:
    d = dataclasses.asdict(b)
    d["source_path"] = str(b.source_path)
    d["num_pr"] = {"num_id": b.num_pr.num_id, "ilvl": b.num_pr.ilvl} if b.num_pr else None
    d["heading_trail"] = list(b.heading_trail)
    return d


def _document_to_dict(doc: Document) -> dict:
    return {
        "source_path": str(doc.source_path),
        "preamble": [_block_to_dict(b) for b in doc.preamble],
        "standards": [
            {
                "number": s.number,
                "title": s.title,
                "blocks": [_block_to_dict(b) for b in s.blocks],
            }
            for s in doc.standards
        ],
        "footnotes": doc.footnotes,
    }


def _dict_to_block(d: dict) -> Block:
    from .ir import NumPr

    np = d.get("num_pr")
    return Block(
        block_id=d["block_id"],
        source_path=Path(d["source_path"]),
        ordinal=d["ordinal"],
        style_id=d["style_id"],
        text=d["text"],
        raw_text=d["raw_text"],
        num_pr=NumPr(num_id=np["num_id"], ilvl=np["ilvl"]) if np else None,
        kind=d["kind"],
        level=d["level"],
        heading_trail=tuple(d["heading_trail"]),
        section=d["section"],
        paragraph_id=d["paragraph_id"],
        is_application_guidance=d["is_application_guidance"],
        is_toc=d["is_toc"],
        refs=list(d.get("refs", [])),
        footnote_ids=list(d.get("footnote_ids", [])),
        table_rows=list(d.get("table_rows", [])),
        continuation_of=d.get("continuation_of"),
    )


def _load_document(path: Path) -> Document:
    data = json.loads(path.read_text(encoding="utf-8"))
    doc = Document(source_path=Path(data["source_path"]))
    doc.preamble = [_dict_to_block(b) for b in data["preamble"]]
    doc.footnotes = data["footnotes"]
    for s in data["standards"]:
        std = Standard(number=s["number"], title=s["title"])
        std.blocks = [_dict_to_block(b) for b in s["blocks"]]
        doc.standards.append(std)
    return doc


def _write_chunks(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(dataclasses.asdict(c), ensure_ascii=False) + "\n")


def _load_chunks(path: Path) -> list[Chunk]:
    out: list[Chunk] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            out.append(Chunk(**json.loads(line)))
    return out


# ── Subcommands ─────────────────────────────────────────────────────────────
@app.command()
def parse(
    source: Annotated[Path, typer.Argument(help="Input DOCX path")],
    output: Annotated[Path, typer.Option(help="Output JSON path")] = Path("parsed/doc.json"),
) -> None:
    """DOCX → classified IR (JSON)."""
    raw, fns, spec = read_docx(source)
    doc = build_document(source, raw, fns, spec)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(_document_to_dict(doc), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    console.print(
        f"[green]parse[/] {len(doc.standards)} standards, {len(doc.all_blocks())} blocks → {output}"
    )


@app.command()
def render(
    doc_json: Annotated[Path, typer.Argument(help="Parsed doc.json")] = Path("parsed/doc.json"),
    output: Annotated[Path, typer.Option(help="Output directory for *.md")] = Path("parsed/md"),
) -> None:
    """JSON IR → per-ISA Markdown."""
    doc = _load_document(doc_json)
    paths = render_document(doc, output)
    console.print(f"[green]render[/] {len(paths)} files → {output}")


@app.command()
def chunk(
    doc_json: Annotated[Path, typer.Argument(help="Parsed doc.json")] = Path("parsed/doc.json"),
    output: Annotated[Path, typer.Option(help="Output chunks JSONL")] = Path("parsed/chunks.jsonl"),
) -> None:
    """JSON IR → retrieval-ready chunks (JSONL)."""
    doc = _load_document(doc_json)
    chunks = chunk_document(doc)
    _write_chunks(chunks, output)
    console.print(f"[green]chunk[/] {len(chunks)} chunks → {output}")


@app.command()
def embed(
    chunks_jsonl: Annotated[Path, typer.Argument(help="Input chunks JSONL")] = Path(
        "parsed/chunks.jsonl"
    ),
    cache_path: Annotated[Path, typer.Option(help="Embedding cache path")] = Path(
        ".embed_cache.sqlite"
    ),
) -> None:
    """Populate the embedding cache for every chunk without pgvector writes."""
    chunks = _load_chunks(chunks_jsonl)
    embedder = _make_embedder("passage")
    cache = EmbedCache(cache_path)
    try:
        reqs = [EmbedRequest(content_hash=c.content_hash, text=c.text) for c in chunks]
        vectors = embed_with_cache(embedder, reqs, cache)
    finally:
        cache.close()
    console.print(
        f"[green]embed[/] {len(chunks)} chunks, {sum(1 for v in vectors if v)} vectors cached"
    )


@app.command()
def upsert(
    chunks_jsonl: Annotated[Path, typer.Argument()] = Path("parsed/chunks.jsonl"),
    cache_path: Annotated[Path, typer.Option()] = Path(".embed_cache.sqlite"),
    dsn: Annotated[
        str | None,
        typer.Option(
            "--dsn",
            help="Postgres DSN; defaults to PG_DSN env or PG_HOST/PG_DATABASE/PG_USER trio",
        ),
    ] = None,
) -> None:
    """Upsert chunks + embeddings into pgvector."""
    import psycopg

    from .db import ensure_schema, upsert_chunks

    dsn = _resolve_dsn(dsn)

    chunks = _load_chunks(chunks_jsonl)
    embedder = _make_embedder("passage")
    cache = EmbedCache(cache_path)
    reqs = [EmbedRequest(content_hash=c.content_hash, text=c.text) for c in chunks]
    vectors = embed_with_cache(embedder, reqs, cache)
    cache.close()

    with psycopg.connect(dsn) as conn:
        ensure_schema(conn, embedder.dim)
        n = upsert_chunks(conn, chunks, vectors, embed_model=embedder.model)
    console.print(f"[green]upsert[/] {n} rows (model: {embedder.model})")


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Natural-language query")],
    top_k: Annotated[int, typer.Option("--top-k")] = 10,
    isa_no: Annotated[str | None, typer.Option("--isa")] = None,
    section: Annotated[str | None, typer.Option("--section")] = None,
    dsn: Annotated[str | None, typer.Option("--dsn")] = None,
) -> None:
    """Embed a query and return top-k chunks from pgvector."""
    import psycopg

    from .db import search as db_search

    dsn = _resolve_dsn(dsn)
    embedder = _make_embedder("query")
    qvec = embedder.embed_query(query)
    with psycopg.connect(dsn) as conn:
        hits = db_search(conn, qvec, top_k=top_k, isa_no=isa_no, section=section)

    table = Table(title=f"Top {len(hits)} matches for {query!r}")
    table.add_column("score", justify="right")
    table.add_column("isa")
    table.add_column("section")
    table.add_column("ids")
    table.add_column("text", overflow="fold")
    for h in hits:
        table.add_row(
            f"{h.score:.3f}",
            h.isa_no,
            h.section,
            ",".join(h.paragraph_ids),
            h.text[:120] + ("…" if len(h.text) > 120 else ""),
        )
    console.print(table)


@app.command()
def eval_run(
    queries: Annotated[Path, typer.Option("--queries")] = Path("docs/eval/queries.yaml"),
    chunks_jsonl: Annotated[Path, typer.Option("--chunks")] = Path("parsed/chunks.jsonl"),
    table: Annotated[str, typer.Option("--table")] = "audit_chunks",
    top_k: Annotated[int, typer.Option("--top-k")] = 10,
    output: Annotated[Path, typer.Option("--output")] = Path(".work/eval_latest.json"),
    dsn: Annotated[str | None, typer.Option("--dsn")] = None,
) -> None:
    """Run the eval harness against a chosen pgvector table.

    The chunks file is only used to resolve logical chunk-ids
    (``{isa}:{N}.(x)``) into concrete ids — no embeddings are generated
    from it. The actual search hits come from the pgvector table.
    """
    import json

    import psycopg

    from .db import SearchHit
    from .eval import load_queries, result_to_dict, run_eval, summarize

    dsn = _resolve_dsn(dsn)
    chunks = _load_chunks(chunks_jsonl)
    cases, resolver_log = load_queries(queries, chunks)
    console.print(
        f"[green]eval[/] {len(cases)} queries × table={table} (top_k={top_k}) "
        f"resolver_log={len(resolver_log)} entries"
    )

    embedder = _make_embedder("query")
    with psycopg.connect(dsn) as conn:
        def _search_fn(qvec: list[float], k: int) -> list[SearchHit]:
            # Inline query to allow per-table routing without exporting
            # every parameter shape from db.search.
            sql = f"""
            SELECT chunk_id, isa_no, section, paragraph_ids, heading_trail, text,
                   (embedding <=> %s::vector) AS distance
            FROM {table}
            WHERE is_toc = FALSE
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """
            from .db import _vector_literal

            lit = _vector_literal(qvec)
            with conn.cursor() as cur:
                cur.execute(sql, (lit, lit, k))
                hits = []
                for cid, isa, sec, pids, trail, text, dist in cur.fetchall():
                    hits.append(
                        SearchHit(
                            chunk_id=cid,
                            isa_no=isa,
                            section=sec,
                            paragraph_ids=list(pids) if pids else [],
                            heading_trail=list(trail) if trail else [],
                            text=text,
                            score=1.0 - float(dist),
                        )
                    )
                return hits

        results = run_eval(embedder, _search_fn, cases, top_k=top_k)

    summary = summarize(results)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "table": table,
                "provider": os.environ.get("EMBED_PROVIDER", "bge"),
                "embed_model": getattr(embedder, "model", "?"),
                "by_category": summary.by_category,
                "overall": summary.overall,
                "ci": {k: list(v) for k, v in summary.ci.items()},
                "unresolved_paths": summary.unresolved_paths,
                "resolver_log": [
                    {
                        "query_id": e.query_id,
                        "logical_path": e.logical_path,
                        "concrete_chunk_id": e.concrete_chunk_id,
                        "parent_section": e.parent_section,
                        "block_ordinal": e.block_ordinal,
                    }
                    for e in resolver_log
                ],
                "results": [result_to_dict(r) for r in results],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    tbl = Table(title=f"eval summary — {table}")
    tbl.add_column("category")
    tbl.add_column("n", justify="right")
    tbl.add_column("recall@5", justify="right")
    tbl.add_column("precision@5", justify="right")
    tbl.add_column("MRR", justify="right")
    tbl.add_column("nDCG@10", justify="right")
    for cat, row in summary.by_category.items():
        tbl.add_row(
            cat,
            f"{int(row['n'])}",
            f"{row['recall@5']:.3f}",
            f"{row['precision@5']:.3f}",
            f"{row['mrr']:.3f}",
            f"{row['ndcg@10']:.3f}",
        )
    tbl.add_row(
        "OVERALL",
        f"{int(summary.overall['n'])}",
        f"{summary.overall['recall@5']:.3f}",
        f"{summary.overall['precision@5']:.3f}",
        f"{summary.overall['mrr']:.3f}",
        f"{summary.overall['ndcg@10']:.3f}",
        style="bold",
    )
    console.print(tbl)
    lo, hi = summary.ci["recall@5"]
    console.print(
        f"recall@5 95% CI: [{lo:.3f}, {hi:.3f}]  "
        f"unresolved paths: {len(summary.unresolved_paths)}"
    )
    console.print(f"[green]written[/] {output}")


@app.command()
def profile(
    source: Annotated[Path, typer.Argument(help="Input DOCX path")],
) -> None:
    """Print style distribution for a DOCX (reproduces Phase 1 counts)."""
    from collections import Counter

    raw, fns, _ = read_docx(source)
    styles = Counter(b.style_id or "<NO_STYLE>" for b in raw)
    table = Table(title=f"{source.name}: {len(raw)} blocks, {len(fns)} footnotes")
    table.add_column("style")
    table.add_column("count", justify="right")
    for s, c in styles.most_common():
        table.add_row(s, str(c))
    console.print(table)
    console.print(f"expected embedding dim: {DEFAULT_DIM} (Upstage)")


if __name__ == "__main__":  # pragma: no cover
    app()
