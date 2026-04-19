# Phase 4 P0 — Query-Set Expansion v2 → v3

**Status**: APPROVED 2026-04-19 (lead)
**request_id**: `phase4-p0-query-expansion-v2`
**parent phase**: Phase 3 (closed 2026-04-19)
**authored**: planner, 2026-04-19
**approved decisions**:
  - §3 카테고리 분배: **(B) req 12 / app 11 / cross 15 / def 12** (총 50)
  - §5 재측정 범위: **(a) 전량 재측정**
  - §6 append-only: **YES**. v2 §5.3 deferred 3건(Q11/Q18/Q19)은 Phase 4 P3로 계속 defer
  - §9.1 Retrofit 임계: S3 50% / S4 30% (DA 사전 조정 여지 열어둠)
  - §R6 Upstage 인덱스 확장: Phase 7 pre-flight 결과로 판단
**blocks**: Phase 4 P1 (rerank / hard-negative), Phase 4 P2 (chunker stub 병합), bulk ingest

## 0. 개요

Phase 3은 "bulk ingest blocked" 판정으로 종료됨. v2 recall@5 = BGE-ON 0.673
(CI-low 0.519) / UPS-ON 0.718 (CI-low 0.564). 양 모델 모두 절대 CI-low 게이트
0.70 미달. **게이트의 binding constraint는 점추정이 아니라 CI의 폭 (±0.15,
n=26)**. Phase 4 P0은 rerank·hard-negative 이전에 **평가세트 자체를 n=50±로
확장해 CI 폭을 좁히고** Phase 3 판정을 robust하게 재판정한다.

cross-standard를 6→15로 가장 크게 증강 (robust FAIL 카테고리 복구 최우선),
그 외 3 카테고리는 gold-sensitive 신호 (definitions 역전, UPS stub-bias)를
n≥10 수준까지 올린다.

## 1. Scope

**In**:
- `docs/eval/queries.yaml` v3 (v2 26개 보존 + 신규 24개, 총 n=50)
- 각 신규 쿼리 oracle gold chunk(s) + 2-pass resolver 매핑 검증
- `docs/eval/query_design_rules.md` (신규) — v1→v2 교훈 → design rule
- Phase 3 3축 (BGE-ON / BGE-OFF / UPS) 재측정 + 게이트 재판정
- Retrofit audit (DA 소관, `phase4_p0_retrofit_audit.md`)

**Out (Phase 4 후속 phase로 defer)**:
- Rerank / hard-negative mining (P1)
- Chunker-level intro-stub 병합 (P3)
- Paired ratio bootstrap (NIT-a) — P0.5로 끼워넣음
- Upstage bulk path (halfvec / ivfflat)

## 2. 산출물 맵

| 경로 | 변경 |
|---|---|
| `docs/eval/queries.yaml` | v2 → v3 (version: 3, total_queries: 50) |
| `docs/eval/query_design_rules.md` | **신규**. DR-1 ~ DR-5 |
| `docs/eval/phase4_p0_plan.md` | 본 문서 |
| `docs/eval/phase4_p0_oracle_log.md` | **신규**. DE 쿼리별 evidence block |
| `docs/eval/phase4_p0_retrofit_audit.md` | **신규 (DA 소관)**. 4-signal audit |
| `docs/eval/reports/phase4_p0_v3_{bge_on,bge_off,upstage_on}.json` | **신규** |
| `docs/eval/phase4_p0_report.md` | **신규**. phase3_report 포맷 재사용 |
| `src/audit_parser/eval.py` | 변경 없음 기대 (필요 시 P5 resolver 확장) |

## 3. 카테고리 분배 옵션

사용자 제안: req 7→13, app 6→12, cross 6→15, def 7→10 (총 50)

| 옵션 | req | app | cross | def | 메모 |
|---|---:|---:|---:|---:|---|
| (A) 사용자 제안 | 13 | 12 | 15 | 10 | cross 우선, def 확장 작음 |
| **(B) planner 권고** | **12** | **11** | **15** | **12** | def 12는 UPS stub-bias 재검증 가능 |
| (C) 보수 균형 | 13 | 13 | 13 | 11 | cross 15 oracle 확보 실패 시 fallback |

**권고: (B).** cross 15 feasibility는 §4에서 검증됨. def 12가 중요한 이유는
v2에서 BGE 0.952 vs UPS 0.714 역전이 n=7의 신호였기 때문. n≥10으로는 검증
불충분.

## 4. Cross-standard n=15 feasibility (사용자 위험 #5)

파싱 커버리지: **25 ISA, 3,748 chunks**. 허브 기준(200/240/315/330/500/540/
700/705)이 모두 100+ chunk 단위로 존재. v2의 6개 + 신규 9개 후보:

| # | 축 | primary 후보 | 신규? |
|---|---|---|---|
| v2-Q14 | RMM (200↔315↔330) | 200:13.(n), 315:23, 330:5 | 기존 |
| v2-Q15 | 전문가적 의구심 (200↔240) | 200:15, 240:13 | 기존 |
| v2-Q16 | 감사위험 모델 (200↔315↔330) | 200:13.(c/e/n) | 기존 |
| v2-Q17 | 유의적 위험 (315↔330↔240) | 315:27, 330:21 | 기존 |
| v2-Q18 | 부정×내부통제 (240↔315) | 240:26, 315:14 | 기존 |
| v2-Q19 | 회계추정 편의 (540↔240) | 540:32, 240:32 | 기존 |
| N1 | 감사증거 충분·적합성 (500↔330↔450) | 500:6, 330:7, 450:8 | 신규 |
| N2 | 서비스조직 통제 (402↔315↔330) | 402:9, 315:12, 330:12 | 신규 |
| N3 | 그룹감사×구성단위 위험 (600↔315↔330) | 600:17, 600:26, 315:11 | 신규 |
| N4 | 변형의견 발동 조건 (705↔450↔700) | 705:6, 450:11, 700:17 | 신규 |
| N5 | 계속기업×의견 (570↔705↔700) | 570:22, 705:21, 700:26 | 신규 |
| N6 | KAM×유의적 위험 (701↔315) | 701:9, 701:10, 315:27 | 신규 |
| N7 | 법규위반×부정 (250↔240) | 250:22, 240:22 | 신규 |
| N8 | 지배기구 소통×미비점 (260↔265) | 260:16, 265:9 | 신규 |
| N9 | 특수관계자×부정위험 (550↔240) | 550:18, 240:24 | 신규 |

**판정: n=15 실현 가능.** N5/N8만 작은 ISA 포함 → Phase 2에서 우선 검증.

## 5. 재측정 범위

| 옵션 | 비용 | 시간 | CI 정합 |
|---|---|---|---|
| (a) 전량 재측정 | UPS 24q × $0.00003 ≈ $0.0007 | 수 분 | ✓ |
| (b) delta-only | $0.0007 | 더 짧음 | 표본 독립성 가정 필요 |
| (c) 병행 | 동일 | 2× | audit trail 최강 |

**권고: (a).** 하네스 결정론적(cache hit). phase3 §3.2 "v2 vs v3 Δ" 표 포맷
재사용 가능.

## 6. v2→v3 구조

**append-only** + `version: 2 → 3`. v2 Q01–Q26 id·label 불변, Q27–Q50 추가.
이유: reproducibility 보존, retrofit audit 프레임 명확. v2 §5.3 deferred 3건
(Q11/Q18/Q19) 재라벨링은 P0 scope **밖**, Phase 4 P3로 계속 defer (동일
phase에서 old label 건드리면 audit trail 오염).

## 7. 구현 Phase (DoD 포함)

### Phase 1 — query_design_rules.md [M, DE 2h]

- DR-1: Intro-parent stub 금지 (본문 "다음과 같다." 형태는 primary 금지)
- DR-2: Heading_trail suffix 검증 (resolver 실측 매핑 로그 첨부)
- DR-3: Alphabetical `(i)` vs Roman `(i)` 모호성 회피 (`200:13.(i)` 패턴 금지)
- DR-4: Query phrasing과 primary framing 일치 (§8.5 워크숍 교훈)
- DR-5: Cross-standard는 **최소 2개 ISA** primary 필수

**DoD**:
- [ ] 5개 DR + 각 chunks.jsonl 원문 인용
- [ ] DE + DA 서명 (문서 내 섹션)
- [ ] 체크리스트 포맷: 신규 24개 각각에 ✓/✗ 마킹 가능

### Phase 2 — cross-standard 9 oracle 초안 [H, DE 10h]

§4.2의 N1~N9 각각:
1. 쿼리 자연어 초안
2. primary chunk_ids (최소 2개 ISA, DR-5)
3. chunks.jsonl 본문 원문 인용 (DR-1 stub 검증)
4. heading_trail 기록 (DR-2)
5. related chunks (top-10 보조)
6. notes — retrofit 체크 (DR-4)

9개 중 oracle 확보 실패 시 → (C) 분배 fallback trigger.

**DoD**:
- [ ] 9개 evidence block (v2 Q10/Q14/Q16 포맷)
- [ ] 2-pass resolver 실측 매핑 로그
- [ ] 모든 primary char_count ≥ 50
- [ ] section 분류 정합

### Phase 3 — req +5 / app +5 / def +5 oracle 초안 [M, DE 10h]

분배 (B) 가정. v2 미커버 영역 타겟:
- requirements 5: ISA 230 문서화, 450 왜곡표시 평가, 580 서면진술, 700 보고서 구성, 610 내부감사 이용
- application 5: 200 윤리, 315 통제 이해, 500 증거 신뢰성, 540 추정, 700 variant
- definitions 5: 정의 역전·stub-bias 검증 강화 — "충분한 적합한 감사증거", "경영진 주장", "해당성 있는 기준", "감사범위", "감사의견 변형"

**DoD**:
- [ ] 15개 evidence block
- [ ] section 일치 검증
- [ ] DR-1~DR-5 ✓ 전원 통과
- [ ] char_count ≥ 50

### Phase 4 — queries.yaml v3 merge + 하네스 검증 [L, DE 1h + lead 0.5h]

- v2 Q01–Q26 보존, Q27–Q50 추가
- version: 3, total_queries: 50
- 메타데이터 코멘트 블록 (v2 rev 블록과 병렬)
- `pytest -q` + `ruff check` 통과
- `eval-run` smoke (resolver만) — 50개 모두 resolve 확인

**DoD**:
- [ ] `yaml.safe_load` 성공
- [ ] 50개 resolver 통과 (unresolved_paths 빈 상태)
- [ ] 카테고리 카운트 req=12, app=11, cross=15, def=12
- [ ] `pytest -q` green, `ruff check` clean

### Phase 5 — Retrofit audit (DA 소관) [M, DA 4h]

Phase 3 §5 3-signal → 4-signal 확장:

- **S1 Verdict flip**: 사전 계산 불가. Phase 7 후 역산
- **S2 One-way movement**: v3 신규 24개가 특정 모델 유리 방향 bias 검증
- **S3 실패 쿼리 bias**: Phase 3 17 실패 쿼리와 v3 신규 24개의 단어/heading_trail 겹침률. **임계 50% 초과 시 blocking flag**
- **S4 Oracle 겹침**: v3 신규 primary 중 "Phase 3 top-5에 이미 오른 chunk" 비율. **임계 30% 초과 시 flag**

**DoD**:
- [ ] 4 signal 정량 측정
- [ ] 임계 위반 시 Phase 2/3 rework
- [ ] DE + Planner + DA 3자 서명

### Phase 6 — Plan-approval checklist [L, lead 1h]

`docs/plan_approval_checklist.md` 11개 항목 인라인 응답. 주요:
- External API caps: Upstage 24q × solar-embedding-1-large-query, ~$0.0007, 60 RPM (여유)
- Migration posture: N/A (데이터 작업, 스키마 불변)
- Rollback: queries.yaml `git revert` 로 v2 복귀, `.work/eval_v2_*.json` 보존
- Independent review: DA Phase 5로 배치

**DoD**:
- [ ] 11개 응답 (N/A 포함)
- [ ] lead `approve` 발행
- [ ] request_id `phase4-p0-query-expansion-v2`로 승격

### Phase 7 — 재측정 실행 [M, lead 2h]

- `EMBED_PROVIDER=bge` + `TABLE=audit_chunks` (ON)
- `EMBED_PROVIDER=bge` + `TABLE=audit_chunks_notrail` (OFF)
- `EMBED_PROVIDER=upstage` + `TABLE=audit_chunks_eval_upstage` (ON)

**Pre-flight**: Upstage 95-row 인덱스가 v3 신규 oracle 커버 확인.
미커버 시 인덱스 mini-확장.

**DoD**:
- [ ] 3 JSON 생성
- [ ] overall recall@5 + 95% CI
- [ ] 카테고리별 recall@5 + precision@5 + MRR + nDCG@10
- [ ] Upstage 인덱스 커버리지 확인

### Phase 8 — 분석 + Phase 4 P0 보고서 [M, lead + DE 4h]

phase3_report §1–§7 포맷 재사용. 게이트 재판정:
- 절대 point: BGE / UPS vs 0.70
- 절대 CI-low: 95% bootstrap CI 하단 vs 0.70
- 상대: BGE/UPS ratio vs 0.95 (paired CI는 NIT-a, P0.5로 defer)
- 카테고리 cross-standard vs 0.55

**DoD**:
- [ ] Dual-gate 판정 표 (v2 vs v3)
- [ ] 카테고리 표
- [ ] Retrofit audit 결과 §5에 포함
- [ ] Verdict 한 줄 (α/β/γ)
- [ ] Phase 4 P1 개시 필요성 명시

### Phase 9 — 리뷰 + 종결 [L, 3인 1h]

3-way review. 판정:
- (α) Phase 3과 동일 blocked → P1 (rerank) 즉시 개시
- (β) 부분 clear (BGE 또는 UPS 한쪽 통과) → 모델 선택 + 조건부 ingest
- (γ) 양쪽 통과 → bulk ingest unblock, schema v4 인덱스 확정

## 8. 예산 집계

| 역할 | 합계 |
|---|---:|
| DE | 25.3h |
| Planner | 3h |
| Lead | 5.8h |
| DA | 4.3h |
| **Total** | **~38h** (3–4 영업일) |

DE peak 25h는 Phase 2+3 합산 20h가 가장 큼. Cross-standard 9 oracle 확보가
최대 risk point — 5개 이하면 (C) fallback trigger.

## 9. 위험 & 완화

| # | 위험 | 완화 | 잔존 |
|---|---|---|---|
| R1 | Retrofit 재발 (DA #1) | Phase 5 4-signal audit, 정량 임계 50%/30% | DA judgement로 blocking flag 가능 |
| R2 | Query-design protocol 이탈 (#2) | Phase 1 DR 체크리스트 강제 | DR-3 Roman `(i)`는 resolver P5 defer, 패턴 자체 회피만 가능 |
| R3 | 재측정 범위 (#3) | §5 옵션 (a) 전량 | 없음 |
| R4 | Oracle 확보 비용 (#4) | DE 25.3h 예산 | 특정 ISA 파싱 품질 문제 시 (C) fallback |
| R5 | Cross-standard n=15 (#5) | §4 9 후보 enum, feasibility 확인 | N5/N8 작은 ISA — Phase 2에서 무산 시 cross 축소 |
| R6 | **Upstage 인덱스 커버리지 [MED]** | Phase 7 pre-flight 확인 | mini-확장 작업 추가 |
| R7 | **chunks.jsonl 불변성 [LOW]** | P0 기간 PR freeze 공지 | chunker 변경 시 oracle chunk_id 파손 |

## 10. 성공 기준

- [ ] queries.yaml v3 (n=50)
- [ ] 신규 24개 evidence block + resolver 매핑 로그
- [ ] query_design_rules.md 5 DR
- [ ] Retrofit audit 4-signal 통과
- [ ] Plan-approval 11 체크리스트 `approve`
- [ ] v3 재측정 3축 완료
- [ ] Phase 4 P0 report + verdict α/β/γ
- [ ] `pytest -q` green, `ruff check` clean
- [ ] 3-way review 서명 + Status: CLOSED

---

## 11. Plan-approval checklist 응답 (inline)

`docs/plan_approval_checklist.md` 10개 항목 응답. 누락 = 반려 사유.

### 11.1 Compatibility constraints

- [x] **Vector index × dimension cap** — **N/A**. 본 P0은 `audit_chunks`/
      `audit_chunks_notrail`/`audit_chunks_eval_upstage` 기존 3개 테이블을
      그대로 사용. 신규 `CREATE INDEX` 없음. 기존 HNSW는 Phase 3에서 검증됨
      (vector(1024) ≤ 2000 cap, Upstage는 seq scan으로 dim cap 회피).
- [x] **Extension version floor** — **N/A**. 스키마 변경 없음. Phase 3 pgvector
      0.8 assumption 계속 유지.
- [x] **External API caps** — Upstage solar-embedding-1-large-query API 사용.
      - 비용: 24개 신규 쿼리 × 약 $0.00003 ≈ **$0.0007** (phase3에서 측정된
        단가 인용, solar embedding is $0.1 per 1M tokens 벤더 공식 가격).
      - rate limit: Upstage 공식 문서 기준 solar embedding 60 RPM — 24 쿼리는
        1분 내 처리 가능 (여유).
      - batch size: `scripts/embed_eval_upstage.py`가 쿼리 단건 호출, batch 없음.
      - 캐시: `.embed_cache.sqlite` content-hash 기반 hit — 동일 쿼리 텍스트
        재실행 시 API 미호출.
- [x] **Uniqueness/conflict keys** — **N/A**. `queries.yaml` 편집만.
      `audit_chunks`의 PK(`chunk_id`) 및 UNIQUE(`source_path`, `content_hash`,
      `embed_model`)는 P0 기간 건드리지 않음. chunks.jsonl 재생성 금지 (§R7).
- [x] **Migration posture** — **N/A**. DDL 없음. YAML schema_version 2 → 3
      bump은 eval 하네스의 `yaml.safe_load` 단계에서만 관찰되므로 runtime
      migration 아님.

### 11.2 Evidence quality

- [x] **Measurement vs recall** — Phase 3 게이트 (recall@5 ≥ 0.70, CI-low,
      cross-standard 0.55, BGE/UPS 0.95) 는 "measured on audit_standards
      cluster, `audit_chunks` (3789 rows BGE-ON), `audit_chunks_notrail`
      (3789 rows BGE-OFF), `audit_chunks_eval_upstage` (95 rows UPS-ON)"
      명시. 벤치마크 인용 없음.
- [x] **Scope reality** — n=50 목표는 P0 phase 2+3에서 실제 확보 대상 수치.
      추가 확장 (n=100+)은 Phase 4 P1+로 out-of-scope. CI 개선 추정 (±0.15
      → ±0.10 근방)은 표본 크기 증가에 따른 일반적 기대치로 명시하고, 실측은
      Phase 7 후 확정 예정.
- [x] **Rollback plan** — 3단계:
      1. **queries.yaml v3 롤백**: `git revert <commit>` 로 v2 (26 queries)
         복귀. chunks·embedding 테이블 불변이므로 재측정 없이 v2 상태 즉시 복원.
      2. **레이블 버그 발견 시**: oracle_log.md만 수정, queries.yaml v3 유지.
      3. **Retrofit audit (Phase 5) blocking flag**: Phase 2/3 oracle을 부분
         rework. 전체 rework 비용은 DE 10h 수준 (재생성 가능).
      - `.work/eval_v2_*.json` 은 보존하여 이전 결과 비교 가능 상태 유지.

### 11.3 Review routing

- [x] **Independent review** — `devils-advocate` 를 Phase 5 (retrofit audit) 에
      배치. lead `approve` 발행은 본 응답 단계에서 1차 완료. Phase 2/3 oracle
      완료 후 Phase 5 DA 리뷰를 반드시 통과해야 Phase 7 재측정 진입 가능.
- [x] **Named request id** — `phase4-p0-query-expansion-v2` (v1 → v2 승격).
      검색 가능 포맷 `<phase>-<topic>-v<n>` 준수.

### 11.4 Lead's decision

**APPROVED** `phase4-p0-query-expansion-v2`, 2026-04-19.

**Conditions of approval**:
1. Phase 5 DA 4-signal audit 통과 없이 Phase 7 재측정 진입 금지.
2. Phase 2에서 cross-standard oracle 확보 실패 (< 7개) 시 lead에 즉시 보고,
   분배 (C) 13-13-13-11로 re-plan (별도 approve 생략, lead 구두 승인으로 대체).
3. P0 기간 중 `src/audit_parser/chunk.py`, `structure.py`, `numbering.py` PR
   freeze. 해당 파일 수정 필요 시 P0 일시 중단 → chunks.jsonl 재생성 → P0 재시작.
4. Phase 7 재측정 전 Upstage 95-row 인덱스 커버리지 pre-flight 필수.
   미커버 시 인덱스 확장 mini-task 선행.

---

**승인 후 다음 단계**: 팀 소환 (team-lead + DE + DA) → Phase 1 (design rules) 착수.
