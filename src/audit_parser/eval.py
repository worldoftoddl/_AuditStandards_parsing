"""Retrieval eval harness: run ``docs/eval/queries.yaml`` and score results.

Exposes the building blocks separately (``load_queries``, ``score_hits``,
``bootstrap_ci``, ``run_eval``) so the CLI wrapper can compose them for
the Phase 3 dual-gate decision: absolute (recall@5 ≥ 0.70) and relative
(BGE ≥ Upstage × 0.95).

Chunk-id resolver implements the README §3.2 rule: logical paths of the
form ``{isa}:{N}.(x)`` map to the first ``{isa}:(x)`` chunk that appears
after the ``{isa}:{N}`` parent and before the next ``{isa}:{N+k}`` in
document order.
"""

from __future__ import annotations

import math
import random
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import yaml

from .db import SearchHit
from .ir import Chunk

# ── Query types ─────────────────────────────────────────────────────────────
_LOGICAL_PATH = re.compile(r"^(?P<isa>[^:]+):(?P<parent>\d+[A-Za-z]?)\.\((?P<sub>[a-z])\)$")


@dataclass(frozen=True)
class QueryCase:
    id: str
    category: str
    query: str
    expected_primary: tuple[str, ...]  # resolved to concrete chunk_ids
    expected_related: tuple[str, ...]
    # Paths that the resolver could not map; kept for warning reports.
    unresolved: tuple[str, ...]


@dataclass
class QueryResult:
    case: QueryCase
    hits: list[SearchHit]
    recall_at_5: float
    precision_at_5: float
    mrr: float
    ndcg_at_10: float


@dataclass
class EvalSummary:
    """Aggregate metrics across a run, by category + overall."""

    by_category: dict[str, dict[str, float]] = field(default_factory=dict)
    overall: dict[str, float] = field(default_factory=dict)
    ci: dict[str, tuple[float, float]] = field(default_factory=dict)
    unresolved_paths: list[str] = field(default_factory=list)


# ── Chunk-id resolver ───────────────────────────────────────────────────────
_NUMERIC_PARA = re.compile(r"^\d+[A-Za-z]?$")
# Legacy ``{isa}:{para_id}`` shorthand used in queries.yaml — e.g. ``210:6``.
# Maps to the first chunk matching the ``(isa_no, para_id)`` pair. This keeps
# the gold-label file portable across chunk_id format changes.
_SHORT_PATH = re.compile(r"^(?P<isa>[^:.]+):(?P<para>[^:.]+)$")


def resolve_short_path(chunks: Sequence[Chunk], shorthand: str) -> str | None:
    """Resolve an ``{isa}:{para_id}`` shorthand via ``paragraph_ids``.

    Unlike ``resolve_logical_path``, the shorthand has no parent/sub split
    — it simply matches the first chunk in the ISA whose ``paragraph_ids``
    contains the token. Sub-items like ``(c)`` are still technically valid
    but ambiguous; callers should prefer the full logical path
    ``{isa}:{N}.(x)`` for sub-items.
    """
    m = _SHORT_PATH.match(shorthand)
    if not m:
        return None
    isa = m.group("isa")
    para = m.group("para")
    for c in chunks:
        if c.isa_no == isa and para in c.paragraph_ids:
            return c.chunk_id
    return None


def _share_heading_suffix(a: Sequence[str], b: Sequence[str]) -> bool:
    """Fallback sibling test: both trails agree on their last heading."""
    if not a or not b:
        return False
    return a[-1] == b[-1]


def resolve_logical_path(chunks: Sequence[Chunk], logical: str) -> str | None:
    """Resolve an ``{isa}:{N}.(x)`` logical path to a concrete ``chunk_id``.

    Two-pass strategy per the Phase 3 plan ``phase3-chunk-id-v2`` §4:

    1. Identify the parent chunk by ``(isa_no == isa) AND (parent_para in
       paragraph_ids)``. paragraph_ids is used rather than chunk_id strings
       so the resolver is forward-compatible with any chunk_id format change.
    2. Walk forward. Pass 1 accepts the first sub-item whose ``section``
       matches the parent's. Pass 2 (fallback) accepts the first sub-item
       whose ``heading_trail`` shares its last element with the parent's —
       only triggered when Pass 1 finds nothing (e.g. when parent lands in
       ``section == 'other'``).

    The walk stops at the next numeric parent in the same ISA to keep the
    match scoped to the parent paragraph's sub-items.
    """
    m = _LOGICAL_PATH.match(logical)
    if not m:
        return logical if any(c.chunk_id == logical for c in chunks) else None

    isa = m.group("isa")
    parent_para = m.group("parent")
    sub = m.group("sub")
    sub_paren = f"({sub})"

    parent_idx: int | None = None
    parent: Chunk | None = None
    for i, c in enumerate(chunks):
        if c.isa_no == isa and parent_para in c.paragraph_ids:
            parent_idx = i
            parent = c
            break
    if parent is None or parent_idx is None:
        return None

    def _walk(predicate: Callable[[Chunk], bool]) -> str | None:
        for c in chunks[parent_idx + 1 :]:
            if c.isa_no != isa:
                break
            # Stop at the next numeric parent in the same ISA.
            if any(_NUMERIC_PARA.match(p) for p in c.paragraph_ids):
                break
            if sub_paren in c.paragraph_ids and predicate(c):
                return c.chunk_id
        return None

    # Pass 1: same section.
    result = _walk(lambda c: c.section == parent.section)
    if result is not None:
        return result
    # Pass 2 (fallback): shared heading-trail suffix.
    return _walk(lambda c: _share_heading_suffix(c.heading_trail, parent.heading_trail))


@dataclass(frozen=True)
class ResolverLogEntry:
    """Record of one logical-path resolution, kept for post-hoc audit."""

    query_id: str
    logical_path: str
    concrete_chunk_id: str | None
    parent_section: str | None
    block_ordinal: int | None


def _resolve_list(
    chunks: Sequence[Chunk],
    raw: Sequence[str],
    *,
    query_id: str,
    log: list[ResolverLogEntry],
) -> tuple[list[str], list[str]]:
    resolved: list[str] = []
    unresolved: list[str] = []
    by_id = {c.chunk_id: c for c in chunks}

    def _log(logical: str, concrete: str | None) -> None:
        c = by_id.get(concrete) if concrete else None
        log.append(
            ResolverLogEntry(
                query_id=query_id,
                logical_path=logical,
                concrete_chunk_id=concrete,
                parent_section=c.section if c else None,
                block_ordinal=c.block_ordinal if c else None,
            )
        )

    for entry in raw:
        # 1) direct chunk_id match (new full format, or any prior concrete id).
        if entry in by_id:
            resolved.append(entry)
            _log(entry, entry)
            continue
        # 2) logical path ``{isa}:{N}.(x)`` — resolver with 2-pass section fallback.
        concrete = resolve_logical_path(chunks, entry)
        if concrete is not None:
            resolved.append(concrete)
            _log(entry, concrete)
            continue
        # 3) shorthand ``{isa}:{para_id}`` — paragraph_ids lookup.
        concrete = resolve_short_path(chunks, entry)
        if concrete is not None:
            resolved.append(concrete)
            _log(entry, concrete)
            continue
        unresolved.append(entry)
        _log(entry, None)
    return resolved, unresolved


# ── Loader ──────────────────────────────────────────────────────────────────
def load_queries(
    queries_path: Path,
    chunks: Sequence[Chunk],
) -> tuple[list[QueryCase], list[ResolverLogEntry]]:
    """Read queries.yaml and resolve expected chunk paths.

    Returns ``(cases, resolver_log)``. The resolver log contains one entry
    per logical path encountered, for audit-domain-expert's post-eval
    verification that each path mapped to the intended section/ordinal.
    """
    data = yaml.safe_load(queries_path.read_text(encoding="utf-8"))
    cases: list[QueryCase] = []
    log: list[ResolverLogEntry] = []
    for entry in data["queries"]:
        qid = entry["id"]
        primary, unres_p = _resolve_list(
            chunks, entry.get("expected_primary_chunks", []), query_id=qid, log=log
        )
        related, unres_r = _resolve_list(
            chunks, entry.get("expected_related_chunks", []), query_id=qid, log=log
        )
        cases.append(
            QueryCase(
                id=qid,
                category=entry["category"],
                query=entry["query"],
                expected_primary=tuple(primary),
                expected_related=tuple(related),
                unresolved=tuple(unres_p + unres_r),
            )
        )
    return cases, log


# ── Metrics ─────────────────────────────────────────────────────────────────
def _recall_at_k(hits: Sequence[SearchHit], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top_k = {h.chunk_id for h in hits[:k]}
    found = len(top_k & relevant)
    return found / len(relevant)


def _precision_at_k(hits: Sequence[SearchHit], relevant: set[str], k: int) -> float:
    if k == 0:
        return 0.0
    top_k = {h.chunk_id for h in hits[:k]}
    return len(top_k & relevant) / k


def _mrr(hits: Sequence[SearchHit], relevant: set[str]) -> float:
    for i, h in enumerate(hits, start=1):
        if h.chunk_id in relevant:
            return 1.0 / i
    return 0.0


def _ndcg_at_k(
    hits: Sequence[SearchHit],
    primary: set[str],
    related: set[str],
    k: int = 10,
) -> float:
    """Relevance grades: primary=2, related=1, else=0."""

    def grade(chunk_id: str) -> int:
        if chunk_id in primary:
            return 2
        if chunk_id in related:
            return 1
        return 0

    gains = [grade(h.chunk_id) for h in hits[:k]]
    dcg = sum((2**g - 1) / math.log2(i + 2) for i, g in enumerate(gains))

    ideal_grades = sorted(
        [2] * len(primary) + [1] * len(related), reverse=True
    )[:k]
    idcg = sum((2**g - 1) / math.log2(i + 2) for i, g in enumerate(ideal_grades))
    return dcg / idcg if idcg > 0 else 0.0


def score_hits(hits: Sequence[SearchHit], case: QueryCase) -> tuple[float, float, float, float]:
    """Return ``(recall@5, precision@5, mrr, ndcg@10)``.

    Primary chunks are the recall/precision targets; MRR uses the first
    primary hit; nDCG treats primary as relevance=2 and related as 1.
    """
    primary = set(case.expected_primary)
    related = set(case.expected_related)
    return (
        _recall_at_k(hits, primary, 5),
        _precision_at_k(hits, primary, 5),
        _mrr(hits, primary),
        _ndcg_at_k(hits, primary, related, 10),
    )


# ── Bootstrap CI ────────────────────────────────────────────────────────────
def bootstrap_ci(
    values: Sequence[float],
    n: int = 1000,
    alpha: float = 0.05,
    seed: int = 42,
) -> tuple[float, float]:
    """Return ``(lower, upper)`` of the 100(1-alpha)% percentile bootstrap CI."""
    if not values:
        return (0.0, 0.0)
    rng = random.Random(seed)
    size = len(values)
    means = []
    for _ in range(n):
        sample = [values[rng.randrange(size)] for _ in range(size)]
        means.append(sum(sample) / size)
    means.sort()
    lo = means[int((alpha / 2) * n)]
    hi = means[int((1 - alpha / 2) * n) - 1]
    return (lo, hi)


# ── Runner ──────────────────────────────────────────────────────────────────
class Embedder(Protocol):
    def embed_query(self, text: str) -> list[float]: ...


SearchFn = Callable[[list[float], int], list[SearchHit]]


def run_eval(
    embedder: Embedder,
    search_fn: SearchFn,
    cases: Sequence[QueryCase],
    *,
    top_k: int = 10,
) -> list[QueryResult]:
    """Embed each query, run ``search_fn(qvec, top_k)``, score results."""
    results: list[QueryResult] = []
    for case in cases:
        qvec = embedder.embed_query(case.query)
        hits = search_fn(qvec, top_k)
        r5, p5, mrr, ndcg = score_hits(hits, case)
        results.append(
            QueryResult(
                case=case,
                hits=hits,
                recall_at_5=r5,
                precision_at_5=p5,
                mrr=mrr,
                ndcg_at_10=ndcg,
            )
        )
    return results


# ── Aggregation ─────────────────────────────────────────────────────────────
def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def summarize(results: Sequence[QueryResult]) -> EvalSummary:
    """Aggregate per-category + overall + bootstrap CI on recall@5."""
    summary = EvalSummary()

    by_cat: dict[str, list[QueryResult]] = {}
    for r in results:
        by_cat.setdefault(r.case.category, []).append(r)

    for cat, rs in by_cat.items():
        summary.by_category[cat] = {
            "n": float(len(rs)),
            "recall@5": _mean([r.recall_at_5 for r in rs]),
            "precision@5": _mean([r.precision_at_5 for r in rs]),
            "mrr": _mean([r.mrr for r in rs]),
            "ndcg@10": _mean([r.ndcg_at_10 for r in rs]),
        }

    all_r = list(results)
    summary.overall = {
        "n": float(len(all_r)),
        "recall@5": _mean([r.recall_at_5 for r in all_r]),
        "precision@5": _mean([r.precision_at_5 for r in all_r]),
        "mrr": _mean([r.mrr for r in all_r]),
        "ndcg@10": _mean([r.ndcg_at_10 for r in all_r]),
    }
    summary.ci["recall@5"] = bootstrap_ci([r.recall_at_5 for r in all_r])
    summary.ci["ndcg@10"] = bootstrap_ci([r.ndcg_at_10 for r in all_r])

    for r in results:
        summary.unresolved_paths.extend(
            f"{r.case.id}:{p}" for p in r.case.unresolved
        )
    return summary


def result_to_dict(r: QueryResult) -> dict[str, Any]:
    return {
        "id": r.case.id,
        "category": r.case.category,
        "query": r.case.query,
        "expected_primary": list(r.case.expected_primary),
        "expected_related": list(r.case.expected_related),
        "unresolved": list(r.case.unresolved),
        "hits": [
            {"chunk_id": h.chunk_id, "score": h.score, "section": h.section}
            for h in r.hits
        ],
        "recall@5": r.recall_at_5,
        "precision@5": r.precision_at_5,
        "mrr": r.mrr,
        "ndcg@10": r.ndcg_at_10,
    }
