"""State machine + heading stack: ``RawBlock[]`` → ``Document``.

States: PRE_TOC → TOC → STANDARD_BODY ⇄ APPENDIX.

The first ``heading_standard`` (style ``10``) transitions out of ``PRE_TOC``
into ``STANDARD_BODY``. Inside a standard, ``heading_appendix`` (style
``aff3``) toggles the ``APPENDIX`` flag, which is cleared by the next
``heading_standard``. TOC headers that appear inside a standard remain flagged
as TOC (local tables of contents within a standard).
"""

from __future__ import annotations

from pathlib import Path

from .ir import Block, Document, Kind, NumberingSpec, RawBlock, Section, Standard, State
from .numbering import (
    NumberingCounter,
    extract_cross_refs,
    extract_paragraph_id,
    match_standard_header,
    split_definition,
)
from .styles import (
    DOCUMENT_TITLE_HINTS,
    HEADING_LEVELS,
    NUMID_APPLICATION,
    NUMID_REQUIREMENT,
    STYLE_MAP,
    TOC_HEADER_TEXTS,
    classify_section,
    infer_kind,
)


def _resolve_numbered_family(raw: RawBlock, style_info_application: bool | None) -> bool | None:
    """For list styles whose ``is_application`` is context-dependent, look at
    the actual ``numId`` to decide. Returns tri-state."""
    if style_info_application is not None:
        return style_info_application
    if raw.num_pr is None or raw.num_pr.num_id is None:
        return None
    if raw.num_pr.num_id == NUMID_APPLICATION:
        return True
    if raw.num_pr.num_id == NUMID_REQUIREMENT:
        return False
    return None


def _is_toc_like_no_style(text: str) -> bool:
    return text.strip() in TOC_HEADER_TEXTS


def _looks_like_document_title(text: str) -> bool:
    return any(hint in text for hint in DOCUMENT_TITLE_HINTS)


class _HeadingStack:
    """Level-based push/pop stack of heading texts."""

    def __init__(self) -> None:
        self._items: list[tuple[int, str]] = []

    def push(self, level: int, text: str) -> None:
        while self._items and self._items[-1][0] >= level:
            self._items.pop()
        self._items.append((level, text))

    def clear(self) -> None:
        self._items.clear()

    def trail(self) -> tuple[str, ...]:
        return tuple(t for _, t in self._items)

    def section(self) -> Section | None:
        """Return the most recent `heading_section` (level-2) text mapped."""
        for lvl, text in self._items:
            if lvl == 2:
                return classify_section(text)
        return None


def build_document(
    source_path: Path,
    raw_blocks: list[RawBlock],
    footnotes: dict[str, str],
    numbering: NumberingSpec,
) -> Document:
    """Walk raw blocks, apply the state machine, return a classified Document."""
    stack = _HeadingStack()
    state: State = "PRE_TOC"
    in_appendix = False
    counter = NumberingCounter(numbering)

    doc = Document(source_path=source_path, footnotes=footnotes)
    current_std: Standard | None = None
    source_stem = source_path.stem
    # Tracks the most-recent numbered body-ish block in the current section,
    # used to link continuation blocks. Keyed by (isa_ordinal, section).
    last_numbered_block_id: str | None = None
    last_numbered_section: str | None = None
    last_numbered_isa_ordinal: int = -1

    for raw in raw_blocks:
        info = STYLE_MAP.get(raw.style_id)
        kind: Kind
        level: int | None

        if raw.is_table:
            kind, level = "table", None
        elif info is not None:
            kind, level = info.kind, info.level
        else:
            kind, level = infer_kind(raw.style_id, raw.outline_lvl)

        # Cross-check: if known heading style disagrees with outlineLvl, trust
        # the style (styles.xml is authoritative), but tag the mismatch via
        # the level we emit. HEADING_LEVELS already encodes the styles.xml
        # ground truth.
        if raw.style_id in HEADING_LEVELS:
            level = HEADING_LEVELS[raw.style_id]

        # Demote unmapped `2`-style headings ("일반원칙과 책임" etc.) to L3 so
        # the heading stack keeps the real section boundary (요구사항 / 적용 …)
        # visible above them.
        if kind == "heading_section" and classify_section(raw.text) == "other":
            kind = "heading_subsection"
            level = 3

        # ── State transitions ──
        if kind == "heading_standard":
            stack.clear()
            in_appendix = False
            state = "STANDARD_BODY"
            counter.reset_all()  # each ISA restarts all automatic numbering
            parsed = match_standard_header(raw.text)
            if parsed is not None:
                std_no, std_title = parsed
            else:
                std_no, std_title = "?", raw.text
            current_std = Standard(number=std_no, title=std_title)
            doc.standards.append(current_std)
            stack.push(level or 1, raw.text)
        elif kind == "heading_appendix":
            in_appendix = True
            stack.push(level or 3, raw.text)
        elif kind.startswith("heading_") and level is not None:
            stack.push(level, raw.text)
        elif state == "PRE_TOC" and _is_toc_like_no_style(raw.text):
            state = "TOC"

        # ── is_toc determination ──
        is_toc = kind == "toc_entry" or (
            state == "TOC" and raw.style_id == "" and _is_toc_like_no_style(raw.text)
        )

        # ── section & is_application_guidance ──
        section: Section | None
        if in_appendix and kind != "heading_standard":
            section = "appendix"
        elif info is not None and info.default_section is not None:
            section = info.default_section
        else:
            section = stack.section()

        style_app = info.is_application if info is not None else None
        is_app = _resolve_numbered_family(raw, style_app) or False
        # A / A0 always set application, regardless of stack.
        if is_app and section != "appendix":
            section = "application"

        # ── Paragraph id extraction (only for body-ish kinds) ──
        text = raw.text
        paragraph_id: str | None = None
        if (
            kind
            in (
                "paragraph_body",
                "paragraph_list_item",
                "paragraph_definition",
            )
            and not is_toc
        ):
            # Primary path: DOCX automatic numbering via numPr (with style
            # inheritance fallback for paragraphs that don't override numPr).
            effective_num_pr = raw.num_pr
            if (
                effective_num_pr is None or effective_num_pr.num_id is None
            ) and raw.style_id in numbering.style_defaults:
                effective_num_pr = numbering.style_defaults[raw.style_id]
            if effective_num_pr is not None and effective_num_pr.num_id is not None:
                try:
                    ilvl = int(effective_num_pr.ilvl) if effective_num_pr.ilvl is not None else 0
                except ValueError:
                    ilvl = 0
                rendered = counter.advance(effective_num_pr.num_id, ilvl)
                if rendered:
                    paragraph_id = rendered.rstrip(".")
            # Fallback: inline numeric prefix in text (other DOCX sources may
            # hardcode the number instead of using numPr).
            if paragraph_id is None:
                inline_id, stripped, style_is_app = extract_paragraph_id(
                    raw.text, style_id=raw.style_id
                )
                if inline_id is not None:
                    paragraph_id = inline_id
                    text = stripped
                    is_app = is_app or style_is_app

        # ── Definition split (style A2 only) — promote kind ──
        if (
            kind == "paragraph_list_item"
            and raw.style_id == "A2"
            and split_definition(text) is not None
        ):
            kind = "paragraph_definition"

        # ── NO_STYLE handling in PRE_TOC: promote to document title ──
        if state == "PRE_TOC" and raw.style_id == "" and _looks_like_document_title(raw.text):
            kind = "heading_document"
            level = 0

        # ── Cross-refs ──
        refs = extract_cross_refs(text)

        # ── Continuation linking ──
        current_isa_ordinal = len(doc.standards) - 1  # resets on each new ISA
        continuation_of: str | None = None
        is_bodyish = kind in (
            "paragraph_body",
            "paragraph_list_item",
            "paragraph_definition",
        )
        if (
            is_bodyish
            and not is_toc
            and paragraph_id is None
            and last_numbered_block_id is not None
            and last_numbered_isa_ordinal == current_isa_ordinal
            and last_numbered_section == section
        ):
            continuation_of = last_numbered_block_id

        block = Block(
            block_id=f"{source_stem}#{raw.ordinal:05d}",
            source_path=source_path,
            ordinal=raw.ordinal,
            style_id=raw.style_id,
            text=text,
            raw_text=raw.raw_text,
            num_pr=raw.num_pr,
            kind=kind,
            level=level,
            heading_trail=stack.trail(),
            section=section,
            paragraph_id=paragraph_id,
            is_application_guidance=is_app,
            is_toc=is_toc,
            refs=refs,
            footnote_ids=list(raw.footnote_ids),
            table_rows=list(raw.table_rows),
            continuation_of=continuation_of,
        )

        if current_std is None:
            doc.preamble.append(block)
        else:
            current_std.blocks.append(block)

        # Update continuation anchor after the block is saved.
        if is_bodyish and not is_toc and paragraph_id is not None:
            last_numbered_block_id = block.block_id
            last_numbered_section = section
            last_numbered_isa_ordinal = current_isa_ordinal
        elif kind.startswith("heading_"):
            # Headings break continuation — next block starts fresh.
            last_numbered_block_id = None

    return doc
