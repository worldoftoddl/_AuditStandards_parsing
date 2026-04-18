"""Document → per-ISA Markdown files.

Each ISA (감사기준서) becomes ``ISA-<NO>.md`` under the output directory.
Preamble blocks (document title, pre-TOC text) go into ``preamble.md``.

Conventions:
- ``heading_standard`` → ``#`` (title only)
- ``heading_section`` → ``##``
- ``heading_subsection`` / ``heading_appendix`` → ``###``
- ``heading_subsubsection`` → ``####``
- deeper heading levels → ``#####``, ``######``
- body paragraphs: ``**<paragraph_id>.** <text>`` (id omitted if None)
- list items: indented ``- `` with id inline
- tables: rendered as GFM pipe tables
- footnotes referenced in body as ``[^<id>]`` appear at the end of the file
"""

from __future__ import annotations

from pathlib import Path

from .ir import Block, Document, Standard

_HEADING_MD = {
    "heading_document": "#",
    "heading_standard": "#",
    "heading_section": "##",
    "heading_subsection": "###",
    "heading_appendix": "###",
    "heading_subsubsection": "####",
    "heading_level5": "#####",
    "heading_level6": "######",
}


def _render_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    ncols = max(len(r) for r in rows)
    padded = [list(r) + [""] * (ncols - len(r)) for r in rows]
    widths = [max(len(r[i]) for r in padded) for i in range(ncols)]
    lines: list[str] = []
    lines.append("| " + " | ".join(padded[0][i].ljust(widths[i]) for i in range(ncols)) + " |")
    lines.append("|" + "|".join("-" * (w + 2) for w in widths) + "|")
    for r in padded[1:]:
        lines.append("| " + " | ".join(r[i].ljust(widths[i]) for i in range(ncols)) + " |")
    return "\n".join(lines)


def _render_block(b: Block, *, footnote_refs: set[str]) -> str | None:
    if b.is_toc:
        return None
    if b.kind == "table":
        return _render_table(b.table_rows)
    if b.kind in _HEADING_MD:
        prefix = _HEADING_MD[b.kind]
        return f"{prefix} {b.text}"

    # body / list / definition
    fn_suffix = ""
    if b.footnote_ids:
        for fid in b.footnote_ids:
            footnote_refs.add(fid)
        fn_suffix = "".join(f"[^{fid}]" for fid in b.footnote_ids)

    id_prefix = ""
    if b.paragraph_id:
        if b.paragraph_id.startswith("("):
            id_prefix = f"{b.paragraph_id} "
        else:
            id_prefix = f"**{b.paragraph_id}.** "

    if b.kind == "paragraph_list_item":
        return f"- {id_prefix}{b.text}{fn_suffix}"
    return f"{id_prefix}{b.text}{fn_suffix}"


def _render_blocks(blocks: list[Block], footnotes: dict[str, str]) -> str:
    referenced: set[str] = set()
    lines: list[str] = []
    for b in blocks:
        rendered = _render_block(b, footnote_refs=referenced)
        if rendered is None:
            continue
        lines.append(rendered)
        lines.append("")  # blank line between blocks

    if referenced:
        lines.append("")
        lines.append("---")
        lines.append("")
        for fid in sorted(referenced, key=lambda s: (len(s), s)):
            text = footnotes.get(fid, "")
            if text:
                lines.append(f"[^{fid}]: {text}")
    return "\n".join(lines).rstrip() + "\n"


def _standard_filename(std: Standard) -> str:
    safe_no = std.number.replace("/", "_") or "unknown"
    return f"ISA-{safe_no}.md"


def render_document(doc: Document, out_dir: Path) -> list[Path]:
    """Emit per-ISA Markdown files. Returns list of written paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    if doc.preamble:
        preamble_path = out_dir / "preamble.md"
        preamble_path.write_text(_render_blocks(doc.preamble, doc.footnotes), encoding="utf-8")
        written.append(preamble_path)

    for std in doc.standards:
        path = out_dir / _standard_filename(std)
        path.write_text(_render_blocks(std.blocks, doc.footnotes), encoding="utf-8")
        written.append(path)

    return written
