# Phase 3 Report — dual-gate retrieval eval

**Status.** Closed 2026-04-19 after three-way team review (audit-domain-expert,
vector-db-expert, devils-advocate) on top of the Phase 2d eval harness.
Companion documents: `queries.yaml` v2, `phase3_self_audit_2026_04_19.md`,
`phase3_failure_analysis.md`, `plan_approval_checklist.md`.

## 1. Question this phase answered

Phase 2d shipped the schema and the ingest path but deferred the retrieval
quality question to Phase 3. Phase 3 asked: *is the Phase 2d decision —
BGE-M3 + `heading_trail` prefix on — good enough to ingest the full 4526-
chunk corpus?*

The phase answered **no**, on robust grounds, after measuring against the
26-query gold set twice (v1 labels and v2 labels, the dual-track protocol
that devils-advocate introduced to keep the gold revision honest).

## 2. What shipped

### Code
- `src/audit_parser/eval.py` — gold loader, two-pass positional resolver
  (`section == parent.section` first, `heading_trail` suffix as fallback)
  with a shorthand resolver for the `{isa}:{para_id}` form used in
  `queries.yaml`, recall@5 / precision@5 / MRR / nDCG@10 metrics, and a
  percentile bootstrap CI.
- `src/audit_parser/cli.py` — new `eval-run` sub-command; `_resolve_dsn`
  now URL-quotes user/password and the embedder is picked via
  `EMBED_PROVIDER` (`bge` | `upstage`).
- `src/audit_parser/db.py` — schema v4: the `chunk_id` widens to
  `{isa}:{block_ordinal:05d}:{para_id}` (eliminates the 344 duplicate
  chunk_ids DE found in the self-audit), a new `block_ordinal` column and
  index, `table_name` parameter on `_create_schema_sql` and
  `upsert_chunks`, and a `chunk.isa_no == '?'` filter with `INFO` logging.
- `src/audit_parser/db_eval.py` — `audit_chunks_eval_upstage` scaffold and
  helpers for the Upstage head-to-head.
- `src/audit_parser/chunk.py` — threads `block_ordinal` through; adds an
  `include_heading_trail` option so the A/B-2 sibling chunk set can be
  produced from the same IR.
- `scripts/bulk_embed.py` — emits both sibling chunk sets (trail ON +
  OFF), re-embeds with BGE-M3, upserts into `audit_chunks` and
  `audit_chunks_notrail` with distinct `embed_model` labels. Pins
  `PG_DATABASE=audit_standards` explicitly after the first run accidentally
  landed in the IFRS database.
- `scripts/embed_eval_upstage.py` — the 95-row Upstage eval subset,
  reusing `resolve_logical_path` plus a paragraph_ids fallback.

### Docs
- `docs/eval/queries.yaml` v2 with 5 corrected gold labels
- `docs/eval/phase3_self_audit_2026_04_19.md` (DE, Phase 3 kickoff)
- `docs/eval/phase3_failure_analysis.md` (DE, analysis of results)
- `docs/plan_approval_checklist.md` — unchanged from Phase 2d but
  actively enforced this phase: it caught v1 of the chunk-id migration
  plan, forcing a v2 that held up.

### Tests
`ruff check` passes; `pytest -q` = 152 passing after the chunk_id and
resolver rework.

## 3. Measurements

### 3.1 Corpus on `audit_standards`

| Table | Rows | Model | Dim | Index |
|---|---:|---|---:|---|
| `audit_chunks` | 3789 | `BAAI/bge-m3` | 1024 | partial HNSW (`WHERE is_toc = FALSE`) |
| `audit_chunks_notrail` | 3789 | `BAAI/bge-m3:notrail` | 1024 | partial HNSW |
| `audit_chunks_eval_upstage` | 95 | `solar-embedding-1-large-passage` | 4096 | seq scan (dim > 2000 HNSW cap) |

4526 chunks were produced; 737 `?:` preamble chunks were filtered at
upsert. Two BGE passes at CPU-only ~0.4s/chunk totalled ~60 minutes.
Upstage cost: **\$0.0007** (caches hit on re-runs).

### 3.2 Overall `recall@5`

| track | BGE-ON | BGE-OFF | UPS-ON |
|---|---:|---:|---:|
| v1 | 0.558 | 0.500 | 0.705 |
| v2 | **0.673** | 0.590 | **0.718** |
| Δ | +0.115 | +0.090 | +0.013 |

### 3.3 95% bootstrap CI on `recall@5`

| track | BGE-ON CI | UPS-ON CI |
|---|---|---|
| v1 | [0.385, 0.731] | [0.551, 0.859] |
| v2 | [0.519, 0.821] | [0.564, 0.865] |

### 3.4 Gates

| Gate | v1 | v2 | Robust? | Verdict |
|---|---|---|:-:|---|
| abs point BGE ≥ 0.70 | FAIL (0.558) | FAIL (0.673) | ✓ | **robust FAIL** |
| abs point UPS ≥ 0.70 | PASS (0.705) | PASS (0.718) | ✓ | PASS (point only) |
| abs CI-low BGE ≥ 0.70 | FAIL (0.385) | FAIL (0.519) | ✓ | **robust FAIL** |
| abs CI-low UPS ≥ 0.70 | FAIL (0.551) | FAIL (0.564) | ✓ | **robust FAIL** |
| relative BGE / UPS ≥ 0.95 | FAIL (0.791) | FAIL (0.938, near) | ⚠ gold-sensitive | FAIL |
| A/B-2 prefix Δ ≥ +0.05 | PASS (+0.058) | PASS (+0.083) | ✓ | **robust PASS — trail ON** |
| cross-standard BGE ≥ 0.55 | FAIL (0.167) | FAIL (0.222) | ✓ | robust FAIL |
| cross-standard UPS ≥ 0.55 | FAIL (0.306) | FAIL (0.361) | ✓ | robust FAIL |

### 3.5 Categories (v2)

| category | n | BGE-ON | BGE-OFF | UPS-ON |
|---|---:|---:|---:|---:|
| requirements | 7 | 0.714 | 0.643 | **0.929** |
| application | 6 | 0.750 | 0.611 | **0.833** |
| cross-standard | 6 | 0.222 | 0.250 | 0.361 |
| definitions | 7 | **0.952** | 0.810 | 0.714 |

The `definitions` reversal is notable: BGE's score climbs from 0.714 to
0.952 when the Phase 2d `200:13` stub ("감사기준에서 사용하는 용어의
정의는 다음과 같다.") is replaced with the actual sub-items, while
Upstage drops from 0.857 to 0.714. DE's reading — that v1's Upstage
lead in definitions was an artifact of the stub label — is consistent
with these numbers, though at n=7 it is a signal, not a conclusion.

## 4. Verdict

### 4.1 Robust
1. **Bulk ingest is blocked.** BGE and Upstage both fail the absolute
   CI-low gate on both tracks. The Phase 2d expansion gate
   (`recall@5 ≥ 0.70` on the 26-query set) is not cleared.
2. **`heading_trail` prefix stays on.** A/B-2 Δ = +0.058 (v1) → +0.083
   (v2). Same sign, crosses the +0.05 threshold both times.
3. **Cross-standard category fails on both models.** The first Phase 4
   candidate.

### 4.2 Gold-sensitive
4. **BGE/UPS relative gap narrowed** from 0.791 to 0.938 after the 5
   label corrections. The gate is still missed (< 0.95 point estimate,
   and no paired ratio CI was computed), but the direction is towards
   BGE being competitive.
5. **Definitions reversal** is a signal inside n=7, not a conclusion.
   Phase 4 needs a wider query set before calling it.

### 4.3 Deferred
6. Model selection (BGE vs Upstage) remains open. Neither clears the
   absolute gate yet.
7. A dense Upstage index would require pgvector ≥ 0.8 `halfvec` or an
   `ivfflat` strategy (HNSW is capped at 2000 dim); that's Phase 2c
   territory and would need its own `plan_approval` pass.

## 5. Retro-fit defences that held

devils-advocate's three-signal retro-fit check came back negative:

| Signal | What would indicate retro-fit | What we saw |
|---|---|---|
| Verdict flips | v1 said "block bulk", v2 flips to "go" | both tracks said "block bulk" |
| One-way score movement | every cell rises | `definitions` UPS dropped −0.143 |
| DE prediction matches reality | BGE +0.15 / UPS +0.10 predicted, measured ≈ the same | measured BGE +0.115 / **UPS +0.013** — DE's UPS prediction was off |

In parallel, DE's own §8 reverse audit (v2 schema) enumerated every
primary chunk in the v1 labels and reported zero cases where the gold
label was lenient enough for a model to stumble onto. The revision sits
on labelling corrections, not on the score tape.

## 6. NITs (from the verdict)

These are not blockers — they belong in Phase 4:

- **[NIT-a] paired bootstrap ratio CI** for `BGE / UPS` is not computed.
  The independent CIs are reported but the 0.938 point estimate is
  being compared to 0.95 without a CI on the ratio itself. Phase 4
  should add a paired-ratio bootstrap.
- **[NIT-b] Small-n.** Categories are n=6–7. Direction signals only;
  absolute category scores should not drive operational choices.
- **[NIT-c] Prediction vs observation tape** is recorded above — kept
  so future gold revisions can be checked against the precedent.
- **[NIT-d] Phase 4 priorities are linked** from DE's
  `phase3_failure_analysis.md` §§8–9: P0 query-set expansion, P1
  rerank or hard-negative mining, then chunker-level stub handling.

## 7. Open items for Phase 4

| # | Topic | Why it matters |
|---|---|---|
| 1 | Query-set expansion beyond 26 | CIs are the binding gate right now |
| 2 | Cross-standard retrieval improvement (rerank / hard-negative) | Robust category failure |
| 3 | Chunker-level stub handling | `200:13` style intro parents should not be indexable as standalones |
| 4 | Paired ratio bootstrap in the harness | NIT-a |
| 5 | BGE-vs-Upstage rematch once the above land | Verdict 4.3.6 deferred to this point |
| 6 | Upstage bulk path (pgvector `halfvec` / `ivfflat`) | Only if the rematch says Upstage wins |
