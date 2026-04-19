"""pgvector schema + upsert + similarity search.

The schema is applied idempotently on connection open so CLI callers don't
need a separate migration step for the first run. If the stored ``dim``
differs from what the caller passes, we raise instead of silently
reindexing — that's an operator decision.

MIGRATION NOTE: ``_create_schema_sql`` is designed for a fresh database.
Adding new NOT NULL columns (e.g. ``block_ordinal``) to an existing table
requires a DROP + re-ingest rather than ALTER TABLE, because ``CREATE TABLE
IF NOT EXISTS`` silently skips when the table already exists.

Phase 3 migration steps:
    DROP TABLE IF EXISTS audit_chunks CASCADE;
    -- Re-run bulk_embed.py; ensure_schema will re-create the table.

If you prefer ALTER TABLE (e.g. to preserve indexes during partial migration):
    ALTER TABLE audit_chunks
        ADD COLUMN block_ordinal INTEGER NOT NULL DEFAULT 0;
    -- Backfill block_ordinal from the re-parsed chunks.jsonl before
    -- removing the DEFAULT clause.

MODEL COEXISTENCE: ``chunk_id`` is the PRIMARY KEY and includes
``block_ordinal`` in its format (``{isa}:{block_ordinal:05d}:{para_id}``
as of Phase 3). Re-running ``upsert_chunks`` with a different ``embed_model``
for the same content overwrites the previous embedding via ON CONFLICT
(chunk_id). The ``UNIQUE (source_path, content_hash, embed_model)``
constraint is provisioned for a future scheme that encodes the model in
``chunk_id`` to enable side-by-side A/B embeddings.

A/B EVAL: The companion table ``audit_chunks_eval_upstage`` (vector(4096))
stores Upstage solar embeddings for the eval subset (A/B-1 model axis).
Managed by ``db_eval.py``, not this module.

A/B-2 PREFIX: The companion table ``audit_chunks_notrail`` uses the same
DDL (created via ``_create_schema_sql(dim, 'audit_chunks_notrail')``) and
stores BGE-M3 embeddings of chunk text WITHOUT the heading_trail prefix
(A/B-2 prefix axis). The eval harness calls
``search_eval(conn, vec, table='audit_chunks_notrail')`` for BGE-notrail.
Both tables intentionally omit ``is_toc=TRUE`` rows at upsert time, so
the ``is_toc = FALSE`` filter in ``search()`` is belt-and-suspenders only.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .ir import Chunk

if TYPE_CHECKING:
    import psycopg

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SearchHit:
    chunk_id: str
    isa_no: str
    section: str
    paragraph_ids: list[str]
    heading_trail: list[str]
    text: str
    score: float


def _vector_literal(vec: Sequence[float]) -> str:
    """pgvector accepts '[x,y,z,...]' string literals in text mode, which
    avoids a binary-protocol dependency on the pgvector-python package."""
    return "[" + ",".join(f"{x:.8f}" for x in vec) + "]"


def _create_schema_sql(dim: int, table_name: str = "audit_chunks") -> str:
    t = table_name
    return f"""
    CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE IF NOT EXISTS {t} (
        chunk_id        TEXT PRIMARY KEY,
        isa_no          TEXT NOT NULL,
        isa_title       TEXT NOT NULL,
        section         TEXT NOT NULL,
        heading_trail   TEXT[] NOT NULL DEFAULT '{{}}',
        paragraph_ids   TEXT[] NOT NULL DEFAULT '{{}}',
        is_application_guidance BOOLEAN NOT NULL DEFAULT FALSE,
        is_appendix     BOOLEAN NOT NULL DEFAULT FALSE,
        is_toc          BOOLEAN NOT NULL DEFAULT FALSE,
        block_ordinal   INTEGER NOT NULL,
        text            TEXT NOT NULL,
        char_count      INTEGER NOT NULL,
        source_path     TEXT NOT NULL,
        content_hash    CHAR(64) NOT NULL,
        refs            TEXT[] NOT NULL DEFAULT '{{}}',
        embedding       vector({dim}) NOT NULL,
        embed_model     TEXT NOT NULL,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_{t}_source_hash_model UNIQUE (source_path, content_hash, embed_model)
    );

    CREATE INDEX IF NOT EXISTS {t}_embedding_idx
        ON {t} USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        WHERE is_toc = FALSE;

    CREATE INDEX IF NOT EXISTS {t}_isa_section_idx
        ON {t} (isa_no, section);

    CREATE INDEX IF NOT EXISTS {t}_paragraph_ids_idx
        ON {t} USING gin (paragraph_ids);

    CREATE INDEX IF NOT EXISTS {t}_embed_model_idx
        ON {t} (embed_model);

    CREATE INDEX IF NOT EXISTS {t}_block_ordinal_idx
        ON {t} (isa_no, block_ordinal);
    """


def ensure_schema(
    conn: psycopg.Connection,
    dim: int,
    table_name: str = "audit_chunks",
) -> None:
    """Apply DDL idempotently."""
    with conn.cursor() as cur:
        cur.execute(_create_schema_sql(dim, table_name))
    conn.commit()


def upsert_chunks(
    conn: psycopg.Connection,
    chunks: Sequence[Chunk],
    vectors: Sequence[Sequence[float]],
    *,
    embed_model: str,
    table_name: str = "audit_chunks",
) -> int:
    """Upsert ``chunks`` with their embeddings. Returns rows affected.

    Chunks with ``isa_no == '?'`` (unidentified preamble blocks) are
    silently skipped; the count is logged at INFO level.

    Conflicts on ``chunk_id`` (PRIMARY KEY) and updates the embedding,
    embed_model, block_ordinal, and updated_at so re-runs are idempotent.
    """
    if len(chunks) != len(vectors):
        raise ValueError(f"chunks ({len(chunks)}) and vectors ({len(vectors)}) length mismatch")

    sql = f"""
    INSERT INTO {table_name} (
        chunk_id, isa_no, isa_title, section, heading_trail, paragraph_ids,
        is_application_guidance, is_appendix, is_toc, block_ordinal, text, char_count,
        source_path, content_hash, refs, embedding, embed_model
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (chunk_id) DO UPDATE SET
        embedding     = EXCLUDED.embedding,
        embed_model   = EXCLUDED.embed_model,
        block_ordinal = EXCLUDED.block_ordinal,
        updated_at    = now();
    """
    affected = 0
    filtered = 0
    with conn.cursor() as cur:
        for ch, vec in zip(chunks, vectors, strict=True):
            if ch.isa_no == "?":
                filtered += 1
                continue
            cur.execute(
                sql,
                (
                    ch.chunk_id,
                    ch.isa_no,
                    ch.isa_title,
                    ch.section,
                    ch.heading_trail,
                    ch.paragraph_ids,
                    ch.is_application_guidance,
                    ch.is_appendix,
                    False,  # is_toc: chunker excludes is_toc=True before calling upsert
                    ch.block_ordinal,
                    ch.text,
                    ch.char_count,
                    ch.source_path,
                    ch.content_hash,
                    ch.refs,
                    _vector_literal(vec),
                    embed_model,
                ),
            )
            affected += cur.rowcount
    conn.commit()
    if filtered:
        logger.info("upsert_chunks: skipped %d chunks with isa_no='?'", filtered)
    return affected


def search(
    conn: psycopg.Connection,
    query_vector: Sequence[float],
    *,
    top_k: int = 10,
    isa_no: str | None = None,
    section: str | None = None,
) -> list[SearchHit]:
    """Cosine-distance kNN with optional metadata filters."""
    where_clauses: list[str] = ["is_toc = FALSE"]
    params: list[object] = [_vector_literal(query_vector)]
    if isa_no is not None:
        where_clauses.append("isa_no = %s")
        params.append(isa_no)
    if section is not None:
        where_clauses.append("section = %s")
        params.append(section)
    where_sql = f"WHERE {' AND '.join(where_clauses)}"
    params.append(top_k)

    sql = f"""
    SELECT chunk_id, isa_no, section, paragraph_ids, heading_trail, text,
           (embedding <=> %s) AS distance
    FROM audit_chunks
    {where_sql}
    ORDER BY embedding <=> %s
    LIMIT %s;
    """
    # The query vector is referenced twice (SELECT and ORDER BY); duplicate it.
    params = [params[0], *params[1:-1], params[0], params[-1]]

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
