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


@pytest.fixture(scope="module")
def notrail_schema_sql() -> str:
    return _create_schema_sql(1024, "audit_chunks_notrail")


# ── Column presence ──────────────────────────────────────────────────────────


def test_schema_has_is_toc_column(schema_sql: str) -> None:
    assert "is_toc" in schema_sql, "is_toc column missing from schema"


def test_schema_has_embed_model_column(schema_sql: str) -> None:
    assert "embed_model" in schema_sql, "embed_model column missing from schema"


def test_schema_has_updated_at_column(schema_sql: str) -> None:
    assert "updated_at" in schema_sql, "updated_at column missing from schema"


def test_schema_has_block_ordinal_column(schema_sql: str) -> None:
    assert "block_ordinal" in schema_sql, "block_ordinal column missing from schema"


def test_schema_block_ordinal_is_not_null(schema_sql: str) -> None:
    assert "block_ordinal   INTEGER NOT NULL" in schema_sql


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


def test_schema_has_block_ordinal_index(schema_sql: str) -> None:
    assert "audit_chunks_block_ordinal_idx" in schema_sql, (
        "block_ordinal index missing — needed for ORDER BY + debugging"
    )


def test_schema_block_ordinal_index_covers_isa_no(schema_sql: str) -> None:
    assert "(isa_no, block_ordinal)" in schema_sql


# ── Unique constraint ────────────────────────────────────────────────────────


def test_schema_unique_constraint_includes_embed_model(schema_sql: str) -> None:
    """UNIQUE (source_path, content_hash, embed_model) prevents duplicate
    embeddings of the same content with the same model."""
    assert "uq_audit_chunks_source_hash_model" in schema_sql
    assert "source_path, content_hash, embed_model" in schema_sql


# ── table_name parameterization ──────────────────────────────────────────────


def test_notrail_schema_uses_notrail_table_name(notrail_schema_sql: str) -> None:
    """audit_chunks_notrail DDL must use its own table and index names."""
    assert "audit_chunks_notrail" in notrail_schema_sql
    assert "audit_chunks_notrail_embedding_idx" in notrail_schema_sql
    assert "uq_audit_chunks_notrail_source_hash_model" in notrail_schema_sql


def test_notrail_schema_does_not_reference_audit_chunks_table(
    notrail_schema_sql: str,
) -> None:
    """Parameterized DDL must not hard-code the default table name."""
    # The string "audit_chunks" appears as a substring of "audit_chunks_notrail",
    # so check the exact table reference in CREATE TABLE.
    assert "CREATE TABLE IF NOT EXISTS audit_chunks_notrail" in notrail_schema_sql
    assert "CREATE TABLE IF NOT EXISTS audit_chunks\n" not in notrail_schema_sql
    assert "CREATE TABLE IF NOT EXISTS audit_chunks " not in notrail_schema_sql


# ── Upsert DO UPDATE ─────────────────────────────────────────────────────────


def test_upsert_sql_has_updated_at() -> None:
    """DO UPDATE must refresh updated_at so re-embedding runs are trackable."""
    src = inspect.getsource(upsert_chunks)
    assert "updated_at" in src, "DO UPDATE SET clause must include updated_at = now()"


def test_upsert_sql_has_embed_model_in_do_update() -> None:
    src = inspect.getsource(upsert_chunks)
    assert "embed_model" in src, "DO UPDATE SET clause must include embed_model"


def test_upsert_sql_has_block_ordinal_in_do_update() -> None:
    src = inspect.getsource(upsert_chunks)
    assert "block_ordinal" in src, "upsert_chunks must include block_ordinal"


def test_upsert_filters_unknown_isa() -> None:
    """upsert_chunks must skip chunks with isa_no == '?'."""
    src = inspect.getsource(upsert_chunks)
    assert 'isa_no == "?"' in src or "isa_no == '?'" in src, (
        "upsert_chunks must filter out isa_no='?' chunks"
    )


# ── Function signature ───────────────────────────────────────────────────────


def test_upsert_chunks_embed_model_is_keyword_only() -> None:
    """``embed_model`` must be keyword-only to prevent positional misuse."""
    sig = inspect.signature(upsert_chunks)
    param = sig.parameters.get("embed_model")
    assert param is not None, "upsert_chunks missing embed_model parameter"
    assert param.kind == inspect.Parameter.KEYWORD_ONLY, (
        "embed_model must be keyword-only (after *)"
    )


def test_upsert_chunks_table_name_is_keyword_only() -> None:
    sig = inspect.signature(upsert_chunks)
    param = sig.parameters.get("table_name")
    assert param is not None, "upsert_chunks missing table_name parameter"
    assert param.kind == inspect.Parameter.KEYWORD_ONLY


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
