"""Phase 1 프로파일러: DOCX 스타일 분포 + 샘플 추출.

대상: raw/감사인증기준/감사기준 전문/0. 회계감사기준 전문(2025 개정).docx

산출:
- stdout: 스타일별 빈도, 레벨 힌트, 샘플 텍스트
- docs/style_samples.md: 스타일별 샘플 블록 (Phase 1 매핑 초안 근거)
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

from docx import Document
from docx.document import Document as DocxDocument
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

DEFAULT_DOCX = (
    Path(__file__).resolve().parent.parent
    / "raw"
    / "감사인증기준"
    / "감사기준 전문"
    / "0. 회계감사기준 전문(2025 개정).docx"
)

SAMPLES_PER_STYLE = 8
MAX_PREVIEW = 140


def iter_body_paragraphs(doc: DocxDocument):
    """문서 body의 단락을 순서대로 yield. 표 안쪽도 평탄화."""
    for child in doc.element.body.iterchildren():
        tag = child.tag
        if tag == qn("w:p"):
            yield Paragraph(child, doc)
        elif tag == qn("w:tbl"):
            tbl = Table(child, doc)
            for row in tbl.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        yield p


def style_name(p: Paragraph) -> str:
    pPr = p._p.find(qn("w:pPr"))
    if pPr is None:
        return ""
    pStyle = pPr.find(qn("w:pStyle"))
    if pStyle is None:
        return ""
    return pStyle.get(qn("w:val")) or ""


def outline_level(p: Paragraph) -> str:
    """direct formatting 또는 스타일의 outlineLvl 힌트(없으면 '')."""
    pPr = p._p.find(qn("w:pPr"))
    if pPr is None:
        return ""
    ol = pPr.find(qn("w:outlineLvl"))
    if ol is None:
        return ""
    return ol.get(qn("w:val")) or ""


def numbering_ref(p: Paragraph) -> str:
    pPr = p._p.find(qn("w:pPr"))
    if pPr is None:
        return ""
    numPr = pPr.find(qn("w:numPr"))
    if numPr is None:
        return ""
    numId = numPr.find(qn("w:numId"))
    ilvl = numPr.find(qn("w:ilvl"))
    nid = numId.get(qn("w:val")) if numId is not None else "?"
    lvl = ilvl.get(qn("w:val")) if ilvl is not None else "?"
    return f"numId={nid},ilvl={lvl}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", nargs="?", default=str(DEFAULT_DOCX))
    parser.add_argument(
        "--out",
        default=str(Path(__file__).resolve().parent.parent / "docs" / "style_samples.md"),
    )
    args = parser.parse_args()

    docx_path = Path(args.docx)
    if not docx_path.exists():
        print(f"NOT FOUND: {docx_path}", file=sys.stderr)
        return 2

    print(f"Loading {docx_path.name} ({docx_path.stat().st_size/1024/1024:.1f} MB)...")
    doc = Document(str(docx_path))

    counter: Counter[str] = Counter()
    samples: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    outline_by_style: dict[str, Counter[str]] = defaultdict(Counter)
    numbering_by_style: dict[str, Counter[str]] = defaultdict(Counter)
    total = 0
    empty = 0

    for p in iter_body_paragraphs(doc):
        text = p.text.strip()
        if not text:
            empty += 1
            continue
        total += 1
        style = style_name(p) or "<NO_STYLE>"
        counter[style] += 1
        outline_by_style[style][outline_level(p)] += 1
        numbering_by_style[style][numbering_ref(p)] += 1
        if len(samples[style]) < SAMPLES_PER_STYLE:
            samples[style].append(
                (text[:MAX_PREVIEW], outline_level(p), numbering_ref(p))
            )

    print()
    print(f"total paragraphs (non-empty): {total}")
    print(f"empty paragraphs: {empty}")
    print(f"distinct styles: {len(counter)}")
    print()
    print("=== Style distribution (desc) ===")
    print(f"{'style':<16} {'count':>6}  {'top outlineLvl':<18} top numPr")
    for style, cnt in counter.most_common():
        top_ol = outline_by_style[style].most_common(1)[0]
        top_num = numbering_by_style[style].most_common(1)[0]
        ol_desc = f"{top_ol[0] or '-'} ({top_ol[1]})"
        num_desc = f"{top_num[0] or '-'} ({top_num[1]})"
        print(f"{style:<16} {cnt:>6}  {ol_desc:<18} {num_desc}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Style samples — {docx_path.name}",
        "",
        f"- total non-empty paragraphs: **{total}**",
        f"- distinct styles: **{len(counter)}**",
        "",
        "Each section lists up to 8 samples. `outlineLvl` / `numPr` columns reveal whether",
        "the style carries Word's native heading level or numbering reference.",
        "",
    ]
    for style, cnt in counter.most_common():
        lines.append(f"## `{style}` — {cnt} blocks")
        lines.append("")
        lines.append("| # | outlineLvl | numPr | preview |")
        lines.append("|---|---|---|---|")
        for i, (text, ol, num) in enumerate(samples[style], 1):
            safe = text.replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {i} | {ol or '-'} | {num or '-'} | {safe} |")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print()
    print(f"Samples written: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
