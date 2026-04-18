"""Intermediate representation for parsed KICPA audit standards.

Two layers:
- `RawBlock`: what the DOCX reader emits (pre-classification).
- `Block`: after classifier + state machine; ready for markdown/chunking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Kind = Literal[
    "heading_document",
    "heading_standard",
    "heading_section",
    "heading_subsection",
    "heading_subsubsection",
    "heading_level5",
    "heading_level6",
    "heading_appendix",
    "paragraph_body",
    "paragraph_list_item",
    "paragraph_definition",
    "table",
    "toc_entry",
    "unknown",
]

Section = Literal[
    "intro",
    "objective",
    "definitions",
    "requirements",
    "application",
    "appendix",
    "other",
]

State = Literal["PRE_TOC", "TOC", "STANDARD_BODY", "APPENDIX"]


@dataclass(frozen=True)
class NumPr:
    num_id: str | None
    ilvl: str | None


@dataclass(frozen=True)
class NumLevel:
    """One lvl element from an abstractNum in word/numbering.xml."""

    ilvl: int
    num_fmt: str  # "decimal" | "bullet" | "lowerLetter" | "lowerRoman" | …
    lvl_text: str  # e.g. "%1.", "A%1.", "(%2)", bullet codepoint
    start: int


@dataclass(frozen=True)
class AbstractNum:
    abs_id: str
    levels: tuple[NumLevel, ...]  # indexed by ilvl, 0..8

    def level(self, ilvl: int) -> NumLevel | None:
        for lv in self.levels:
            if lv.ilvl == ilvl:
                return lv
        return None


@dataclass(frozen=True)
class NumberingSpec:
    """Parsed word/numbering.xml: numId → abstractNumId → levels.

    ``style_defaults`` captures the ``numPr`` declared inside each style in
    ``word/styles.xml`` so the walker can fall back when a paragraph doesn't
    override numbering explicitly.
    """

    num_to_abs: dict[str, str]
    abstracts: dict[str, AbstractNum]
    style_defaults: dict[str, NumPr]

    def level_for(self, num_id: str, ilvl: int) -> NumLevel | None:
        abs_id = self.num_to_abs.get(num_id)
        if abs_id is None:
            return None
        ab = self.abstracts.get(abs_id)
        if ab is None:
            return None
        return ab.level(ilvl)


@dataclass
class RawBlock:
    """One DOCX paragraph (or a synthesized table block) before classification."""

    ordinal: int
    style_id: str  # "" means <NO_STYLE>
    outline_lvl: int | None  # from w:pPr/w:outlineLvl (0-based)
    num_pr: NumPr | None
    text: str  # stripped concatenation of w:t runs
    raw_text: str  # original concatenation, pre-strip
    is_table: bool = False
    table_rows: list[list[str]] = field(default_factory=list)  # rows → cells
    footnote_ids: list[str] = field(default_factory=list)  # referenced footnote ids


@dataclass
class Block:
    """Classified block, ready for markdown emission and chunking."""

    block_id: str  # f"{source_stem}#{ordinal:05d}"
    source_path: Path
    ordinal: int

    style_id: str
    text: str  # paragraph_id prefix stripped
    raw_text: str  # original
    num_pr: NumPr | None

    kind: Kind
    level: int | None

    heading_trail: tuple[str, ...]
    section: Section | None

    paragraph_id: str | None
    is_application_guidance: bool
    is_toc: bool

    refs: list[str] = field(default_factory=list)  # cross-reference targets
    footnote_ids: list[str] = field(default_factory=list)

    # only for kind == "table"
    table_rows: list[list[str]] = field(default_factory=list)

    # Continuation link: for body/list_item blocks without an own paragraph_id
    # that semantically extend the most-recent numbered body block in the same
    # section. The chunker uses this to merge continuations into the parent.
    continuation_of: str | None = None


@dataclass
class Chunk:
    """Retrieval-ready chunk. Produced by chunk.py from Block(s)."""

    chunk_id: str  # f"{isa_no}:{paragraph_id}" or hash-based for merges
    isa_no: str  # "200","210", …; "" for preamble
    isa_title: str
    section: str  # intro/objective/definitions/requirements/application/appendix/other
    heading_trail: list[str]
    paragraph_ids: list[str]  # possibly merged
    is_application_guidance: bool
    is_appendix: bool
    text: str  # final embed target — may include heading_trail prefix
    char_count: int
    source_path: str  # relative / str repr
    content_hash: str  # SHA-256 of `text`
    refs: list[str] = field(default_factory=list)  # expanded cross-ref ids


@dataclass
class Standard:
    """One ISA (감사기준서) — blocks scoped under a heading_standard."""

    number: str  # "200", "315", …
    title: str  # "독립된 감사인의 전반적인 목적 …"
    blocks: list[Block] = field(default_factory=list)


@dataclass
class Document:
    """Full parsed document."""

    source_path: Path
    preamble: list[Block] = field(default_factory=list)  # blocks before first ISA
    standards: list[Standard] = field(default_factory=list)
    footnotes: dict[str, str] = field(default_factory=dict)  # footnote_id → text

    def all_blocks(self) -> list[Block]:
        out: list[Block] = list(self.preamble)
        for s in self.standards:
            out.extend(s.blocks)
        return out
