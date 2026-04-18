"""End-to-end integration tests on the real target DOCX.

These tests skip when ``raw/`` is not available (CI environments without
the copyrighted corpus). They lock down structural invariants that we
relied on during Phase 2a design.
"""

from collections import Counter

import pytest

from audit_parser.docx_reader import read_docx
from audit_parser.structure import build_document

# Cross-verified against an independent abstractNum simulator run by the
# `audit-domain-expert` teammate on 2026-04-18. Each entry is
# ``(isa_no, first_requirement_paragraph_id)``.
ISA_FIRST_REQUIREMENT = [
    ("200", "14"),
    ("210", "6"),
    ("220", "8"),
    ("230", "7"),
    ("240", "13"),
    ("250", "13"),
    ("260", "11"),
    ("265", "7"),
    ("300", "5"),
    ("315", "13"),
    ("320", "10"),
    ("330", "5"),
    ("402", "9"),
    ("500", "6"),
    ("510", "5"),
    ("520", "5"),
    ("530", "6"),
    ("540", "13"),
    ("550", "11"),
    ("560", "6"),
    ("570", "10"),
    ("580", "9"),
    ("600", "11"),
    ("610", "15"),
    ("620", "7"),
]


def test_docx_reader_returns_all_styles(target_docx):
    raw, _, _ = read_docx(target_docx)
    styles = {b.style_id for b in raw}
    for expected in ("10", "2", "3", "a1", "A", "A0", "ad", "aff3"):
        assert expected in styles, f"style {expected} missing"


def test_exactly_36_standards(target_docx):
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    assert len(doc.standards) == 36


def test_standards_have_core_sections(target_docx):
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    # At least 30 of 36 ISAs should cover the four structural sections.
    # (Some ISAs omit "적용 및 기타 설명자료", e.g. shorter ones.)
    core = {"intro", "objective", "definitions", "requirements"}
    with_core = 0
    for std in doc.standards:
        secs = {b.section for b in std.blocks if b.section}
        if core.issubset(secs):
            with_core += 1
    assert with_core >= 30, f"only {with_core}/36 ISAs have all core sections"


def test_paragraph_id_coverage_requirements(target_docx):
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    a1_blocks = [b for b in doc.all_blocks() if b.style_id == "a1" and not b.is_toc]
    with_id = sum(1 for b in a1_blocks if b.paragraph_id)
    # The Phase 2a benchmark was 97.1%; leave a small margin for future edits.
    assert with_id / max(len(a1_blocks), 1) >= 0.95


def test_paragraph_id_coverage_application(target_docx):
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    A_blocks = [b for b in doc.all_blocks() if b.style_id == "A" and not b.is_toc]
    with_id = sum(1 for b in A_blocks if b.paragraph_id)
    assert with_id / max(len(A_blocks), 1) >= 0.90


@pytest.mark.parametrize("isa_no,expected_first_id", ISA_FIRST_REQUIREMENT)
def test_isa_first_requirement_number(target_docx, isa_no, expected_first_id):
    """The first a1-body block in each ISA's 'requirements' section must
    match the golden value cross-verified by the domain expert."""
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    std = next((s for s in doc.standards if s.number == isa_no), None)
    assert std is not None, f"ISA {isa_no} not found in document"
    reqs = [
        b
        for b in std.blocks
        if b.section == "requirements" and b.style_id == "a1" and b.paragraph_id is not None
    ]
    assert reqs, f"ISA {isa_no} has no numbered requirement bodies"
    assert reqs[0].paragraph_id == expected_first_id, (
        f"ISA {isa_no} first requirement id: got {reqs[0].paragraph_id!r}, "
        f"expected {expected_first_id!r}"
    )


def test_nested_list_numbering(target_docx):
    """ISA 210 has requirement 6 with (a), (b) list items, and (a) has
    (i), (ii), (iii) sub-items. Verify the counter walks correctly."""
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    std = next(s for s in doc.standards if s.number == "210")
    ids = [
        b.paragraph_id
        for b in std.blocks
        if b.section == "requirements" and b.paragraph_id is not None
    ]
    # the 6, (a), (b), (i), (ii), (iii) sequence must appear contiguously
    head = ids[:6]
    assert head == ["6", "(a)", "(b)", "(i)", "(ii)", "(iii)"]


def test_toc_entries_filtered(target_docx):
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    toc_blocks = [b for b in doc.all_blocks() if b.is_toc]
    # The draft counted 761 `ad` blocks plus NO_STYLE TOC headers.
    assert len(toc_blocks) >= 700


def test_footnotes_loaded(target_docx):
    raw, fns, spec = read_docx(target_docx)
    assert len(fns) >= 100  # observed ~851


def test_table_blocks_detected(target_docx):
    raw, _, _ = read_docx(target_docx)
    tables = [b for b in raw if b.is_table]
    assert len(tables) >= 10  # observed ~74


def test_every_body_block_has_trail_or_is_preamble(target_docx):
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    missing: list[str] = []
    for std in doc.standards:
        for b in std.blocks:
            if b.kind.startswith("heading_"):
                continue
            if b.is_toc:
                continue
            if len(b.heading_trail) < 1:
                missing.append(b.block_id)
    assert len(missing) < 50, f"{len(missing)} body blocks without heading_trail"


def test_kind_distribution_sanity(target_docx):
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    kinds = Counter(b.kind for b in doc.all_blocks())
    assert kinds["heading_standard"] == 36
    assert kinds["heading_section"] >= 150  # ~182 expected
    assert kinds["heading_appendix"] >= 30  # ~41 expected
    assert kinds["paragraph_body"] > 3000
