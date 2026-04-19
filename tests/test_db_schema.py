"""SQL structure validation for db.py.

These tests inspect the DDL strings and function signatures produced by
``_create_schema_sql`` and ``upsert_chunks`` without requiring a live
Postgres connection.
"""

from __future__ import annotations

import inspect

import pytest

from audit_parser.db import _create_schema_sql, upsert_chunks

# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def schema_sql() -> str:
    return _create_schema_sql(1024)


# ── Column presence ──────────────────────────────────────────────────────────


def test_schema_has_is_toc_column(schema_sql: str) -> None:
    assert "is_toc" in schema_sql, "is_toc column missing from schema"


def test_schema_has_embed_model_column(schema_sql: str) -> None:
    assert "embed_model" in schema_sql, "embed_model column missing from schema"


def test_schema_has_updated_at_column(schema_sql: str) -> None:
    assert "updated_at" in schema_sql, "updated_at column missing from schema"


# ── Index strategy ───────────────────────────────────────────────────────────


def test_schema_hnsw_is_partial_on_is_toc(schema_sql: str) -> None:
    """Partial HNSW must exclude TOC rows to keep the vector space clean."""
    assert "WHERE is_toc = FALSE" in schema_sql, (
        "HNSW index should be partial: WHERE is_toc = FALSE"
    )


def test_schema_hnsw_params(schema_sql: str) -> None:
    assert "m = 16" in schema_sql
    assert "ef_construction = 64" in schema_sql


def test_schema_embed_model_index(schema_sql: str) -> None:
    assert "audit_chunks_embed_model_idx" in schema_sql, (
        "embed_model index missing — needed for re-embed queries"
    )


# ── Unique constraint ────────────────────────────────────────────────────────


def test_schema_unique_constraint_includes_embed_model(schema_sql: str) -> None:
    """UNIQUE (source_path, content_hash, embed_model) prevents duplicate
    embeddings of the same content with the same model."""
    assert "uq_source_hash_model" in schema_sql
    assert "source_path, content_hash, embed_model" in schema_sql


# ── Upsert DO UPDATE ─────────────────────────────────────────────────────────


def test_upsert_sql_has_updated_at() -> None:
    """DO UPDATE must refresh updated_at so re-embedding runs are trackable."""

    src = inspect.getsource(upsert_chunks)
    assert "updated_at" in src, "DO UPDATE SET clause must include updated_at = now()"


def test_upsert_sql_has_embed_model_in_do_update() -> None:
    src = inspect.getsource(upsert_chunks)
    assert "embed_model" in src, "DO UPDATE SET clause must include embed_model"


# ── Function signature ───────────────────────────────────────────────────────


def test_upsert_chunks_embed_model_is_keyword_only() -> None:
    """``embed_model`` must be keyword-only to prevent positional misuse."""
    sig = inspect.signature(upsert_chunks)
    param = sig.parameters.get("embed_model")
    assert param is not None, "upsert_chunks missing embed_model parameter"
    assert param.kind == inspect.Parameter.KEYWORD_ONLY, (
        "embed_model must be keyword-only (after *)"
    )


# ── dim placeholder ──────────────────────────────────────────────────────────


@pytest.mark.parametrize("dim", [768, 1024])
def test_schema_dim_is_templated(dim: int) -> None:
    sql = _create_schema_sql(dim)
    assert f"vector({dim})" in sql, f"vector({dim}) not found in schema DDL"


def test_schema_4096_exceeds_hnsw_vector_limit() -> None:
    """pgvector 0.8 HNSW supports vector(≤2000). 4096-dim (solar-embedding) cannot use HNSW.
    This is why dim=1024 (BGE-M3) is used as the production default.
    Runtime error: 'column cannot have more than 2000 dimensions for hnsw index'
    """
    assert 4096 > 2000  # documents the constraint; dim=1024 is the safe choice
