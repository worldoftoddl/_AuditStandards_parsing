# Plan-approval checklist

**When to use.** Any `plan_approval_request` that touches database DDL,
external APIs, embeddings, vector index strategy, or schema-level data
contracts must go through the checklist below before the lead issues
`approve`. Origin: Phase 2c's approved plan shipped a `vector(4096) +
HNSW` schema that pgvector 0.8 cannot actually index (HNSW caps at
vector≤2000 / halfvec≤4000). The failure was caught only at
`ensure_schema` runtime. This document exists so the next sign-off
won't discover the same class of issue at runtime.

## Checklist

Every plan must answer these in writing. Missing answers are grounds
for rejection.

### Compatibility constraints

- [ ] **Vector index × dimension cap** — if any `CREATE INDEX ... USING
      hnsw|ivfflat` is planned, cite the pgvector version and its
      dimension caps (vector 2000, halfvec 4000, bit 64000 for HNSW on
      0.8). Confirm the chosen `<type>(<dim>)` fits.
- [ ] **Extension version floor** — features like `halfvec`, `bit`, or
      iterative index scans require pgvector ≥ 0.7. State the minimum
      version the plan assumes and verify against the target cluster.
- [ ] **External API caps** — embedding provider batch size, token
      limits per request, and rate limits are quoted from vendor docs,
      not memory.
- [ ] **Uniqueness/conflict keys** — every new `UNIQUE` or `PRIMARY KEY`
      clause is traced against every INSERT/UPSERT site to confirm the
      intended conflict path fires. Phantom constraints (PostgreSQL
      treats distinct NULLs as non-conflicting; earlier PK may shadow a
      later UNIQUE) must be called out.
- [ ] **Migration posture** — idempotent DDL for fresh installs; explicit
      ALTER recipe for existing tables; backfill order when `NOT NULL`
      columns are added.

### Evidence quality

- [ ] **Measurement vs recall** — every performance claim distinguishes
      "measured on this cluster / this dataset" from "cited from a
      benchmark". Benchmark citations include source + domain.
- [ ] **Scope reality** — extrapolations (e.g. "at 40k rows") are
      tagged with the phase at which that scope actually happens. A
      plan cannot use out-of-scope projections as its sole driver.
- [ ] **Rollback plan** — when a plan depends on a model or library
      choice that might not hold up in eval, the rollback path is
      described (schema change vs data re-population vs both) with the
      estimated cost in each dimension.

### Review routing

- [ ] **Independent review** — plans touching contracts the rest of the
      team consumes (schema, chunk IDs, embedding dim) are forwarded to
      `devils-advocate` before the lead issues `approve`.
- [ ] **Named request id** — every request carries `request_id` in a
      stable, searchable form: `<phase>-<topic>-v<n>`.

## Lead's decision format

When approving, quote the request id and list any "conditions of
approval" (items the plan does not need to change but that are tracked
elsewhere, e.g. in a followup task). When rejecting, cite which
checklist item failed and what the plan must add.

## Provenance

- Introduced: Phase 2d, after the v1 plan miss described above.
- Authored by: team-lead, in response to `devils-advocate` [MED-3]
  in the review of `phase2d-index-strategy-v1`.
- Enforcement: convention, not tooling. Anyone can block a plan that
  skips a checklist item.
