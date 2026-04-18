"""Tests for chunk.py: block merging + refs expansion + metadata."""

from pathlib import Path

from audit_parser.chunk import chunk_document
from audit_parser.docx_reader import read_docx
from audit_parser.ir import Block, Document, Standard
from audit_parser.structure import build_document


def _block(
    ordinal: int,
    *,
    kind: str = "paragraph_body",
    paragraph_id: str | None = None,
    text: str = "body",
    section: str = "requirements",
    heading_trail: tuple[str, ...] = ("ISA 200", "요구사항"),
    continuation_of: str | None = None,
    is_application: bool = False,
    style_id: str = "a1",
    refs: list[str] | None = None,
) -> Block:
    return Block(
        block_id=f"doc#{ordinal:05d}",
        source_path=Path("doc.docx"),
        ordinal=ordinal,
        style_id=style_id,
        text=text,
        raw_text=text,
        num_pr=None,
        kind=kind,
        level=None,
        heading_trail=heading_trail,
        section=section,
        paragraph_id=paragraph_id,
        is_application_guidance=is_application,
        is_toc=False,
        refs=refs or [],
        continuation_of=continuation_of,
    )


class TestChunkingMerge:
    def test_continuation_merges_into_parent(self):
        doc = Document(source_path=Path("doc.docx"))
        std = Standard(number="200", title="title")
        std.blocks = [
            _block(0, paragraph_id="14", text="parent body"),
            _block(
                1,
                paragraph_id=None,
                text="continuation tail",
                continuation_of="doc#00000",
            ),
        ]
        doc.standards.append(std)
        chunks = chunk_document(doc)
        assert len(chunks) == 1
        assert chunks[0].paragraph_ids == ["14"]
        assert "parent body" in chunks[0].text
        assert "continuation tail" in chunks[0].text

    def test_bullet_items_attach_to_prior_body(self):
        doc = Document(source_path=Path("doc.docx"))
        std = Standard(number="210", title="title")
        std.blocks = [
            _block(0, paragraph_id="6", text="parent"),
            _block(1, paragraph_id=None, text="first bullet", style_id="A0"),
            _block(2, paragraph_id=None, text="second bullet", style_id="A0"),
        ]
        doc.standards.append(std)
        chunks = chunk_document(doc)
        # bullets without continuation_of still attach to the most recent primary
        assert len(chunks) == 1
        assert "first bullet" in chunks[0].text
        assert "second bullet" in chunks[0].text

    def test_distinct_ids_produce_distinct_chunks(self):
        doc = Document(source_path=Path("doc.docx"))
        std = Standard(number="210", title="title")
        std.blocks = [
            _block(0, paragraph_id="6", text="req 6"),
            _block(1, paragraph_id="(a)", text="sub-a", style_id="A2"),
            _block(2, paragraph_id="(b)", text="sub-b", style_id="A2"),
        ]
        doc.standards.append(std)
        chunks = chunk_document(doc)
        assert [c.paragraph_ids for c in chunks] == [["6"], ["(a)"], ["(b)"]]

    def test_toc_and_headings_skipped(self):
        doc = Document(source_path=Path("doc.docx"))
        std = Standard(number="210", title="title")
        std.blocks = [
            _block(0, kind="heading_section", text="요구사항"),
            _block(1, paragraph_id="1", text="kept"),
        ]
        doc.standards.append(std)
        chunks = chunk_document(doc)
        assert len(chunks) == 1
        assert chunks[0].paragraph_ids == ["1"]

    def test_refs_get_expanded(self):
        doc = Document(source_path=Path("doc.docx"))
        std = Standard(number="200", title="title")
        std.blocks = [
            _block(0, paragraph_id="1", text="refs here", refs=["A20-A22", "A63"]),
        ]
        doc.standards.append(std)
        chunks = chunk_document(doc)
        assert chunks[0].refs == ["A20", "A21", "A22", "A63"]

    def test_heading_trail_in_text(self):
        doc = Document(source_path=Path("doc.docx"))
        std = Standard(number="200", title="title")
        std.blocks = [
            _block(0, paragraph_id="1", text="body", heading_trail=("ISA 200", "요구사항")),
        ]
        doc.standards.append(std)
        chunks = chunk_document(doc)
        assert chunks[0].text.startswith("ISA 200 > 요구사항")
        assert "body" in chunks[0].text

    def test_content_hash_stable(self):
        doc = Document(source_path=Path("doc.docx"))
        std = Standard(number="200", title="title")
        std.blocks = [_block(0, paragraph_id="1", text="hello")]
        doc.standards.append(std)
        chunks_a = chunk_document(doc)
        chunks_b = chunk_document(doc)
        assert chunks_a[0].content_hash == chunks_b[0].content_hash


# ── Integration: full DOCX produces the expected number of chunks ──────────
def test_full_docx_chunk_count(target_docx):
    raw, fns, spec = read_docx(target_docx)
    doc = build_document(target_docx, raw, fns, spec)
    chunks = chunk_document(doc)
    # Phase 2b baseline: ~4500 chunks. Guard against regressions that would
    # collapse many blocks into a single chunk or explode the count.
    assert 3000 < len(chunks) < 6000

    # Every chunk should carry heading_trail (no orphan blocks).
    without_trail = [c for c in chunks if not c.heading_trail]
    assert len(without_trail) < 50

    # No empty text.
    assert all(c.text.strip() for c in chunks)
