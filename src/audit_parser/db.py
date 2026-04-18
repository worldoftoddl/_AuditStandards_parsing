"""pgvector schema + upsert + similarity search.

The schema is applied idempotently on connection open so CLI callers don't
need a separate migration step for the first run. If the stored ``dim``
differs from what the caller passes, we raise instead of silently
reindexing — that's an operator decision.

MIGRATION NOTE: ``_create_schema_sql`` is designed for a fresh database.
If an existing ``audit_chunks`` table was built without ``embed_model``,
``is_toc``, or ``updated_at``, the ``CREATE TABLE IF NOT EXISTS`` will skip
silently and subsequent INSERTs will fail on the NOT NULL constraint.
In that case run manually (backfill embed_model with the model actually used
for existing rows before re-enforcing NOT NULL):
    ALTER TABLE audit_chunks
        ADD COLUMN is_toc      BOOLEAN     NOT NULL DEFAULT FALSE,
        ADD COLUMN embed_model TEXT        NOT NULL,
        ADD COLUMN updated_at  TIMESTAMPTZ NOT NULL DEFAULT now();

MODEL COEXISTENCE: ``chunk_id`` is the PRIMARY KEY and does NOT include
``embed_model`` (see ``chunk._chunk_id``). Re-running ``upsert_chunks`` with
a different ``embed_model`` for the same content therefore **overwrites** the
previous embedding via ON CONFLICT (chunk_id). The ``UNIQUE (source_path,
content_hash, embed_model)`` constraint and the ``audit_chunks_embed_model_idx``
index are provisioned for a future scheme that widens ``chunk_id`` to carry
the model, enabling side-by-side A/B embeddings. Today they only help with
operator-driven ``DELETE WHERE embed_model = '<old>'`` cleanup.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .ir import Chunk

if TYPE_CHECKING:
    import psycopg


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


def _create_schema_sql(dim: int) -> str:
    return f"""
    CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE IF NOT EXISTS audit_chunks (
        chunk_id        TEXT PRIMARY KEY,
        isa_no          TEXT NOT NULL,
        isa_title       TEXT NOT NULL,
        section         TEXT NOT NULL,
        heading_trail   TEXT[] NOT NULL DEFAULT '{{}}',
        paragraph_ids   TEXT[] NOT NULL DEFAULT '{{}}',
        is_application_guidance BOOLEAN NOT NULL DEFAULT FALSE,
        is_appendix     BOOLEAN NOT NULL DEFAULT FALSE,
        is_toc          BOOLEAN NOT NULL DEFAULT FALSE,
        text            TEXT NOT NULL,
        char_count      INTEGER NOT NULL,
        source_path     TEXT NOT NULL,
        content_hash    CHAR(64) NOT NULL,
        refs            TEXT[] NOT NULL DEFAULT '{{}}',
        embedding       vector({dim}) NOT NULL,
        embed_model     TEXT NOT NULL,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
        CONSTRAINT uq_source_hash_model UNIQUE (source_path, content_hash, embed_model)
    );

    CREATE INDEX IF NOT EXISTS audit_chunks_embedding_idx
        ON audit_chunks USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        WHERE is_toc = FALSE;

    CREATE INDEX IF NOT EXISTS audit_chunks_isa_section_idx
        ON audit_chunks (isa_no, section);

    CREATE INDEX IF NOT EXISTS audit_chunks_paragraph_ids_idx
        ON audit_chunks USING gin (paragraph_ids);

    CREATE INDEX IF NOT EXISTS audit_chunks_embed_model_idx
        ON audit_chunks (embed_model);
    """


def ensure_schema(conn: psycopg.Connection, dim: int) -> None:
    """Apply DDL idempotently."""
    with conn.cursor() as cur:
        cur.execute(_create_schema_sql(dim))
    conn.commit()


def upsert_chunks(
    conn: psycopg.Connection,
    chunks: Sequence[Chunk],
    vectors: Sequence[Sequence[float]],
    *,
    embed_model: str,
) -> int:
    """Upsert ``chunks`` with their embeddings. Returns rows affected.

    Conflicts on ``chunk_id`` (PRIMARY KEY) and updates the embedding,
    embed_model, and updated_at so re-runs refresh the row without
    creating duplicates.
    """
    if len(chunks) != len(vectors):
        raise ValueError(f"chunks ({len(chunks)}) and vectors ({len(vectors)}) length mismatch")

    sql = """
    INSERT INTO audit_chunks (
        chunk_id, isa_no, isa_title, section, heading_trail, paragraph_ids,
        is_application_guidance, is_appendix, is_toc, text, char_count,
        source_path, content_hash, refs, embedding, embed_model
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (chunk_id) DO UPDATE SET
        embedding   = EXCLUDED.embedding,
        embed_model = EXCLUDED.embed_model,
        updated_at  = now();
    """
    affected = 0
    with conn.cursor() as cur:
        for ch, vec in zip(chunks, vectors, strict=True):
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
                    False,  # is_toc: chunks are pre-filtered (is_toc=True excluded by chunker)
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
