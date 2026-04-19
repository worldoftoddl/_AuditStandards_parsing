"""End-to-end smoke: ISA 200 chunks → BGE-M3 embed → pgvector upsert → search.

Run:
    .venv/bin/python scripts/smoke_isa200.py

Prerequisites:
    - audit_standards DB reachable via PG_HOST/PG_PORT/PG_USER/PG_PASSWORD
    - ``sentence-transformers`` installed (``pip install -e .[embedding-local]``)
    - ``.work/isa200_chunks.jsonl`` produced from ``parsed/chunks.jsonl``

The script does not touch the eval harness; it only proves the ingest +
search path works end-to-end with the Phase 2d schema v3.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import psycopg

from audit_parser.cli import _resolve_dsn
from audit_parser.db import ensure_schema, search, upsert_chunks
from audit_parser.embed import BgeEmbedder, EmbedCache, EmbedRequest, embed_with_cache
from audit_parser.ir import Chunk

CHUNKS_PATH = Path(".work/isa200_chunks.jsonl")
CACHE_PATH = Path(".embed_cache.sqlite")

SMOKE_QUERIES = [
    "감사인의 전반적인 목적은 무엇인가",
    "전문가적 의구심을 유지하는 이유",
    "감사증거의 충분성과 적합성",
    "감사기준에 따른 감사의 수행",
    "재무보고체계의 수용가능성",
]


def _load_chunks(path: Path) -> list[Chunk]:
    out: list[Chunk] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(Chunk(**json.loads(line)))
    return out


def main() -> None:
    # Force audit_standards DB regardless of .env default.
    os.environ["PG_DATABASE"] = "audit_standards"
    dsn = _resolve_dsn(None)

    print(f"loading {CHUNKS_PATH} …")
    chunks = _load_chunks(CHUNKS_PATH)
    print(f"  {len(chunks)} chunks")

    print("initializing BGE-M3 embedder (first run downloads ~2.5 GB) …")
    t0 = time.time()
    embedder = BgeEmbedder()
    print(f"  ready in {time.time() - t0:.1f}s, dim={embedder.dim}")

    cache = EmbedCache(CACHE_PATH)
    try:
        print(f"embedding {len(chunks)} chunks …")
        t0 = time.time()
        reqs = [EmbedRequest(content_hash=c.content_hash, text=c.text) for c in chunks]
        vectors = embed_with_cache(embedder, reqs, cache)
        print(f"  done in {time.time() - t0:.1f}s")
    finally:
        cache.close()

    assert len(vectors) == len(chunks)
    assert all(len(v) == embedder.dim for v in vectors)

    print(f"upserting to {dsn.split('@')[-1]} …")
    with psycopg.connect(dsn) as conn:
        ensure_schema(conn, embedder.dim)
        n = upsert_chunks(conn, chunks, vectors, embed_model=embedder.model)
        print(f"  upserted {n} rows (model={embedder.model})")

        print("\nrunning smoke queries:")
        for q in SMOKE_QUERIES:
            t0 = time.time()
            qvec = embedder.embed_query(q)
            hits = search(conn, qvec, top_k=3)
            dt = (time.time() - t0) * 1000
            print(f"\n  Q: {q}  [{dt:.0f} ms]")
            for h in hits:
                ids = ",".join(h.paragraph_ids) or "-"
                snippet = h.text.replace("\n", " ")[:80]
                print(f"    {h.score:.3f}  {h.chunk_id:<20} ids={ids:<8} {snippet}…")


if __name__ == "__main__":
    main()
