"""Block → Chunk conversion for retrieval/embedding.

Rules (agreed with audit-domain-expert + vector-db-expert):
- 1 body block = 1 chunk by default.
- ``continuation_of`` blocks merge into their parent.
- Bullet-only list items (e.g. A0/B with no paragraph_id) also merge into
  the nearest prior body block in the same section.
- ``is_toc`` and ``kind in {"heading_*", "table"}`` blocks are skipped at
  the chunk stage (headings live in ``heading_trail``; tables are emitted
  to markdown but not embedded — a future phase can add them).
- The embed target is ``heading_trail`` prefix + body text joined by
  newlines. Callers that worry about precision can strip the prefix.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable

from .ir import Block, Chunk, Document, Standard
from .numbering import expand_cross_refs

# Kinds that carry retrievable prose.
_BODY_KINDS: frozenset[str] = frozenset(
    {"paragraph_body", "paragraph_list_item", "paragraph_definition"}
)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _heading_prefix(trail: Iterable[str]) -> str:
    parts = [t for t in trail if t]
    return " > ".join(parts)


def _format_paragraph_id_prefix(pid: str | None) -> str:
    if not pid:
        return ""
    # sub-items like "(a)" / "(i)" don't need a trailing dot because they
    # already carry their own punctuation.
    if pid.startswith("("):
        return f"{pid} "
    return f"{pid}. "


def _chunk_id(isa_no: str, paragraph_ids: list[str], content_hash: str) -> str:
    if paragraph_ids:
        joined = "+".join(paragraph_ids)
        return f"{isa_no or 'preamble'}:{joined}"
    # Fallback when the chunk has no id at all (rare — used for preamble blocks).
    return f"{isa_no or 'preamble'}:{content_hash[:12]}"


def _build_chunk(
    *,
    primary: Block,
    extras: list[Block],
    isa_no: str,
    isa_title: str,
) -> Chunk:
    """Compose a Chunk from a primary block and its merged continuations."""
    all_blocks = [primary, *extras]
    paragraph_ids = [b.paragraph_id for b in all_blocks if b.paragraph_id is not None]
    # Preserve insertion order; de-dupe.
    seen: set[str] = set()
    unique_ids: list[str] = []
    for pid in paragraph_ids:
        if pid not in seen:
            seen.add(pid)
            unique_ids.append(pid)

    body_lines: list[str] = []
    for b in all_blocks:
        prefix = _format_paragraph_id_prefix(b.paragraph_id)
        body_lines.append(f"{prefix}{b.text}".strip())

    trail_str = _heading_prefix(primary.heading_trail)
    body_str = "\n".join(body_lines)
    embed_text = f"{trail_str}\n\n{body_str}" if trail_str else body_str

    refs_raw: list[str] = []
    for b in all_blocks:
        refs_raw.extend(b.refs)
    expanded_refs = expand_cross_refs(refs_raw)

    content_hash = _sha256(embed_text)
    section = primary.section or "other"
    is_app = any(b.is_application_guidance for b in all_blocks)
    is_appendix = section == "appendix"

    return Chunk(
        chunk_id=_chunk_id(isa_no, unique_ids, content_hash),
        isa_no=isa_no,
        isa_title=isa_title,
        section=section,
        heading_trail=list(primary.heading_trail),
        paragraph_ids=unique_ids,
        is_application_guidance=is_app,
        is_appendix=is_appendix,
        text=embed_text,
        char_count=len(embed_text),
        source_path=str(primary.source_path),
        content_hash=content_hash,
        refs=expanded_refs,
    )


def _chunk_standard(std: Standard | None, blocks: list[Block]) -> list[Chunk]:
    """Walk a block sequence, merging continuations, emitting chunks."""
    isa_no = std.number if std is not None else ""
    isa_title = std.title if std is not None else ""

    chunks: list[Chunk] = []
    # Map block_id → chunk index in progress so continuation_of can locate
    # its parent even when the parent was the most recent body block.
    pending: dict[str, tuple[Block, list[Block]]] = {}
    # Keep insertion order of the pending primaries.
    pending_order: list[str] = []

    def flush_all() -> None:
        for bid in pending_order:
            primary, extras = pending[bid]
            chunks.append(
                _build_chunk(primary=primary, extras=extras, isa_no=isa_no, isa_title=isa_title)
            )
        pending.clear()
        pending_order.clear()

    last_body_id: str | None = None
    for b in blocks:
        if b.is_toc or b.kind == "table" or b.kind.startswith("heading_"):
            # Headings and tables/TOC break the continuation window and aren't
            # embedded as separate chunks at this stage.
            continue
        if b.kind not in _BODY_KINDS:
            continue

        # Determine the target primary id.
        if b.continuation_of and b.continuation_of in pending:
            pending[b.continuation_of][1].append(b)
            continue
        if b.continuation_of is None and b.paragraph_id is None and last_body_id in pending:
            # Bullet/orphan with no explicit continuation — merge into the most
            # recent pending primary so we don't lose the text.
            pending[last_body_id][1].append(b)
            continue

        # Start a new primary chunk.
        pending[b.block_id] = (b, [])
        pending_order.append(b.block_id)
        last_body_id = b.block_id

    flush_all()
    return chunks


def chunk_document(doc: Document) -> list[Chunk]:
    """Produce a flat list of Chunks for the whole Document, preamble first."""
    all_chunks: list[Chunk] = []
    all_chunks.extend(_chunk_standard(None, doc.preamble))
    for std in doc.standards:
        all_chunks.extend(_chunk_standard(std, std.blocks))
    return all_chunks
