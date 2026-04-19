"""Embed eval-subset chunks with Upstage solar and upsert to audit_chunks_eval_upstage.

Steps:
1. Parse docs/eval/queries.yaml → collect expected_primary + expected_related chunk IDs
2. Resolve logical paths (e.g. "200:13.(c)") via eval.resolve_logical_path (DRY reuse)
3. Load matching Chunk objects from parsed/chunks.jsonl
4. Embed passages with solar-embedding-1-large-passage (EmbedCache-backed)
5. Upsert to audit_chunks_eval_upstage (drop_first=True to apply new schema)
6. Embed 26 query texts with solar-embedding-1-large-query (single batch)
7. Save query vectors to .work/eval_query_vectors.jsonl (for eval harness)
8. Report row count + estimated Upstage API cost

Run:
    .venv/bin/python scripts/embed_eval_upstage.py

Prerequisites:
    - UPSTAGE_API_KEY set (via .env or env var)
    - PG_* set to audit_standards DB
    - parsed/chunks.jsonl present (must be Phase 3 format with block_ordinal)
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import psycopg
import yaml
from dotenv import load_dotenv

from audit_parser.cli import _resolve_dsn
from audit_parser.db_eval import EVAL_PASSAGE_MODEL, ensure_eval_schema, upsert_eval_chunks
from audit_parser.embed import EmbedCache, EmbedRequest, UpstageEmbedder, embed_with_cache
from audit_parser.eval import resolve_logical_path
from audit_parser.ir import Chunk

load_dotenv()

QUERIES_PATH = Path("docs/eval/queries.yaml")
CHUNKS_PATH = Path("parsed/chunks.jsonl")
CACHE_PATH = Path(".embed_cache.sqlite")
QUERY_VECTORS_PATH = Path(".work/eval_query_vectors.jsonl")

# Upstage pricing: ~$0.10 / 1M tokens (conservative estimate)
_COST_PER_TOKEN = 0.10 / 1_000_000
_COST_LIMIT_USD = 2.0


# ── helpers ────────────────────────────────────────────────────────────────

def _load_chunks(path: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(Chunk(**json.loads(line)))
    return chunks


def _resolve_by_para_id(chunks: list[Chunk], raw_id: str) -> str | None:
    """Resolve old-format ``{isa}:{para_id}`` by paragraph_ids field lookup.

    queries.yaml still uses pre-Phase-3 chunk_id strings (e.g. ``"210:6"``).
    The new format is ``"210:00361:6"``.  This resolver bridges the gap by
    finding the first chunk where ``isa_no`` matches and ``para_id`` appears
    in ``paragraph_ids``.  Logical-path entries (containing ``"."``) are
    skipped — those are handled by ``resolve_logical_path``.
    """
    if ":" not in raw_id:
        return None
    isa_no, para_id = raw_id.split(":", 1)
    if "." in para_id:  # logical path — not ours to handle
        return None
    for c in chunks:
        if c.isa_no == isa_no and para_id in c.paragraph_ids:
            return c.chunk_id
    return None


def _collect_eval_subset(
    chunks: list[Chunk],
    queries: list[dict],
) -> tuple[list[Chunk], list[str]]:
    """Resolve all expected chunk IDs from queries.yaml and return matching Chunks.

    Three-tier resolution (in order):
    1. Direct chunk_id match (future-proof once queries.yaml is updated)
    2. ``eval.resolve_logical_path`` for ``{isa}:{N}.(x)`` logical paths
    3. ``_resolve_by_para_id`` for old-format ``{isa}:{para_id}`` strings
       whose chunk_id changed in the Phase 3 block_ordinal migration

    Returns ``(eval_chunks, unresolved_paths)``.
    """
    chunk_map = {c.chunk_id: c for c in chunks}
    target_ids: set[str] = set()
    unresolved: list[str] = []

    for q in queries:
        for raw_id in (
            q.get("expected_primary_chunks", []) + q.get("expected_related_chunks", [])
        ):
            if raw_id in chunk_map:
                target_ids.add(raw_id)
                continue
            concrete = resolve_logical_path(chunks, raw_id)
            if concrete:
                target_ids.add(concrete)
                continue
            concrete = _resolve_by_para_id(chunks, raw_id)
            if concrete:
                target_ids.add(concrete)
            else:
                unresolved.append(f"{q['id']}:{raw_id}")

    return (
        [chunk_map[cid] for cid in sorted(target_ids) if cid in chunk_map],
        unresolved,
    )


def _estimate_tokens(texts: list[str]) -> int:
    """Rough estimate: 1 token ≈ 4 characters (conservative for Korean text)."""
    return sum(len(t) for t in texts) // 4


# ── main ───────────────────────────────────────────────────────────────────

def main() -> None:
    os.environ["PG_DATABASE"] = "audit_standards"
    dsn = _resolve_dsn(None)

    # 1. Load queries
    with QUERIES_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    queries: list[dict] = data["queries"]
    print(f"Loaded {len(queries)} queries from {QUERIES_PATH}")

    # 2. Load all chunks (Phase 3 format — block_ordinal required)
    print(f"Loading {CHUNKS_PATH} …")
    all_chunks = _load_chunks(CHUNKS_PATH)
    print(f"  {len(all_chunks)} total chunks")

    # 3. Resolve eval subset
    eval_chunks, unresolved = _collect_eval_subset(all_chunks, queries)
    if unresolved:
        print(f"  WARNING: {len(unresolved)} paths unresolved: {unresolved[:8]}")
    print(f"  Eval subset: {len(eval_chunks)} chunks")

    # 4. Cost guard
    passage_texts = [c.text for c in eval_chunks]
    query_texts = [q["query"] for q in queries]
    est_tokens = _estimate_tokens(passage_texts + query_texts)
    est_cost = est_tokens * _COST_PER_TOKEN
    print(f"\nEstimated cost: ~{est_tokens:,} tokens → ~${est_cost:.4f} USD")
    if est_cost > _COST_LIMIT_USD:
        raise RuntimeError(
            f"Estimated cost ${est_cost:.4f} exceeds ${_COST_LIMIT_USD} limit. "
            "Aborting — get leader approval before proceeding."
        )

    # 5. Initialize embedder + cache
    embedder = UpstageEmbedder()
    cache = EmbedCache(CACHE_PATH)

    try:
        # 6. Embed passages (cache-backed — content_hash hit expected)
        print(f"\nEmbedding {len(eval_chunks)} passages ({embedder.passage_model}) …")
        t0 = time.time()
        passage_reqs = [
            EmbedRequest(content_hash=c.content_hash, text=c.text)
            for c in eval_chunks
        ]
        passage_vectors = embed_with_cache(embedder, passage_reqs, cache)
        print(f"  Done in {time.time() - t0:.1f}s  dim={len(passage_vectors[0])}")

        # 7. Embed queries (query model, single batch, no cache needed)
        print(f"Embedding {len(queries)} queries ({embedder.query_model}) …")
        t0 = time.time()
        query_vectors = embedder.embed_queries(query_texts)
        print(f"  Done in {time.time() - t0:.1f}s")

        # 8. Save query vectors for eval harness
        QUERY_VECTORS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with QUERY_VECTORS_PATH.open("w", encoding="utf-8") as f:
            for q, vec in zip(queries, query_vectors, strict=True):
                f.write(json.dumps({"id": q["id"], "query": q["query"], "vector": vec}) + "\n")
        print(f"Query vectors → {QUERY_VECTORS_PATH}  ({len(query_vectors)} rows)")

    finally:
        cache.close()

    # 9. Upsert to DB (drop_first=True → apply new schema with block_ordinal)
    print(f"\nUpserting to {dsn.split('@')[-1]} …")
    with psycopg.connect(dsn) as conn:
        ensure_eval_schema(conn, drop_first=True)

        rows = [
            {
                "chunk_id": c.chunk_id,
                "isa_no": c.isa_no,
                "section": c.section,
                "heading_trail": c.heading_trail,
                "paragraph_ids": c.paragraph_ids,
                "block_ordinal": c.block_ordinal,
                "text": c.text,
            }
            for c in eval_chunks
        ]
        n = upsert_eval_chunks(conn, rows, passage_vectors, embed_model=EVAL_PASSAGE_MODEL)

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM audit_chunks_eval_upstage;")
            total_rows = cur.fetchone()[0]

    print(f"  Upserted {n} → total {total_rows} rows in audit_chunks_eval_upstage")

    # 10. Final cost report
    actual_tokens = _estimate_tokens(passage_texts + query_texts)
    print(f"\n{'='*40}")
    print("Upstage API Cost Report")
    print(f"  Passages : ~{_estimate_tokens(passage_texts):,} tokens ({len(eval_chunks)} chunks)")
    print(f"  Queries  : ~{_estimate_tokens(query_texts):,} tokens ({len(queries)} queries)")
    print(f"  Total    : ~{actual_tokens:,} tokens")
    print(f"  Est. cost: ~${actual_tokens * _COST_PER_TOKEN:.4f} USD")
    print(f"  DB rows  : {total_rows}")
    print(f"{'='*40}")


if __name__ == "__main__":
    main()
