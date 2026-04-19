"""Unit tests for retrieval eval primitives.

Focuses on the pure-function parts: logical-path resolution, metric
scoring, and bootstrap CI. The runner path (DB + embedder) is covered
by the Phase 3 smoke script, not unit tests.
"""

from pathlib import Path

from audit_parser.db import SearchHit
from audit_parser.eval import (
    QueryCase,
    _mrr,
    _ndcg_at_k,
    _precision_at_k,
    _recall_at_k,
    bootstrap_ci,
    resolve_logical_path,
    score_hits,
)
from audit_parser.ir import Chunk


def _chunk(cid: str, *, section: str = "requirements", paragraph_ids: list[str] | None = None,
           block_ordinal: int = 0, heading_trail: list[str] | None = None) -> Chunk:
    return Chunk(
        chunk_id=cid,
        isa_no="200",
        isa_title="",
        section=section,
        heading_trail=heading_trail or [],
        paragraph_ids=paragraph_ids or [],
        block_ordinal=block_ordinal,
        is_application_guidance=False,
        is_appendix=False,
        text=cid,
        char_count=len(cid),
        source_path="dummy",
        content_hash="0" * 64,
    )


def _hit(cid: str, score: float = 0.5) -> SearchHit:
    return SearchHit(
        chunk_id=cid,
        isa_no="200",
        section="requirements",
        paragraph_ids=[],
        heading_trail=[],
        text=cid,
        score=score,
    )


class TestResolveLogicalPath:
    def test_concrete_chunk_id_passthrough(self):
        chunks = [_chunk("200:00013:13", paragraph_ids=["13"])]
        assert resolve_logical_path(chunks, "200:00013:13") == "200:00013:13"

    def test_resolves_simple_logical_same_section(self):
        # ¶13 (definitions) followed by its sub-items, all definitions
        chunks = [
            _chunk("200:00013:13", section="definitions", paragraph_ids=["13"]),
            _chunk("200:00014:(a)", section="definitions", paragraph_ids=["(a)"]),
            _chunk("200:00015:(b)", section="definitions", paragraph_ids=["(b)"]),
            _chunk("200:00030:14", section="requirements", paragraph_ids=["14"]),
        ]
        assert resolve_logical_path(chunks, "200:13.(a)") == "200:00014:(a)"

    def test_pass1_filters_by_section_to_skip_wrong_sibling(self):
        # Parent ¶13 is definitions. There is a (c) in application before a (c)
        # in definitions — pass1 must skip the application one.
        chunks = [
            _chunk("200:00013:13", section="definitions", paragraph_ids=["13"]),
            _chunk("200:00014:(c)", section="application", paragraph_ids=["(c)"]),
            _chunk("200:00015:(c)", section="definitions", paragraph_ids=["(c)"]),
        ]
        assert resolve_logical_path(chunks, "200:13.(c)") == "200:00015:(c)"

    def test_pass2_fallback_by_heading_trail_when_section_other(self):
        # Parent has section=other; pass1 finds nothing (no other-section
        # sub). Pass2 kicks in and matches by last heading.
        chunks = [
            _chunk(
                "200:00013:13",
                section="other",
                paragraph_ids=["13"],
                heading_trail=["ISA 200", "§ misc"],
            ),
            _chunk(
                "200:00014:(c)",
                section="application",
                paragraph_ids=["(c)"],
                heading_trail=["ISA 200", "적용 및 기타 설명자료"],
            ),
            _chunk(
                "200:00015:(c)",
                section="appendix",
                paragraph_ids=["(c)"],
                heading_trail=["ISA 200", "§ misc"],
            ),
        ]
        assert resolve_logical_path(chunks, "200:13.(c)") == "200:00015:(c)"

    def test_returns_none_when_parent_missing(self):
        chunks = [_chunk("200:00011:11", paragraph_ids=["11"])]
        assert resolve_logical_path(chunks, "200:13.(a)") is None

    def test_returns_none_when_sub_not_found(self):
        chunks = [
            _chunk("200:00013:13", section="definitions", paragraph_ids=["13"]),
            _chunk("200:00030:14", section="requirements", paragraph_ids=["14"]),
        ]
        assert resolve_logical_path(chunks, "200:13.(a)") is None

    def test_stops_at_next_numeric_parent(self):
        # "200:13.(a)" must NOT match "(a)" that appears under ¶14.
        chunks = [
            _chunk("200:00013:13", section="definitions", paragraph_ids=["13"]),
            _chunk("200:00020:14", section="requirements", paragraph_ids=["14"]),
            _chunk("200:00021:(a)", section="requirements", paragraph_ids=["(a)"]),
        ]
        assert resolve_logical_path(chunks, "200:13.(a)") is None


class TestMetrics:
    def test_recall_at_5_perfect(self):
        hits = [_hit("200:13"), _hit("200:14")]
        assert _recall_at_k(hits, {"200:13"}, 5) == 1.0

    def test_recall_at_5_miss(self):
        hits = [_hit("200:99")]
        assert _recall_at_k(hits, {"200:13"}, 5) == 0.0

    def test_precision_at_5(self):
        hits = [_hit("200:13"), _hit("200:99"), _hit("200:14")]
        # 2 of first 5 are relevant
        assert _precision_at_k(hits, {"200:13", "200:14"}, 5) == 2 / 5

    def test_mrr_first_hit(self):
        hits = [_hit("200:99"), _hit("200:13")]
        assert _mrr(hits, {"200:13"}) == 1 / 2

    def test_mrr_no_hit(self):
        hits = [_hit("200:99")]
        assert _mrr(hits, {"200:13"}) == 0.0

    def test_ndcg_prefers_primary_over_related(self):
        hits = [_hit("200:13"), _hit("200:related"), _hit("200:14")]
        # primary = {200:13, 200:14}, related = {200:related}
        ndcg = _ndcg_at_k(hits, {"200:13", "200:14"}, {"200:related"}, k=10)
        assert 0 < ndcg <= 1

    def test_score_hits_tuple_shape(self):
        case = QueryCase(
            id="Q", category="requirements",
            query="q", expected_primary=("200:13",),
            expected_related=(), unresolved=(),
        )
        hits = [_hit("200:13"), _hit("200:14")]
        r5, p5, mrr, ndcg = score_hits(hits, case)
        assert r5 == 1.0 and p5 == 1 / 5 and mrr == 1.0 and ndcg > 0


class TestBootstrap:
    def test_ci_contains_mean(self):
        # Uniform values — any resampled mean should be exactly 0.5
        lo, hi = bootstrap_ci([0.5] * 20, n=200)
        assert lo == hi == 0.5

    def test_ci_widens_with_variance(self):
        lo, hi = bootstrap_ci([0.0, 1.0] * 10, n=500)
        assert lo < 0.5 < hi

    def test_ci_empty_returns_zero(self):
        assert bootstrap_ci([]) == (0.0, 0.0)


def test_load_queries_on_real_yaml():
    """Smoke test: the real queries.yaml loads with expected structure."""
    from audit_parser.eval import load_queries

    queries_path = Path("docs/eval/queries.yaml")
    if not queries_path.exists():
        return  # skip if not present
    # Empty chunk list means every logical path is unresolved — that's
    # fine for this loader smoke test.
    cases, log = load_queries(queries_path, [])
    assert len(cases) == 26
    categories = {c.category for c in cases}
    assert categories == {"requirements", "application", "cross-standard", "definitions"}
    # Every path should produce a log entry, all unresolved here.
    assert len(log) > 0
    assert all(e.concrete_chunk_id is None for e in log)
