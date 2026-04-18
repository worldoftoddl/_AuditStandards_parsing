"""DOCX → ``RawBlock[]`` using lxml directly (no python-docx abstraction).

We read ``word/document.xml`` and ``word/footnotes.xml`` in-place. This keeps
namespace handling explicit and lets us preserve paragraph order across
both paragraphs (``w:p``) and tables (``w:tbl``) at the body level.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Final

from lxml import etree

from .ir import NumberingSpec, NumPr, RawBlock
from .numbering import parse_numbering_xml

WNS: Final[str] = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS: Final[dict[str, str]] = {"w": WNS}


def _w(tag: str) -> str:
    return f"{{{WNS}}}{tag}"


def _style_id(p: etree._Element) -> str:
    ppr = p.find(_w("pPr"))
    if ppr is None:
        return ""
    ps = ppr.find(_w("pStyle"))
    if ps is None:
        return ""
    return ps.get(_w("val"), "")


def _outline_lvl(p: etree._Element) -> int | None:
    ppr = p.find(_w("pPr"))
    if ppr is None:
        return None
    ol = ppr.find(_w("outlineLvl"))
    if ol is None:
        return None
    v = ol.get(_w("val"))
    if v is None:
        return None
    try:
        return int(v)
    except ValueError:
        return None


def _num_pr(p: etree._Element) -> NumPr | None:
    ppr = p.find(_w("pPr"))
    if ppr is None:
        return None
    npr = ppr.find(_w("numPr"))
    if npr is None:
        return None
    nid = npr.find(_w("numId"))
    il = npr.find(_w("ilvl"))
    num_id = nid.get(_w("val")) if nid is not None else None
    ilvl = il.get(_w("val")) if il is not None else None
    if num_id is None and ilvl is None:
        return None
    return NumPr(num_id=num_id, ilvl=ilvl)


def _paragraph_text(p: etree._Element) -> tuple[str, list[str]]:
    """Return ``(text, footnote_ids)``. Line breaks become a single space."""
    fn_ids: list[str] = []
    parts: list[str] = []
    for node in p.iter():
        tag = etree.QName(node.tag).localname
        if tag == "t" and node.text:
            parts.append(node.text)
        elif tag == "tab":
            parts.append("\t")
        elif tag == "br":
            parts.append(" ")
        elif tag == "footnoteReference":
            fid = node.get(_w("id"))
            if fid is not None:
                fn_ids.append(fid)
    return "".join(parts), fn_ids


def _table_rows(tbl: etree._Element) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in tbl.findall(_w("tr")):
        cells: list[str] = []
        for tc in tr.findall(_w("tc")):
            cell_parts: list[str] = []
            for p in tc.findall(_w("p")):
                text, _ = _paragraph_text(p)
                cell_parts.append(text.strip())
            cells.append(" ".join(s for s in cell_parts if s))
        rows.append(cells)
    return rows


def _read_footnotes(z: zipfile.ZipFile) -> dict[str, str]:
    try:
        with z.open("word/footnotes.xml") as f:
            tree = etree.parse(f)
    except KeyError:
        return {}
    out: dict[str, str] = {}
    for fn in tree.getroot().findall(_w("footnote")):
        fid = fn.get(_w("id"))
        if fid is None:
            continue
        parts: list[str] = []
        for p in fn.findall(_w("p")):
            text, _ = _paragraph_text(p)
            if text.strip():
                parts.append(text.strip())
        if parts:
            out[fid] = "\n".join(parts)
    return out


def read_docx(
    path: Path,
) -> tuple[list[RawBlock], dict[str, str], NumberingSpec]:
    """Parse a DOCX file into ``(raw_blocks, footnotes, numbering_spec)``.

    ``raw_blocks`` preserves body order across ``w:p`` and ``w:tbl``. Empty
    paragraphs (no text runs and no table) are dropped to match the Phase 1
    profile counts. Footnotes are returned as ``{id: text}`` for the caller
    to keep alongside the Document. ``numbering_spec`` lets callers render
    automatic numbering via :class:`audit_parser.numbering.NumberingCounter`.
    """
    numbering = parse_numbering_xml(path)
    with zipfile.ZipFile(path) as z:
        with z.open("word/document.xml") as f:
            tree = etree.parse(f)
        footnotes = _read_footnotes(z)

    body = tree.getroot().find(_w("body"))
    if body is None:
        return [], footnotes, numbering

    blocks: list[RawBlock] = []
    ordinal = 0
    for child in body:
        tag = etree.QName(child.tag).localname
        if tag == "p":
            raw_text, fn_ids = _paragraph_text(child)
            text = raw_text.strip()
            if not text:
                continue
            blocks.append(
                RawBlock(
                    ordinal=ordinal,
                    style_id=_style_id(child),
                    outline_lvl=_outline_lvl(child),
                    num_pr=_num_pr(child),
                    text=text,
                    raw_text=raw_text,
                    is_table=False,
                    footnote_ids=fn_ids,
                )
            )
            ordinal += 1
        elif tag == "tbl":
            rows = _table_rows(child)
            if not any(any(c for c in row) for row in rows):
                continue
            # Flatten for a searchable text representation; markdown.py will
            # render the structured rows. Empty-cell joins remove duplicate
            # whitespace seams.
            flat = " | ".join(" | ".join(c for c in row if c) for row in rows if any(row))
            blocks.append(
                RawBlock(
                    ordinal=ordinal,
                    style_id="",
                    outline_lvl=None,
                    num_pr=None,
                    text=flat,
                    raw_text=flat,
                    is_table=True,
                    table_rows=rows,
                )
            )
            ordinal += 1
        # sectPr and other body-level elements are ignored.

    return blocks, footnotes, numbering
