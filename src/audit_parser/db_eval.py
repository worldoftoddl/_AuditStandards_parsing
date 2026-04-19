"""Eval-subset table DDL + upsert + generic search adapter.

Manages ``audit_chunks_eval_upstage`` (vector(4096), Upstage solar embeddings)
alongside the primary ``audit_chunks`` (vector(1024), BGE-M3).

HNSW is intentionally omitted: pgvector limits HNSW to dim ≤ 2000, and the
eval subset is ~150 rows, so a sequential scan is faster anyway.

``search_eval`` also serves as the generic search path for the A/B-2
companion table ``audit_chunks_notrail`` — pass ``table="audit_chunks_notrail"``
to the caller. Both tables share the same column projection in the SELECT.

is_toc note: ``audit_chunks_eval_upstage`` has no ``is_toc`` column; the eval
subset is pre-filtered to non-TOC chunks at ingest time. ``audit_chunks_notrail``
does have ``is_toc`` but all rows are inserted with ``is_toc=FALSE`` by
``db.upsert_chunks``, so omitting the filter here is safe and consistent.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from .db import SearchHit, _vector_literal

if TYPE_CHECKING:
    import psycopg

EVAL_TABLE = "audit_chunks_eval_upstage"
EVAL_DIM = 4096
EVAL_PASSAGE_MODEL = "solar-embedding-1-large-passage"


def ensure_eval_schema(conn: psycopg.Connection, *, drop_first: bool = False) -> None:
    """Create eval table idempotently.

    Pass ``drop_first=True`` to drop-and-recreate (e.g. after a chunk_id
    schema migration where existing rows use the old format).
    """
    with conn.cursor() as cur:
        if drop_first:
            cur.execute(f"DROP TABLE IF EXISTS {EVAL_TABLE};")
        cur.execute(f"""
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS {EVAL_TABLE} (
            chunk_id      TEXT PRIMARY KEY,
            isa_no        TEXT NOT NULL,
            section       TEXT NOT NULL,
            heading_trail TEXT[] NOT NULL DEFAULT '{{}}',
            paragraph_ids TEXT[] NOT NULL DEFAULT '{{}}',
            block_ordinal INTEGER NOT NULL DEFAULT 0,
            text          TEXT NOT NULL,
            embedding     vector({EVAL_DIM}) NOT NULL,
            embed_model   TEXT NOT NULL DEFAULT '{EVAL_PASSAGE_MODEL}',
            created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """)
    conn.commit()


def upsert_eval_chunks(
    conn: psycopg.Connection,
    rows: Sequence[dict],
    vectors: Sequence[Sequence[float]],
    *,
    embed_model: str = EVAL_PASSAGE_MODEL,
) -> int:
    """Upsert eval-subset rows with their embeddings. Returns rows affected.

    Each ``rows`` dict must have keys: chunk_id, isa_no, section,
    heading_trail, paragraph_ids, block_ordinal, text.
    """
    if len(rows) != len(vectors):
        raise ValueError(f"rows ({len(rows)}) and vectors ({len(vectors)}) length mismatch")

    sql = f"""
    INSERT INTO {EVAL_TABLE} (
        chunk_id, isa_no, section, heading_trail, paragraph_ids,
        block_ordinal, text, embedding, embed_model
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (chunk_id) DO UPDATE SET
        embedding     = EXCLUDED.embedding,
        embed_model   = EXCLUDED.embed_model,
        block_ordinal = EXCLUDED.block_ordinal;
    """
    affected = 0
    with conn.cursor() as cur:
        for row, vec in zip(rows, vectors, strict=True):
            cur.execute(
                sql,
                (
                    row["chunk_id"],
                    row["isa_no"],
                    row["section"],
                    row["heading_trail"],
                    row["paragraph_ids"],
                    row.get("block_ordinal", 0),
                    row["text"],
                    _vector_literal(vec),
                    embed_model,
                ),
            )
            affected += cur.rowcount
    conn.commit()
    return affected


def search_eval(
    conn: psycopg.Connection,
    query_vector: Sequence[float],
    *,
    table: str = EVAL_TABLE,
    top_k: int = 10,
    isa_no: str | None = None,
) -> list[SearchHit]:
    """Cosine-distance kNN on a named eval table (sequential scan).

    ``table`` is an internal parameter — never pass user-supplied input here.
    Usable for ``audit_chunks_eval_upstage`` (Upstage, A/B-1) and
    ``audit_chunks_notrail`` (BGE-notrail, A/B-2).
    """
    vec_lit = _vector_literal(query_vector)
    where_clauses: list[str] = []
    filter_params: list[object] = []
    if isa_no is not None:
        where_clauses.append("isa_no = %s")
        filter_params.append(isa_no)
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    sql = f"""
    SELECT chunk_id, isa_no, section, paragraph_ids, heading_trail, text,
           (embedding <=> %s) AS distance
    FROM {table}
    {where_sql}
    ORDER BY embedding <=> %s
    LIMIT %s;
    """
    # First %s = SELECT distance, filter params, second %s = ORDER BY, LIMIT
    params: list[object] = [vec_lit, *filter_params, vec_lit, top_k]

    hits: list[SearchHit] = []
    with conn.cursor() as cur:
        cur.execute(sql, params)
        for row in cur.fetchall():
            cid, isa, sec, pids, trail, text, dist = row
            hits.append(
                SearchHit(
                    chunk_id=cid,
                    isa_no=isa,
                    section=sec,
                    paragraph_ids=list(pids),
                    heading_trail=list(trail),
                    text=text,
                    score=1.0 - float(dist),
                )
            )
    return hits
