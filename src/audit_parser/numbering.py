"""Paragraph-id extraction, cross-reference detection, dash normalization.

All regexes are compiled once at import time and constrained to match at the
start of a paragraph (paragraph_id) or anywhere (cross_ref).

Rationale for the shapes here is in ``docs/style_map.md`` §"paragraph_id 정규식".
"""

from __future__ import annotations

import re
import unicodedata
import zipfile
from pathlib import Path
from typing import Final

from lxml import etree

from .ir import AbstractNum, NumberingSpec, NumLevel, NumPr

_WNS: Final[str] = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _w(tag: str) -> str:
    return f"{{{_WNS}}}{tag}"


# ── Regex building blocks ───────────────────────────────────────────────────
# Paragraph-id grammar: digits, optional "-digits" range, optional alpha suffix,
# optional "(lowercase)" sub-item. e.g. "14", "14A", "1-2", "13(f)", "A24-A26".
_ID_BODY: Final[str] = r"\d+(?:-\d+)?(?:[A-Za-z])?(?:\([a-z]\))?"

REQ_ID: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<id>{_ID_BODY})(?:\.\s+|\s+)(?P<rest>.*)$",
    re.UNICODE | re.DOTALL,
)
APP_ID: Final[re.Pattern[str]] = re.compile(
    rf"^A(?P<id>{_ID_BODY})(?:\.\s+|\s+)(?P<rest>.*)$",
    re.UNICODE | re.DOTALL,
)
# Cross-references may span a range with matching/mixed prefixes: "문단 A24-A26"
# or "문단 12-14". Compound lists joined by commas, "、", or the Korean
# connectives 와/과/및 are absorbed into one target span so downstream expansion
# can split them: "문단 A11-A14, A20" → "A11-A14, A20".
# Range-end may also be a bare "(x)" sub-item used as shorthand: "12(a)-(c)".
_RANGE_END: Final[str] = rf"(?:A?{_ID_BODY}|\([a-z]\))"
_CONNECTOR: Final[str] = r"(?:\s*[,、]\s*|\s*(?:와|과|및)\s*)"
CROSS_REF: Final[re.Pattern[str]] = re.compile(
    rf"문단\s+(?P<target>"
    rf"A?{_ID_BODY}(?:-{_RANGE_END})?"
    rf"(?:{_CONNECTOR}A?{_ID_BODY}(?:-{_RANGE_END})?)*"
    rf")",
    re.UNICODE,
)

# Standard header: "감사기준서 200 독립된 감사인의 …"
STANDARD_HEADER: Final[re.Pattern[str]] = re.compile(
    r"^감사기준서\s+(?P<no>\d{3})(?:호)?\s+(?P<title>.+)$",
    re.UNICODE,
)

# Appendix title: "보론 1 (문단 A24-A26 참조) 감사계약서의 예시"
APPENDIX_TITLE: Final[re.Pattern[str]] = re.compile(
    r"^보론\s*(?P<n>\d+)?\s*\(문단\s+A?\d+(?:-A?\d+)?\s*참조\)\s*(?P<title>.+)$",
    re.UNICODE,
)

# TOC line: "title\t…\tpages" or "title   pages" (2+ spaces). Pages may be
# "12" or "12-15".
TOC_LINE: Final[re.Pattern[str]] = re.compile(
    r"^(?P<title>.+?)(?:\t+|\s{2,})(?P<pages>\d+(?:-\d+)?)\s*$",
    re.UNICODE,
)

# Dash variants U+2010..U+2015 plus the ASCII hyphen, surrounded by whitespace.
DASH_SPLIT: Final[re.Pattern[str]] = re.compile(
    r"\s[\u2010-\u2015\-]\s",
    re.UNICODE,
)


# ── Text normalization ──────────────────────────────────────────────────────
def normalize(text: str) -> str:
    """NFKC-normalize a paragraph before regex matching."""
    return unicodedata.normalize("NFKC", text)


# Dash variants U+2010..U+2015 appear in cross-reference ranges (typographic
# en/em/figure dashes, horizontal bar). NFKC does not collapse these to ASCII
# hyphen, so we do it explicitly before CROSS_REF matches.
_DASH_NORMALIZE: Final[re.Pattern[str]] = re.compile(r"[\u2010-\u2015]", re.UNICODE)
# Korean possessive particle between a numeric id and a paren sub-item:
# "49의 (a)" → "49(a)". Translators used both forms in the 2025 revision.
_UI_PARTICLE: Final[re.Pattern[str]] = re.compile(r"(\d)의\s+\(", re.UNICODE)
# Whitespace surrounding a hyphen between two reference atoms. Constrained by
# alphanumeric/paren lookbehind+lookahead to avoid touching unrelated prose.
_DASH_WS: Final[re.Pattern[str]] = re.compile(
    r"(?<=[A-Za-z0-9\)])\s*-\s*(?=[A-Za-z0-9\(])",
    re.UNICODE,
)
# Space inserted between the "A" prefix and its digits: "A 30" → "A30".
_A_SPACE: Final[re.Pattern[str]] = re.compile(r"\bA\s+(?=\d)", re.UNICODE)


def _normalize_ref_text(text: str) -> str:
    """Normalize cross-reference artifacts before :data:`CROSS_REF` matching.

    Applied independently from :func:`normalize` (which does NFKC only):

    - Replace Unicode dash variants (U+2010..U+2015) with ASCII hyphen.
    - Collapse ``N의 (x)`` into ``N(x)`` (Korean possessive particle).
    - Remove whitespace around hyphens that sit between reference atoms.
    - Remove whitespace between an uppercase ``A`` prefix and its digits.

    The lookbehind/lookahead constraints on ``_DASH_WS`` limit changes to
    contexts that look like reference ranges, so arbitrary dashes in body
    prose are not affected.
    """
    text = _DASH_NORMALIZE.sub("-", text)
    text = _UI_PARTICLE.sub(r"\1(", text)
    text = _DASH_WS.sub("-", text)
    text = _A_SPACE.sub("A", text)
    return text


# ── Paragraph-id extraction ─────────────────────────────────────────────────
def extract_paragraph_id(text: str, *, style_id: str) -> tuple[str | None, str, bool]:
    """Return ``(paragraph_id, remaining_text, is_application_guidance)``.

    The regex applied is determined by the style: ``A`` / ``A0`` use ``APP_ID``,
    everything else uses ``REQ_ID``. Failure to match returns the input text
    unchanged with ``paragraph_id=None``.

    ``is_application_guidance`` is returned independently from ``style_id``:
    callers should rely on the style's semantic mapping, but it is convenient
    to surface here so structure.py can double-check.
    """
    norm = normalize(text)
    prefer_app = style_id in {"A", "A0"}
    patterns = (APP_ID, REQ_ID) if prefer_app else (REQ_ID, APP_ID)
    for pat in patterns:
        m = pat.match(norm)
        if m:
            pid = m.group("id")
            if pat is APP_ID:
                pid = f"A{pid}"
                is_app = True
            else:
                is_app = False
            return pid, m.group("rest"), is_app
    return None, norm, prefer_app


def extract_cross_refs(text: str) -> list[str]:
    """Collect every ``문단 N`` reference target in the paragraph.

    The paragraph is NFKC-normalized and then passed through
    :func:`_normalize_ref_text` so dash variants, the ``의`` particle, and
    stray whitespace inside ranges do not cause misses.
    """
    return [m.group("target") for m in CROSS_REF.finditer(_normalize_ref_text(normalize(text)))]


# ── Compound reference expansion ────────────────────────────────────────────
# After ``extract_cross_refs`` collects raw targets, callers often need to
# (a) split compound forms like "A22와 A28" → ["A22", "A28"], and (b) expand
# numeric ranges like "A20-A22" → ["A20", "A21", "A22"].
# Ranges that mix alpha prefixes differently (e.g. "A22-B3" if it ever existed)
# are left as-is.
_COMPOUND_SPLIT: Final[re.Pattern[str]] = re.compile(r"\s*[,、와과및]\s*", re.UNICODE)
_REF_PARTS: Final[re.Pattern[str]] = re.compile(
    r"^(?P<prefix>A)?(?P<num>\d+)(?P<suffix>[A-Za-z])?"
    r"(?:\((?P<paren>[a-z])\))?$",
    re.UNICODE,
)
# Matches bare "(x)" used as range-end shorthand: "12(a)-(c)".
_PAREN_ONLY: Final[re.Pattern[str]] = re.compile(r"^\((?P<paren>[a-z])\)$", re.UNICODE)


def _expand_range(start: str, end: str) -> list[str]:
    """Expand ``start-end`` into the list of ids it covers. Returns
    ``[start, end]`` unchanged if the shape is not enumerable."""
    ms = _REF_PARTS.match(start)
    me = _REF_PARTS.match(end)
    # Shorthand: "12(a)-(c)" — end is bare "(x)", inherits prefix/num from start.
    if ms is not None and me is None:
        po = _PAREN_ONLY.match(end)
        if po is not None and ms.group("paren"):
            a, b = ms.group("paren"), po.group("paren")
            if a <= b:
                prefix = ms.group("prefix") or ""
                return [f"{prefix}{ms.group('num')}({chr(c)})" for c in range(ord(a), ord(b) + 1)]
    if ms is None or me is None:
        return [start, end]
    # Prefix-omitted end (e.g. "A38-40"): the translator dropped the "A"
    # because the range context makes it unambiguous. Inherit the start
    # prefix before comparing, so this expands as a same-prefix range.
    start_prefix = ms.group("prefix")
    end_prefix = me.group("prefix") or start_prefix
    # Mixed-prefix ranges (A22-B3 …) aren't expandable with decimal logic.
    if start_prefix != end_prefix:
        return [start, end]
    # If both sides have paren sub-items and their numeric parts match,
    # walk the paren letters: "12(a)-(c)" → 12(a), 12(b), 12(c).
    if ms.group("num") == me.group("num") and ms.group("paren") and me.group("paren"):
        prefix = start_prefix or ""
        a, b = ms.group("paren"), me.group("paren")
        if a <= b:
            return [f"{prefix}{ms.group('num')}({chr(c)})" for c in range(ord(a), ord(b) + 1)]
        return [start, end]
    # Otherwise expand the numeric parts.
    try:
        s, e = int(ms.group("num")), int(me.group("num"))
    except ValueError:
        return [start, end]
    if s > e:
        return [start, end]
    prefix = start_prefix or ""
    suffix = ms.group("suffix") or ""
    return [f"{prefix}{n}{suffix}" for n in range(s, e + 1)]


def expand_cross_refs(raw_refs: list[str]) -> list[str]:
    """Given the raw strings from :func:`extract_cross_refs`, split compounds
    and expand simple ranges. Duplicates are removed while preserving order.

    Examples:
        >>> expand_cross_refs(["A22", "A28"])
        ['A22', 'A28']
        >>> expand_cross_refs(["A20-A22"])
        ['A20', 'A21', 'A22']
        >>> expand_cross_refs(["12(a)-(c)"])
        ['12(a)', '12(b)', '12(c)']
    """
    out: list[str] = []
    seen: set[str] = set()
    for raw in raw_refs:
        for piece in _COMPOUND_SPLIT.split(raw):
            piece = piece.strip()
            if not piece:
                continue
            if "-" in piece:
                lo, sep, hi = piece.rpartition("-")
                expanded = _expand_range(lo, hi) if sep and lo and hi else [piece]
            else:
                expanded = [piece]
            for item in expanded:
                if item not in seen:
                    seen.add(item)
                    out.append(item)
    return out


def match_standard_header(text: str) -> tuple[str, str] | None:
    """Parse a `10`-style heading text into ``(isa_no, title)``."""
    m = STANDARD_HEADER.match(normalize(text))
    if not m:
        return None
    return m.group("no"), m.group("title").strip()


def match_appendix_title(text: str) -> tuple[str | None, str] | None:
    """Parse an `aff3` heading into ``(appendix_number, title)``."""
    m = APPENDIX_TITLE.match(normalize(text))
    if not m:
        return None
    return m.group("n"), m.group("title").strip()


def match_toc_line(text: str) -> tuple[str, str] | None:
    """Split a TOC entry into ``(title, pages)``; returns None for non-TOC."""
    m = TOC_LINE.match(normalize(text))
    if not m:
        return None
    return m.group("title").strip(), m.group("pages")


# ── Term – definition split (for style A2) ──────────────────────────────────
_MAX_TERM_LEN: Final[int] = 20  # empirically A2 terms are 4–15 chars; 20 gives headroom


def split_definition(text: str) -> tuple[str, str] | None:
    """Split "term – definition" into parts; return None if not a definition.

    Guards:
    - Require a dash flanked by whitespace (``DASH_SPLIT``).
    - Only the first dash splits — paragraphs often contain additional dashes.
    - If the term portion is too long, assume this is prose with an em-dash,
      not a definition. Fall back to None so the caller treats it as body.
    """
    norm = normalize(text)
    parts = DASH_SPLIT.split(norm, maxsplit=1)
    if len(parts) != 2:
        return None
    term, defn = parts[0].strip(), parts[1].strip()
    if not term or not defn:
        return None
    if len(term) > _MAX_TERM_LEN:
        return None
    return term, defn


# ── numbering.xml parsing ───────────────────────────────────────────────────
def _parse_style_defaults(z: zipfile.ZipFile) -> dict[str, NumPr]:
    """Return ``{style_id: NumPr}`` from ``word/styles.xml``.

    Only styles that declare a ``pPr/numPr`` with a ``numId`` are included,
    because that's what paragraphs inherit when they don't override numbering.
    """
    try:
        with z.open("word/styles.xml") as f:
            tree = etree.parse(f)
    except KeyError:
        return {}
    out: dict[str, NumPr] = {}
    for style in tree.getroot().findall(_w("style")):
        sid = style.get(_w("styleId"))
        ppr = style.find(_w("pPr"))
        if sid is None or ppr is None:
            continue
        npr = ppr.find(_w("numPr"))
        if npr is None:
            continue
        nid_el = npr.find(_w("numId"))
        il_el = npr.find(_w("ilvl"))
        num_id = nid_el.get(_w("val")) if nid_el is not None else None
        ilvl = il_el.get(_w("val")) if il_el is not None else None
        if num_id is None and ilvl is None:
            continue
        out[sid] = NumPr(num_id=num_id, ilvl=ilvl)
    return out


def parse_numbering_xml(docx_path: Path) -> NumberingSpec:
    """Load ``word/numbering.xml`` and ``word/styles.xml`` numPr defaults.

    Missing files yield an empty spec section for that aspect.
    """
    with zipfile.ZipFile(docx_path) as z:
        style_defaults = _parse_style_defaults(z)
        try:
            with z.open("word/numbering.xml") as f:
                tree = etree.parse(f)
        except KeyError:
            return NumberingSpec(num_to_abs={}, abstracts={}, style_defaults=style_defaults)

    root = tree.getroot()
    num_to_abs: dict[str, str] = {}
    for n in root.findall(_w("num")):
        nid = n.get(_w("numId"))
        abs_el = n.find(_w("abstractNumId"))
        if nid is None or abs_el is None:
            continue
        abs_id = abs_el.get(_w("val"))
        if abs_id is not None:
            num_to_abs[nid] = abs_id

    abstracts: dict[str, AbstractNum] = {}
    for a in root.findall(_w("abstractNum")):
        abs_id = a.get(_w("abstractNumId"))
        if abs_id is None:
            continue
        levels: list[NumLevel] = []
        for lvl in a.findall(_w("lvl")):
            try:
                ilvl = int(lvl.get(_w("ilvl"), "0"))
            except ValueError:
                continue
            fmt_el = lvl.find(_w("numFmt"))
            text_el = lvl.find(_w("lvlText"))
            start_el = lvl.find(_w("start"))
            num_fmt = fmt_el.get(_w("val"), "decimal") if fmt_el is not None else "decimal"
            lvl_text = text_el.get(_w("val"), "") if text_el is not None else ""
            try:
                start = int(start_el.get(_w("val"), "1")) if start_el is not None else 1
            except ValueError:
                start = 1
            levels.append(NumLevel(ilvl=ilvl, num_fmt=num_fmt, lvl_text=lvl_text, start=start))
        abstracts[abs_id] = AbstractNum(abs_id=abs_id, levels=tuple(levels))
    return NumberingSpec(num_to_abs=num_to_abs, abstracts=abstracts, style_defaults=style_defaults)


# ── Number rendering ────────────────────────────────────────────────────────
_ROMAN_UNITS: Final[tuple[str, ...]] = (
    "",
    "i",
    "ii",
    "iii",
    "iv",
    "v",
    "vi",
    "vii",
    "viii",
    "ix",
    "x",
    "xi",
    "xii",
    "xiii",
    "xiv",
    "xv",
    "xvi",
    "xvii",
    "xviii",
    "xix",
    "xx",
    "xxi",
    "xxii",
    "xxiii",
    "xxiv",
    "xxv",
    "xxvi",
    "xxvii",
    "xxviii",
    "xxix",
    "xxx",
)


def _fmt_value(num_fmt: str, n: int) -> str:
    if n <= 0:
        return ""
    if num_fmt == "decimal":
        return str(n)
    if num_fmt == "lowerLetter":
        # 1=a, 2=b, …, 26=z, 27=aa
        if n <= 26:
            return chr(ord("a") + n - 1)
        q, r = divmod(n - 1, 26)
        return chr(ord("a") + q - 1) + chr(ord("a") + r)
    if num_fmt == "upperLetter":
        if n <= 26:
            return chr(ord("A") + n - 1)
        q, r = divmod(n - 1, 26)
        return chr(ord("A") + q - 1) + chr(ord("A") + r)
    if num_fmt == "lowerRoman":
        return _ROMAN_UNITS[n] if n < len(_ROMAN_UNITS) else str(n)
    if num_fmt == "upperRoman":
        return (_ROMAN_UNITS[n].upper()) if n < len(_ROMAN_UNITS) else str(n)
    if num_fmt == "bullet":
        return ""
    # Unknown format: fall back to decimal.
    return str(n)


class NumberingCounter:
    """Stateful counter for DOCX automatic numbering.

    Keyed by ``abstractNumId`` (not ``numId``): Word creates many ``numId``
    instances that all point at the same abstract; sharing counters across
    them matches the rendered output. Within an abstract, maintains a
    per-``ilvl`` counter. Advancing ``ilvl=N`` resets deeper counters.
    Call :meth:`reset_all` at document boundaries (e.g. ISA transitions).
    """

    def __init__(self, spec: NumberingSpec) -> None:
        self._spec = spec
        # abstract_id → list[int] indexed by ilvl.
        self._state: dict[str, list[int]] = {}

    def reset_all(self) -> None:
        self._state.clear()

    def advance(self, num_id: str, ilvl: int) -> str:
        """Advance ``(numId→abstract, ilvl)`` and return the rendered number."""
        abs_id = self._spec.num_to_abs.get(num_id)
        if abs_id is None:
            return ""
        ab = self._spec.abstracts.get(abs_id)
        if ab is None:
            return ""
        level = ab.level(ilvl)
        if level is None:
            return ""

        counters = self._state.setdefault(abs_id, [])
        while len(counters) <= ilvl:
            counters.append(0)
        for deeper in range(ilvl + 1, len(counters)):
            counters[deeper] = 0
        if counters[ilvl] == 0:
            counters[ilvl] = level.start
        else:
            counters[ilvl] += 1

        if level.num_fmt == "bullet":
            return ""

        out = level.lvl_text
        for placeholder_ilvl in range(ilvl + 1):
            placeholder = f"%{placeholder_ilvl + 1}"
            v_level = ab.level(placeholder_ilvl)
            v_fmt = v_level.num_fmt if v_level is not None else "decimal"
            n = counters[placeholder_ilvl] if placeholder_ilvl < len(counters) else 0
            out = out.replace(placeholder, _fmt_value(v_fmt, n))
        return out
