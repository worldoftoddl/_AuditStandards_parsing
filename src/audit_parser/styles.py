"""Single source of truth for style → semantic mapping.

Derived from ``docs/style_map.md`` (Phase 1.5). If that document changes,
update this module in the same commit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from .ir import Kind, Section

# ── numId families (from word/styles.xml inspection) ────────────────────────
NUMID_APPLICATION: Final[str] = "105"  # root: style A ("문단A")
NUMID_REQUIREMENT: Final[str] = "119"  # root: style a1 ("문단")

TOC_HEADER_TEXTS: Final[frozenset[str]] = frozenset(["목 차", "목차", "문단번호", "페이지"])

# Plain-text document-title candidates seen in PRE_TOC state.
DOCUMENT_TITLE_HINTS: Final[tuple[str, ...]] = (
    "회계감사기준 전문",
    "회계감사기준",
)


@dataclass(frozen=True)
class StyleInfo:
    kind: Kind
    level: int | None
    default_section: Section | None
    # Tri-state: True / False explicit, None means "inherit from ancestor/context".
    is_application: bool | None


# ── style_id → StyleInfo ────────────────────────────────────────────────────
# Mirrors docs/style_map.md §"최종 매핑 테이블".
STYLE_MAP: Final[dict[str, StyleInfo]] = {
    # Headings (outlineLvl = level-1).
    "10": StyleInfo("heading_standard", 1, None, None),
    "2": StyleInfo("heading_section", 2, None, None),
    "3": StyleInfo("heading_subsection", 3, None, None),
    "4": StyleInfo("heading_subsubsection", 4, None, None),
    "5": StyleInfo("heading_level5", 5, None, None),
    "6": StyleInfo("heading_level6", 6, None, None),
    "aff3": StyleInfo("heading_appendix", 3, "appendix", None),
    # Body paragraphs.
    "a1": StyleInfo("paragraph_body", None, None, False),
    "A": StyleInfo("paragraph_body", None, "application", True),
    # List items — family inferred from numId / basedOn chain.
    "A0": StyleInfo("paragraph_list_item", None, "application", True),
    "A2": StyleInfo("paragraph_list_item", None, None, False),
    "B": StyleInfo("paragraph_list_item", None, "application", True),
    "B0": StyleInfo("paragraph_list_item", None, None, False),
    "C": StyleInfo("paragraph_list_item", None, None, None),
    "a9": StyleInfo("paragraph_list_item", None, None, None),
    # TOC entries.
    "ad": StyleInfo("toc_entry", None, None, None),
}

# Styles that belong to the heading family — used by heading-stack logic.
HEADING_STYLES: Final[frozenset[str]] = frozenset(
    sid for sid, info in STYLE_MAP.items() if info.kind.startswith("heading_")
)

# heading styleId → level reverse lookup (for outlineLvl cross-check).
HEADING_LEVELS: Final[dict[str, int]] = {
    sid: info.level  # type: ignore[misc]
    for sid, info in STYLE_MAP.items()
    if info.kind.startswith("heading_") and info.level is not None
}


# ── 2-style section text → Section ──────────────────────────────────────────
SECTION_TEXT_MAP: Final[dict[str, Section]] = {
    "서론": "intro",
    "감사인의 전반적인 목적": "objective",
    "목적": "objective",
    "용어의 정의": "definitions",
    "요구사항": "requirements",
    "적용 및 기타 설명자료": "application",
}


def classify_section(heading_text: str) -> Section:
    """Map a `2`-style heading text to a Section tag."""
    key = heading_text.strip()
    return SECTION_TEXT_MAP.get(key, "other")


def infer_kind(style_id: str, outline_lvl: int | None) -> tuple[Kind, int | None]:
    """Return (kind, level) for a style, cross-checking outlineLvl.

    outlineLvl is treated as a secondary signal: if STYLE_MAP is unambiguous,
    use it; otherwise fall back to outlineLvl+1 as the level.
    """
    if style_id in STYLE_MAP:
        info = STYLE_MAP[style_id]
        return info.kind, info.level
    if outline_lvl is not None and 0 <= outline_lvl <= 8:
        # Unknown style but Word flagged it as a heading.
        level = outline_lvl + 1
        kind: Kind
        if level == 1:
            kind = "heading_standard"
        elif level == 2:
            kind = "heading_section"
        elif level == 3:
            kind = "heading_subsection"
        elif level == 4:
            kind = "heading_subsubsection"
        elif level == 5:
            kind = "heading_level5"
        elif level == 6:
            kind = "heading_level6"
        else:
            kind = "unknown"
        return kind, level
    return "unknown", None
