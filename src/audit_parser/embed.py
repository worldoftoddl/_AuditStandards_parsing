"""Embedding provider + content-hash cache.

Defaults to Upstage ``solar-embedding-1-large`` (passage for storage,
query for search). A BGE-M3 fallback path is included for local
development when the API key is unset; switching provider requires
purging the cache because embedding dimensions differ.

The cache is a single-table SQLite file keyed by
``(provider, model, content_hash)``.
"""

from __future__ import annotations

import os
import sqlite3
import struct
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

UPSTAGE_URL = "https://api.upstage.ai/v1/embeddings"
DEFAULT_PASSAGE_MODEL = "solar-embedding-1-large-passage"
DEFAULT_QUERY_MODEL = "solar-embedding-1-large-query"
DEFAULT_DIM = 4096


@dataclass(frozen=True)
class EmbedRequest:
    content_hash: str  # SHA-256 hex
    text: str


class Embedder(Protocol):
    """Minimal protocol the CLI/DB layer depends on."""

    provider: str
    model: str
    dim: int

    def embed_passage(self, texts: Sequence[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...


# ── Cache ───────────────────────────────────────────────────────────────────
_SCHEMA = """
CREATE TABLE IF NOT EXISTS embedding_cache (
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    dim INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    vector BLOB NOT NULL,
    PRIMARY KEY (provider, model, content_hash)
);
"""


def _pack(vec: Sequence[float]) -> bytes:
    return struct.pack(f"{len(vec)}f", *vec)


def _unpack(blob: bytes) -> list[float]:
    n = len(blob) // 4
    return list(struct.unpack(f"{n}f", blob))


class EmbedCache:
    """SQLite-backed content-hash cache. Safe across concurrent processes
    thanks to SQLite's file locking."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path))
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def get(self, provider: str, model: str, content_hash: str) -> list[float] | None:
        row = self._conn.execute(
            "SELECT vector FROM embedding_cache WHERE provider=? AND model=? AND content_hash=?",
            (provider, model, content_hash),
        ).fetchone()
        return _unpack(row[0]) if row else None

    def put(
        self,
        provider: str,
        model: str,
        dim: int,
        content_hash: str,
        vector: Sequence[float],
    ) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO embedding_cache VALUES (?,?,?,?,?)",
            (provider, model, dim, content_hash, _pack(vector)),
        )
        self._conn.commit()

    def purge_provider(self, provider: str) -> int:
        cur = self._conn.execute("DELETE FROM embedding_cache WHERE provider=?", (provider,))
        self._conn.commit()
        return cur.rowcount

    def close(self) -> None:
        self._conn.close()


# ── Upstage provider ────────────────────────────────────────────────────────
class UpstageEmbedder:
    """HTTP embedder targeting Upstage's OpenAI-compatible endpoint.

    Batches passages; retries transient failures with exponential backoff.
    """

    provider: str = "upstage"

    def __init__(
        self,
        api_key: str | None = None,
        passage_model: str = DEFAULT_PASSAGE_MODEL,
        query_model: str = DEFAULT_QUERY_MODEL,
        dim: int = DEFAULT_DIM,
        batch_size: int = 16,
    ) -> None:
        self._api_key = api_key or os.environ.get("UPSTAGE_API_KEY", "")
        if not self._api_key:
            raise RuntimeError("UPSTAGE_API_KEY is not set")
        self.passage_model = passage_model
        self.query_model = query_model
        self.model = passage_model
        self.dim = dim
        self.batch_size = batch_size

    def _call(self, model: str, inputs: Sequence[str]) -> list[list[float]]:
        # httpx/tenacity imported here so the package can be imported without
        # optional extras installed (e.g. during parsing-only workflows).
        import httpx
        from tenacity import (
            retry,
            retry_if_exception_type,
            stop_after_attempt,
            wait_exponential,
        )

        @retry(
            retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
            stop=stop_after_attempt(4),
            wait=wait_exponential(multiplier=1, min=1, max=16),
            reraise=True,
        )
        def _post() -> httpx.Response:
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
            payload = {"model": model, "input": list(inputs)}
            with httpx.Client(timeout=httpx.Timeout(60.0)) as client:
                resp = client.post(UPSTAGE_URL, json=payload, headers=headers)
                resp.raise_for_status()
                return resp

        resp = _post()
        data = resp.json()["data"]
        return [item["embedding"] for item in data]

    def embed_passage(self, texts: Sequence[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            out.extend(self._call(self.passage_model, texts[i : i + self.batch_size]))
        return out

    def embed_query(self, text: str) -> list[float]:
        return self._call(self.query_model, [text])[0]


# ── BGE-M3 fallback (local) ─────────────────────────────────────────────────
class BgeEmbedder:
    """Local BGE-M3 via sentence-transformers. Optional — requires the
    ``sentence-transformers`` package to be installed by the caller."""

    provider: str = "bge"

    def __init__(self, model_name: str = "BAAI/bge-m3") -> None:
        # Imported lazily because sentence-transformers is a heavy optional
        # dependency not listed in pyproject.
        from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]

        self._model = SentenceTransformer(model_name)
        self.model = model_name
        self.dim = self._model.get_sentence_embedding_dimension()

    def embed_passage(self, texts: Sequence[str]) -> list[list[float]]:
        arr = self._model.encode(list(texts), normalize_embeddings=True)
        return arr.tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.embed_passage([text])[0]


# ── Cache-wrapped embedder ──────────────────────────────────────────────────
def embed_with_cache(
    embedder: Embedder,
    requests: Iterable[EmbedRequest],
    cache: EmbedCache,
) -> list[list[float]]:
    """Return vectors for each request in order, using the cache to avoid
    re-embedding content we've already seen."""
    reqs = list(requests)
    results: list[list[float] | None] = [None] * len(reqs)
    to_fetch: list[tuple[int, EmbedRequest]] = []

    for i, req in enumerate(reqs):
        cached = cache.get(embedder.provider, embedder.model, req.content_hash)
        if cached is not None:
            results[i] = cached
        else:
            to_fetch.append((i, req))

    if to_fetch:
        texts = [r.text for _, r in to_fetch]
        vectors = embedder.embed_passage(texts)
        for (idx, req), vec in zip(to_fetch, vectors, strict=True):
            if len(vec) != embedder.dim:
                raise RuntimeError(
                    f"embedding dim mismatch for {req.content_hash[:12]}: "
                    f"got {len(vec)}, expected {embedder.dim}"
                )
            cache.put(embedder.provider, embedder.model, embedder.dim, req.content_hash, vec)
            results[idx] = vec

    # At this point every entry must be filled.
    return [r if r is not None else [] for r in results]
