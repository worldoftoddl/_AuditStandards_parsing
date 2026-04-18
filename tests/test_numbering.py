"""Unit tests for regex extractors and numbering engine."""

from audit_parser.ir import AbstractNum, NumberingSpec, NumLevel
from audit_parser.numbering import (
    NumberingCounter,
    expand_cross_refs,
    extract_cross_refs,
    extract_paragraph_id,
    match_appendix_title,
    match_standard_header,
    match_toc_line,
    split_definition,
)


class TestExpandCrossRefs:
    def test_simple_passthrough(self):
        assert expand_cross_refs(["A22"]) == ["A22"]

    def test_compound_wa(self):
        assert expand_cross_refs(["A22와 A28"]) == ["A22", "A28"]

    def test_compound_comma(self):
        assert expand_cross_refs(["A63, A84"]) == ["A63", "A84"]

    def test_numeric_range(self):
        assert expand_cross_refs(["A20-A22"]) == ["A20", "A21", "A22"]

    def test_paren_range(self):
        assert expand_cross_refs(["12(a)-(c)"]) == ["12(a)", "12(b)", "12(c)"]

    def test_range_and_list_mixed(self):
        got = expand_cross_refs(["A20-A22", "A63", "A84"])
        assert got == ["A20", "A21", "A22", "A63", "A84"]

    def test_dedup_order_preserved(self):
        got = expand_cross_refs(["A22", "A20-A22"])
        assert got == ["A22", "A20", "A21"]

    def test_descending_range_kept_as_is(self):
        assert expand_cross_refs(["A22-A20"]) == ["A22", "A20"]

    def test_mixed_prefix_range_kept_as_is(self):
        # prefix mismatch is not expanded
        assert expand_cross_refs(["A22-B3"]) == ["A22", "B3"]


# ── Paragraph id regex ─────────────────────────────────────────────────────
class TestExtractParagraphId:
    def test_simple_requirement(self):
        pid, rest, is_app = extract_paragraph_id("1. 이 감사기준서는", style_id="a1")
        assert pid == "1"
        assert rest == "이 감사기준서는"
        assert is_app is False

    def test_requirement_with_alpha_suffix(self):
        pid, rest, is_app = extract_paragraph_id("14A. 본문", style_id="a1")
        assert pid == "14A"
        assert is_app is False

    def test_requirement_with_paren(self):
        pid, _, _ = extract_paragraph_id("13(f). 본문", style_id="a1")
        assert pid == "13(f)"

    def test_requirement_range(self):
        pid, _, _ = extract_paragraph_id("1-2. 본문", style_id="a1")
        assert pid == "1-2"

    def test_application_simple(self):
        pid, rest, is_app = extract_paragraph_id("A15. 본문", style_id="A")
        assert pid == "A15"
        assert is_app is True
        assert rest == "본문"

    def test_range_not_a_prefix(self):
        # "A24-A26." appears only as a cross-reference target, not as an
        # actual paragraph id prefix, so the extractor should not match.
        pid, _, _ = extract_paragraph_id("A24-A26. 본문", style_id="A")
        assert pid is None

    def test_no_prefix_returns_none(self):
        pid, rest, _ = extract_paragraph_id("감사인은 독립적이어야 한다.", style_id="a1")
        assert pid is None
        assert rest == "감사인은 독립적이어야 한다."

    def test_leading_whitespace_trimmed(self):
        # callers should normalize; this verifies NFKC of an already-trimmed
        # string still matches.
        pid, _, _ = extract_paragraph_id("5. 본문", style_id="a1")
        assert pid == "5"


# ── Cross-references ───────────────────────────────────────────────────────
class TestExtractCrossRefs:
    def test_single(self):
        assert extract_cross_refs("본문 (문단 15 참조) 끝") == ["15"]

    def test_appendix(self):
        assert extract_cross_refs("(문단 A24 참조)") == ["A24"]

    def test_range(self):
        assert extract_cross_refs("(문단 A24-A26 참조)") == ["A24-A26"]

    def test_multiple(self):
        refs = extract_cross_refs("문단 3과 문단 A15, 문단 14A 참조.")
        assert refs == ["3", "A15", "14A"]

    def test_none(self):
        assert extract_cross_refs("본문") == []


# ── Reference-text normalization ───────────────────────────────────────────
class TestNormalizeRefText:
    def test_en_dash_in_range(self):
        # "A24–A26" (U+2013 en-dash) should be treated the same as "A24-A26".
        assert extract_cross_refs("(문단 A24\u2013A26 참조)") == ["A24-A26"]

    def test_em_dash_in_paren_range(self):
        # "49(a)—(c)" (U+2014 em-dash) captured and expanded via paren shorthand.
        refs = extract_cross_refs("(문단 49(a)\u2014(c) 참조)")
        assert expand_cross_refs(refs) == ["49(a)", "49(b)", "49(c)"]

    def test_figure_dash_in_range(self):
        # U+2012 figure dash is another typographer variant used in PDFs.
        refs = extract_cross_refs("(문단 A12\u2012A14 참조)")
        assert expand_cross_refs(refs) == ["A12", "A13", "A14"]

    def test_prefix_omitted_range(self):
        # "A38-40" is shorthand where the translator dropped the second "A".
        assert expand_cross_refs(["A38-40"]) == ["A38", "A39", "A40"]

    def test_prefix_omitted_via_extract(self):
        # Same shape reaching us through the full extract→expand pipeline.
        refs = extract_cross_refs("(문단 A38-40 참조)")
        assert expand_cross_refs(refs) == ["A38", "A39", "A40"]

    def test_space_in_range(self):
        # "A12- A13" is the same reference; the stray space must not split it.
        refs = extract_cross_refs("(문단 A12- A13 참조)")
        assert expand_cross_refs(refs) == ["A12", "A13"]

    def test_spaces_around_range_dash(self):
        # "A12 - A13" with spaces on both sides of the hyphen.
        refs = extract_cross_refs("(문단 A12 - A13 참조)")
        assert expand_cross_refs(refs) == ["A12", "A13"]

    def test_uija_particle(self):
        # "49의 (a)-(c)" — Korean possessive between id and paren sub-item.
        refs = extract_cross_refs("(문단 49의 (a)-(c) 참조)")
        assert expand_cross_refs(refs) == ["49(a)", "49(b)", "49(c)"]

    def test_a_prefix_space(self):
        # "A 30" — stray space inside the "A" prefix.
        refs = extract_cross_refs("(문단 A 30 참조)")
        assert expand_cross_refs(refs) == ["A30"]

    def test_compound_list_after_single_문단(self):
        # Only one "문단" keyword but several comma-separated targets.
        refs = extract_cross_refs("(문단 A11-A14, A20 참조)")
        assert expand_cross_refs(refs) == ["A11", "A12", "A13", "A14", "A20"]

    def test_compound_with_wa(self):
        # Korean conjunction 와 inside a single "문단" span is absorbed.
        refs = extract_cross_refs("문단 A22와 A28 참조")
        assert expand_cross_refs(refs) == ["A22", "A28"]

    def test_dash_in_prose_left_alone(self):
        # A word-break hyphen in prose (Korean glyphs on both sides) does not
        # match the reference-dash normalizer, so no false positive.
        refs = extract_cross_refs("자세한 논의는-또는-별도의 지침을 참조하라")
        assert refs == []


# ── Standard header ────────────────────────────────────────────────────────
class TestMatchStandardHeader:
    def test_typical(self):
        result = match_standard_header(
            "감사기준서 200  독립된 감사인의 전반적인 목적 및 감사기준에 따른 감사의 수행"
        )
        assert result is not None
        no, title = result
        assert no == "200"
        assert title.startswith("독립된 감사인의")

    def test_with_ho(self):
        # "감사기준서 200호 ..."  (alternative form in some sources)
        result = match_standard_header("감사기준서 200호  부정에 관한 감사인의 책임")
        assert result is not None
        assert result[0] == "200"

    def test_non_match(self):
        assert match_standard_header("그냥 본문입니다.") is None


# ── Appendix title ─────────────────────────────────────────────────────────
class TestMatchAppendixTitle:
    def test_numbered(self):
        result = match_appendix_title("보론 1 (문단 A24-A26 참조) 감사계약서의 예시")
        assert result is not None
        assert result[0] == "1"
        assert "감사계약서" in result[1]

    def test_unnumbered(self):
        result = match_appendix_title("보론(문단 3 참조) 기타 설명")
        assert result is not None
        assert result[0] is None

    def test_non_match(self):
        assert match_appendix_title("일반 문단") is None


# ── TOC line ───────────────────────────────────────────────────────────────
class TestMatchTocLine:
    def test_tab(self):
        result = match_toc_line("이 감사기준서의 범위\t\t1-2")
        assert result is not None
        assert result[0] == "이 감사기준서의 범위"
        assert result[1] == "1-2"

    def test_double_space(self):
        result = match_toc_line("시행일   10")
        assert result is not None
        assert result[1] == "10"

    def test_non_match_single_space(self):
        assert match_toc_line("시행일 10") is None


# ── Definition split ───────────────────────────────────────────────────────
class TestSplitDefinition:
    def test_em_dash(self):
        result = split_definition("감사위험 — 왜곡된 의견을 낼 위험")
        assert result == ("감사위험", "왜곡된 의견을 낼 위험")

    def test_en_dash(self):
        result = split_definition("감사증거 – 결론의 근거가 되는 정보")
        assert result is not None
        assert result[0] == "감사증거"

    def test_ascii_hyphen(self):
        result = split_definition("감사 - 검토")
        assert result == ("감사", "검토")

    def test_long_term_rejected(self):
        # A real A2 term is 4–15 chars; anything above ~20 is prose that
        # happens to contain an em-dash and must not be parsed as a definition.
        text = "매우 긴 산문 문장이 이어지다가 계속 이어지다가 한참 후에 — 그리고 뒤에 또 문장이"
        assert split_definition(text) is None

    def test_no_dash(self):
        assert split_definition("정의 없는 단락.") is None


# ── NumberingCounter ───────────────────────────────────────────────────────
def _spec_with_abstract(abs_id: str, levels: list[NumLevel]) -> NumberingSpec:
    return NumberingSpec(
        num_to_abs={"1": abs_id},
        abstracts={abs_id: AbstractNum(abs_id=abs_id, levels=tuple(levels))},
        style_defaults={},
    )


class TestNumberingCounter:
    def test_decimal_sequence(self):
        spec = _spec_with_abstract(
            "A",
            [
                NumLevel(0, "decimal", "%1.", 1),
            ],
        )
        c = NumberingCounter(spec)
        assert c.advance("1", 0) == "1."
        assert c.advance("1", 0) == "2."
        assert c.advance("1", 0) == "3."

    def test_application_prefix(self):
        spec = _spec_with_abstract(
            "A",
            [
                NumLevel(0, "decimal", "A%1.", 1),
            ],
        )
        c = NumberingCounter(spec)
        assert c.advance("1", 0) == "A1."
        assert c.advance("1", 0) == "A2."

    def test_nested_levels_reset(self):
        spec = _spec_with_abstract(
            "A",
            [
                NumLevel(0, "decimal", "%1.", 1),
                NumLevel(1, "lowerLetter", "(%2)", 1),
                NumLevel(2, "lowerRoman", "(%3)", 1),
            ],
        )
        c = NumberingCounter(spec)
        assert c.advance("1", 0) == "1."
        assert c.advance("1", 1) == "(a)"
        assert c.advance("1", 1) == "(b)"
        assert c.advance("1", 2) == "(i)"
        # advancing level 0 again resets deeper counters
        assert c.advance("1", 0) == "2."
        assert c.advance("1", 1) == "(a)"

    def test_shared_abstract_across_numids(self):
        # Two numIds pointing at the same abstract share a counter.
        spec = NumberingSpec(
            num_to_abs={"5": "A", "9": "A"},
            abstracts={
                "A": AbstractNum(
                    abs_id="A",
                    levels=(NumLevel(0, "decimal", "A%1.", 1),),
                )
            },
            style_defaults={},
        )
        c = NumberingCounter(spec)
        assert c.advance("5", 0) == "A1."
        assert c.advance("9", 0) == "A2."  # same abstract counter

    def test_bullet_returns_empty(self):
        spec = _spec_with_abstract(
            "A",
            [
                NumLevel(0, "bullet", "\uf097", 1),
            ],
        )
        c = NumberingCounter(spec)
        assert c.advance("1", 0) == ""

    def test_unknown_numid(self):
        spec = _spec_with_abstract("A", [NumLevel(0, "decimal", "%1.", 1)])
        c = NumberingCounter(spec)
        assert c.advance("999", 0) == ""

    def test_reset_all(self):
        spec = _spec_with_abstract("A", [NumLevel(0, "decimal", "%1.", 1)])
        c = NumberingCounter(spec)
        c.advance("1", 0)
        c.advance("1", 0)
        c.reset_all()
        assert c.advance("1", 0) == "1."
