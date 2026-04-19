"""Bulk-embed all ISA chunks (BGE-M3) and load two sides into pgvector.

- ``audit_chunks``          — heading_trail ON (the default production shape)
- ``audit_chunks_notrail``  — heading_trail OFF (Phase 3 A/B-2 comparison)

Run:
    .venv/bin/python scripts/bulk_embed.py

Intentionally loads the BGE model once and streams both chunk sets
through it — the model weights dominate the startup cost, so emitting
``audit_chunks_notrail`` in the same process halves the effective latency.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict
from pathlib import Path

import psycopg

from audit_parser.chunk import chunk_document
from audit_parser.cli import _load_document, _resolve_dsn
from audit_parser.db import _create_schema_sql, ensure_schema, upsert_chunks
from audit_parser.embed import BgeEmbedder, EmbedCache, EmbedRequest, embed_with_cache

DOC_JSON = Path("parsed/doc.json")
CHUNKS_TRAIL = Path("parsed/chunks.jsonl")
CHUNKS_NOTRAIL = Path("parsed/chunks_notrail.jsonl")
CACHE_PATH = Path(".embed_cache.sqlite")
NOTRAIL_TABLE = "audit_chunks_notrail"


def _write_chunks_jsonl(chunks, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")


def _ensure_notrail_table(conn: psycopg.Connection, dim: int) -> None:
    """Sibling schema: same columns as audit_chunks, renamed identifiers.

    Kept as an explicit copy rather than a shared function to avoid
    coupling the primary table's evolution to the A/B comparison.
    """
    sql = _create_schema_sql(dim).replace("audit_chunks", NOTRAIL_TABLE)
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def main() -> None:
    # Force audit_standards even when .env pre-sets PG_DATABASE to a
    # different database (e.g. the shared IFRS instance). setdefault() is
    # too weak for this — we hard-override.
    os.environ["PG_DATABASE"] = "audit_standards"
    dsn = _resolve_dsn(None)

    print(f"loading {DOC_JSON} …")
    doc = _load_document(DOC_JSON)
    print(f"  standards={len(doc.standards)} blocks={len(doc.all_blocks())}")

    print("producing chunk sets (trail ON + OFF) …")
    t0 = time.time()
    chunks_trail = chunk_document(doc, include_heading_trail=True)
    chunks_notrail = chunk_document(doc, include_heading_trail=False)
    print(f"  ON={len(chunks_trail)} OFF={len(chunks_notrail)} in {time.time() - t0:.1f}s")

    _write_chunks_jsonl(chunks_trail, CHUNKS_TRAIL)
    _write_chunks_jsonl(chunks_notrail, CHUNKS_NOTRAIL)

    print("loading BGE-M3 (model weights stay resident for both passes) …")
    t0 = time.time()
    embedder = BgeEmbedder()
    print(f"  ready in {time.time() - t0:.1f}s dim={embedder.dim}")

    cache = EmbedCache(CACHE_PATH)
    try:
        for label, chunks, table in (
            ("trail-ON", chunks_trail, "audit_chunks"),
            ("trail-OFF", chunks_notrail, NOTRAIL_TABLE),
        ):
            print(f"\n[{label}] embedding {len(chunks)} chunks …")
            t0 = time.time()
            reqs = [EmbedRequest(content_hash=c.content_hash, text=c.text) for c in chunks]
            vectors = embed_with_cache(embedder, reqs, cache)
            dt = time.time() - t0
            print(f"  done in {dt:.1f}s ({dt / len(chunks) * 1000:.0f} ms/chunk)")

            print(f"[{label}] upserting into {table} …")
            t0 = time.time()
            with psycopg.connect(dsn) as conn:
                if table == "audit_chunks":
                    ensure_schema(conn, embedder.dim)
                else:
                    _ensure_notrail_table(conn, embedder.dim)
                # Distinct embed_model label so analysts can tell the two runs apart
                # via SELECT even though they live in separate tables.
                model = (
                    f"{embedder.model}:notrail" if table == NOTRAIL_TABLE else embedder.model
                )
                n = upsert_chunks(
                    conn, chunks, vectors, embed_model=model, table_name=table
                )
            print(f"  upserted {n} rows in {time.time() - t0:.1f}s")
    finally:
        cache.close()

    print("\ndone.")


if __name__ == "__main__":
    main()
