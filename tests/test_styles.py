"""Tests for style → semantic mapping."""

from audit_parser.styles import (
    HEADING_LEVELS,
    STYLE_MAP,
    classify_section,
    infer_kind,
)


class TestStyleMap:
    def test_heading_styles_have_levels(self):
        for sid in ("10", "2", "3", "4", "5", "6"):
            assert STYLE_MAP[sid].kind.startswith("heading_")
            assert STYLE_MAP[sid].level == int(sid) if sid != "10" else 1

    def test_a1_is_requirement(self):
        info = STYLE_MAP["a1"]
        assert info.kind == "paragraph_body"
        assert info.is_application is False

    def test_A_is_application(self):
        info = STYLE_MAP["A"]
        assert info.kind == "paragraph_body"
        assert info.is_application is True
        assert info.default_section == "application"

    def test_A0_inherits_application(self):
        info = STYLE_MAP["A0"]
        assert info.is_application is True
        assert info.kind == "paragraph_list_item"

    def test_appendix_style(self):
        info = STYLE_MAP["aff3"]
        assert info.kind == "heading_appendix"
        assert info.level == 3
        assert info.default_section == "appendix"

    def test_toc_style(self):
        assert STYLE_MAP["ad"].kind == "toc_entry"

    def test_heading_levels_match_styleids(self):
        assert HEADING_LEVELS["10"] == 1
        assert HEADING_LEVELS["2"] == 2
        assert HEADING_LEVELS["aff3"] == 3


class TestClassifySection:
    def test_known(self):
        assert classify_section("서론") == "intro"
        assert classify_section("요구사항") == "requirements"
        assert classify_section("적용 및 기타 설명자료") == "application"
        assert classify_section("용어의 정의") == "definitions"

    def test_target_trimmed(self):
        assert classify_section("  서론  ") == "intro"

    def test_unknown_falls_back(self):
        assert classify_section("공공부문 특유의 고려사항") == "other"


class TestInferKind:
    def test_known_style_wins(self):
        # outlineLvl disagreement is ignored — STYLE_MAP is authoritative.
        kind, level = infer_kind("10", outline_lvl=5)
        assert kind == "heading_standard"
        assert level == 1

    def test_unknown_style_uses_outline(self):
        kind, level = infer_kind("xyz", outline_lvl=0)
        assert kind == "heading_standard"
        assert level == 1

    def test_unknown_and_no_outline(self):
        kind, level = infer_kind("xyz", outline_lvl=None)
        assert kind == "unknown"
        assert level is None
