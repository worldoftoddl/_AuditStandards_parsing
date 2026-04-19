# Phase 4 P0 — Retrofit 4-Signal Audit

## Status: DRAFT — design skeleton, pre-implementation

작성 시점: 2026-04-19. §1-§10 spec complete; §5 breakdown 로직은 `.work/eval_v2_*.json` schema inspection pending. 측정 결과는 task#5 open 후 §2~§8 각 섹션에 append 하는 단일 파일 evolution 구조 (Phase 3 `phase3_failure_analysis.md` precedent). Title 에서 "P5" 표기 제거 — retrofit audit 은 P0 signoff gate 의 산출물이며 P5 는 P0 내부 phase 식별자.

**Owner**: devils-advocate (DA)
**Blocking flag**: yes — P7 (task#6) 차단.
**Implementation gate**: task#5 open 조건 = task#4 (queries.yaml v3 merge) closed.
**Lead-approved parallel work**: design 단계 작성은 queries.yaml v3 merge 와 무관한 영역 (아키텍처, tokenization, Jaccard 수식, breakdown, 재현 명세) 선행 가능. 2026-04-19 lead 승인으로 단일 파일 통일 (Phase 3 precedent 패턴 적용).
**Referenced docs**:
- `docs/eval/phase4_p0_plan.md` §7 (Phase 5), §9.1 (task#5 DoD)
- `docs/eval/query_design_rules.md` §DR-4 (tokenization 스펙), §서명 조건
- `docs/eval/phase3_failure_analysis.md` §5 (17 failures 목록)
- `docs/eval/phase4_p0_oracle_log.md` (cross-standard 9 oracle evidence)

---

## §1. Purpose & Inputs/Outputs

### Purpose
P4 (queries.yaml v3 merge) 이후 P7 (3축 재측정) 진입 전에 **query set 확장에 따른 test-set bias 감사**. 4 signal (S1/S2/S3/S4) 의 정량 측정으로 v3 query set 이 Phase 3 의 17 실패 쿼리 방향으로 편향되었는지, 또는 Phase 3 top-5 결과에 이미 포함된 chunk 집합에 편향되었는지 판정.

### Inputs
| 경로 | 목적 | 접근 시점 |
|---|---|---|
| `docs/eval/queries.yaml` (v3) | S2/S3/S4 primary chunk_ids + query 토큰 | task#4 close 후 |
| `.work/eval_v2_bge_on.json` | Phase 3 BGE-ON 실행 결과 (per-query top-5 chunk_ids) | (구조 inspection pending) |
| `.work/eval_v2_bge_off.json` | Phase 3 BGE-OFF 실행 결과 | 동일 |
| `.work/eval_v2_upstage_on.json` | Phase 3 Upstage 실행 결과 | 동일 |
| `docs/eval/phase3_failure_analysis.md` §5 | 17 실패 쿼리 (query_id + 토큰) | 이미 접근 가능 |
| `data/chunks.jsonl` | chunk 본문 (S4 분모 계산 참조) | 이미 접근 가능 |

**파일 구조 inspection pending**: `.work/eval_v2_*.json` 의 per-query hits schema 는 §5 전 단계에서 Read 로 확인 후 본 design 업데이트.

### Outputs
산출 파일: **본 문서 자체** (`docs/eval/phase4_p0_retrofit_audit.md`, 단일 파일 evolution). Design spec 작성 후 task#5 open 시점에 측정 결과를 §2-§8 아래 각 섹션에 추가, §9 verdict 및 3-way signoff 로 최종 완료.

Schema (전체 구조, 측정 결과 기록 시 기준):
```markdown
# Phase 4 P0 — Retrofit Audit Report

## §1. Inputs & Run metadata
- queries.yaml v3 SHA
- .work/eval_v2_*.json SHA (3 파일)
- retrofit_audit.py git commit SHA
- Run timestamp, seed (해당 시)

## §2. S1 — Verdict flip (deferred to Phase 7)
- N/A 이 report 단계, Phase 7 재측정 후 역산.

## §3. S2 — One-way movement (질적 분석)
- v3 신규 24개 쿼리의 모델별 예상 유불리 방향 table

## §4. S3 — 실패 쿼리 bias (임계 50%)
- Phase 3 17 failures vs v3 신규 24 쿼리 Jaccard 유사도 table
- 최대값, 평균, 임계 50% 초과 query_id 목록
- 판정: PASS / FAIL + blocking flag

## §5. S4 — Oracle 겹침 (임계 30%)
- v3 신규 primary chunk_ids (≈ 72개) 중 Phase 3 top-5 hit 이력 보유 chunk 비율
- Per-model breakdown (BGE-ON / BGE-OFF / Upstage)
- 판정: PASS / FAIL + blocking flag

## §6. Monitored pair proximity diagnostic (P-1, P-2)
- cross-oracle adjacent ¶ pair (N2↔N3 = P-2) 의 retrieval 혼동 통계

## §7. Obs-3 parser limitation 입력 지점
- 701:9 "문단9" cross-ref 파싱 누락 영향 범위

## §8. N5 axis-weak false-positive tracking
- 705:21 (N5 primary, axis 약) 의 non-N5 쿼리 top-5 hit 빈도

## §9. Verdict
- Per-signal PASS/FAIL
- 전체 signoff: DE + Planner + DA 3자 서명 영역

## §10. Appendix
- 재현 명령, 환경 변수, 실행 로그 해시
```

**Signoff gate**: `## §9. Verdict` 블록에 DE + Planner + DA 3 agent 서명 (inline 서명 형식: "signed: <agent_id> <timestamp>") → P7 진행 허용.

---

## §2. S1–S4 4-Signal 정의 + 임계 (50% / 30% 고정)

### S1 — Verdict flip
- **정의**: v2 쿼리 집합과 v3 쿼리 집합에서 동일 gate 기준 (recall@5 / MRR / nDCG@10 등) 에 대해 최종 판정 (PASS / FAIL / borderline) 이 **flip** 된 track 수.
- **시점**: Phase 5 계산 불가 — Phase 7 재측정 후 v2 basline 과 비교하여 역산. 본 P5 report 의 §2 는 Phase 7 재측정 결과를 기다리는 placeholder.
- **임계**: 정량 임계 없음. 질적 flag (flip 발생 시 Phase 7 report 에서 원인 분석 의무).

### S2 — One-way movement (질적)
- **정의**: v3 신규 24개 쿼리가 **특정 모델에 체계적으로 유리한 방향 bias** 를 가지는지 질적 분석. 예: BGE-M3 강점 (long-form 한국어) 에만 유리한 쿼리 / Upstage 강점 (짧은 keyword) 에만 유리한 쿼리.
- **측정 방법**: v3 신규 24 쿼리를 수작업 분류 (query 길이, heading_trail depth, axis 전문성 등) → 각 모델의 예상 유불리 대칭성 판정.
- **임계**: 정량 임계 없음. 비대칭 bias 발견 시 보고.

### S3 — 실패 쿼리 bias (**임계 50%**)
- **정의**: Phase 3 의 17 실패 쿼리 (source: `phase3_failure_analysis.md` §5) 의 토큰 집합과 v3 신규 24 쿼리의 토큰 집합 간 Jaccard 유사도 J.
- **측정**:
  - 각 v3 신규 쿼리 q_new 에 대해: max over 17 failures `J(tokens(q_new), tokens(f_i))` 를 계산.
  - 전체 신규 24 쿼리 중 **max-J 값이 0.50 을 초과하는 쿼리 비율** 을 S3 metric 으로 채택.
- **임계**: **S3 > 50% → blocking flag**.
- **해석**: v3 신규 쿼리가 실패 쿼리와 과도히 유사하면 → query set 이 "실패 재현 대응 전용" 으로 설계된 의혹 (test-set leak 변종).

### S4 — Oracle 겹침 (**임계 30%**)
- **정의**: v3 신규 primary chunk_ids (= N1~N9 cross + Q+15 requirements/application/definitions = 약 72 chunks) 중 **Phase 3 top-5 에 이미 hit 한 적 있는 chunk** 의 비율.
- **측정**:
  - v3 신규 primary chunk_ids 집합 `C_new`
  - Phase 3 top-5 에 등장한 chunk 집합 `C_top5 = ⋃ over 3 models, over all queries, top-5 hits`
  - `overlap_rate = |C_new ∩ C_top5| / |C_new|`
- **임계**: **overlap_rate > 30% → blocking flag**.
- **해석**: v3 신규 primary 가 Phase 3 결과에 이미 많이 포함되어 있으면 → 새로운 retrieval challenge 가 부족 (test-set 강화 효과 저하).

### 임계 고정 정책
**50% / 30% 임계 는 Phase 4 P0 기간 동안 고정**. 임계 조정 제안은 Phase 9 (task#8) retrospective agenda 로 이관. P5 에서 임계 아래쪽으로 완화하는 것은 blocking flag 회피 동기 의혹 발생 — 금지.

---

## §3. Tokenization 스펙 (DR-4 §검증 절차와 완전 동일)

### 정책
1. **공백 split** (split by ASCII whitespace) — 형태소 분석 미적용.
2. **영문/숫자 lowercase** — e.g., "ISA 500" → "isa", "500".
3. **Stopword 제거** (17 항목, 아래 목록).
4. **구두점 처리**: 공백 split 전 `[?!.,;:]` 단독 제거 (단어 끝/시작 붙은 경우만). 예: "입수하는가?" → "입수하는가". 단 "(i)" 같은 식별자는 단일 토큰 유지.

### Stopword 리스트 (DR-4 §검증 절차 복사, 17 항목)

```python
STOPWORDS = frozenset({
    "의", "은", "는", "이", "가", "에", "와", "과", "을", "를",
    "수", "등", "및", "한", "한다", "있다", "하는",
})
```

**일치성 검증 assert**: retrofit_audit.py 실행 시 query_design_rules.md 의 STOPWORDS 리스트 SHA 와 일치 여부를 assert. 불일치 시 abort.

### 토큰화 함수 시그니처 (Python pseudo-code)

```python
def tokenize(text: str) -> list[str]:
    """Strict surface-form tokenizer (DR-4 공유)."""
    # 1. lowercase
    s = text.lower()
    # 2. trailing/leading punctuation strip
    tokens = [t.strip(".?!,;:") for t in s.split()]
    # 3. empty + stopword 제거
    return [t for t in tokens if t and t not in STOPWORDS]
```

**설계 제약**:
- 한국어 조사는 strip 대상 아님 (e.g., "감사인은" 은 그대로 1 토큰). DR-4 의 strict surface form 정책 그대로.
- 활용형 변이 병합 (e.g., "입수하는가" ≡ "입수한다") **미적용**. P3 재평가 ticket (2026-04-19 DE N2 spot-check 발견) 에서 별도 논의.

---

## §4. Jaccard 유사도 + 검증 Assertions

### 수식

J(A, B) = |A ∩ B| / |A ∪ B|, 단 A ∪ B ≠ ∅.

### Edge case
- `|A ∪ B| == 0` (양쪽 빈 집합): J 는 **1.0 으로 정의** (identity by convention, two empty sets are identical). retrofit_audit 에서 양쪽 빈 토큰 집합은 실무상 발생 불가 (쿼리는 최소 3 토큰 이상) 이나 assert 로 방어.
- `|A| == 0, |B| > 0`: J = 0.0.

### 검증 assertions (Python pseudo-code)

```python
def jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    if not union:
        return 1.0  # both empty, identity
    return len(a & b) / len(union)

# Self-test assertions (run once at import or in test suite):
assert jaccard(set(), set()) == 1.0
assert jaccard({"a"}, set()) == 0.0
assert jaccard({"a", "b"}, {"a", "b"}) == 1.0
assert abs(jaccard({"a", "b", "c"}, {"b", "c", "d"}) - 0.5) < 1e-9
```

---

## §5. Cross vs Non-Cross Breakdown 아키텍처

**(파일 구조 inspection pending — `.work/eval_v2_*.json` schema 확인 후 완성)**

### 설계 의도
v3 신규 24 쿼리 = cross-standard 9 (N1~N9) + requirements +5 + application +5 + definitions +5 = 24. S3/S4 signal 을 **전체 (24)** 와 **cross-only (9)** + **non-cross (15)** 로 breakdown 하여 cross-standard 설계의 고유 bias 여부를 분리 측정.

### 출력 구조 (draft)

```markdown
## §4. S3 실패 쿼리 bias

| 집합 | 신규 쿼리 수 | max-J > 0.50 쿼리 수 | S3 비율 | 판정 |
|---|---:|---:|---:|---|
| 전체 v3 신규 | 24 | ? | ?% | PASS/FAIL |
| Cross-standard (N1~N9) | 9 | ? | ?% | PASS/FAIL |
| Non-cross (Q+15) | 15 | ? | ?% | PASS/FAIL |

## §5. S4 Oracle 겹침 (per-model)

| 집합 \ Model | BGE-ON | BGE-OFF | Upstage | 판정 |
|---|---:|---:|---:|---|
| 전체 v3 primary | ?% | ?% | ?% | PASS/FAIL |
| Cross-standard primary | ?% | ?% | ?% | PASS/FAIL |
| Non-cross primary | ?% | ?% | ?% | PASS/FAIL |
```

**Blocking 로직**: 임의 cell 의 % 가 S3 50% / S4 30% 임계 초과 시 전체 판정 FAIL + blocking flag 발행. 서브집합이 PASS 이고 전체가 FAIL 이면 → 원인을 §10 Appendix 에 기록.

---

## §6. Monitored Diagnostics (Pair Proximity + Cross-Overlap + Enhanced Queries)

Cross-standard 9 oracle 설계 과정에서 발견된 3 종류 관찰 항목을 single CLI 플래그 (`--diagnostic-monitored`) 로 일괄 보고. §6.1 은 pair proximity, §6.2 는 role-based cross-query overlap, §6.3 은 DR-6 (P3 조항화 예정) 의 query enhancement 효과 tracking.

### §6.1. Pair Proximity Diagnostic (P-1, P-2)

#### 대상
- **P-1** (within-oracle parent-child): 단일 oracle 내 parent-child heading cluster ¶ pair. **Schema reserved — 현재 해당 case 없음** (2026-04-19 DE Clarification 2 확정: N1/N2/…/N9 9 oracle 의 primaries 모두 서로 다른 ISA 로 구성되어 within-oracle parent-child pair 부재). P3 확장 (requirements +5 / application +5 / definitions +5) 시점 발생 가능성 대비 schema 유지.
- **P-2** (cross-oracle adjacent ¶): N2 §22 ↔ N3 §23 ISA 315 인접 ¶ pair (2026-04-19 DE spot-check 확인).

#### Schema (JSON)

```json
{
  "pair_id": "P-2",
  "oracles": ["N2", "N3"],
  "isa": "315",
  "paragraph_distance": 1,
  "block_ordinal_distance": 3,
  "section_A": "requirements",
  "section_B": "requirements",
  "heading_prefix_depth": 3,
  "proximity_subtype": "cross-oracle adjacent",
  "retrieval_stats": {
    "N2_query_top5_includes_N3_chunk": "count/3_models",
    "N3_query_top5_includes_N2_chunk": "count/3_models"
  }
}
```

#### 측정 항목
**retrieval confusion rate** = (상대 oracle chunk 가 자기 쿼리 top-5 에 들어온 횟수) / (3 models × per-pair). 높으면 proximity artefact.

### §6.2. Cross-Oracle Primary-vs-Related Overlap

#### 배경
동일 chunk 가 한 oracle 의 `expected_related_chunks` 에, 다른 oracle 의 `expected_primary_chunks` 에 이중 등록되는 경우 (role 분리). DR-5(b) 는 primary disjoint 만 규정하므로 **형식 위반 없음** 이나 P5 diagnostic 대상.

#### 1st instance (2026-04-19 DA 발견)
- chunk: `315:02498:27`
- role A: Q29 (N3) `expected_related_chunks` 중 하나
- role B: Q32 (N6) `expected_primary_chunks` 중 하나

#### Schema (JSON)

```json
{
  "overlap_id": "O-1",
  "chunk_id": "315:02498:27",
  "source_oracle": "N3",
  "source_role": "related",
  "target_oracle": "N6",
  "target_role": "primary",
  "overlap_subtype": "cross-oracle primary-vs-related",
  "retrieval_stats": {
    "source_query_top5_includes_chunk": "count/3_models",
    "target_query_top5_includes_chunk": "count/3_models"
  }
}
```

#### 측정 항목
**dual-role hit rate** = (source 쿼리 top-5 + target 쿼리 top-5 에 동시에 등장한 비율). 높으면 cross-query contamination 지표.

### §6.3. Enhanced Queries Performance Tracking (DR-6 precedent)

#### 배경
DR-6 (P3 조항화 예정) — query enhancement 허용 기준: DR-4 ∩ pre-estimate ∈ {2, 3} 임계 zone 에서 DA 2-test (axis-확장 / 자연 phrasing / 보강 token 출처) 통과 시 쿼리 보강 허용. evidence block `notes` yaml 에 `enhanced: true` + `enhanced_intersection_post_query_expansion: N` 컬럼 기록.

#### 1st precedent (2026-04-19 N3 Q29)
- query_id: Q29
- enhanced target chunk: `315:02485:23`
- pre-estimate ∩: 3
- post-enhancement ∩: 4 (DE 사전 측정 값)
- enhancement type: axis expansion (추가 phrase "어느 수준에서 식별·평가")

#### Schema (JSON)

```json
{
  "enhancement_id": "E-1",
  "query_id": "Q29",
  "oracle": "N3",
  "enhanced_primary_chunk_id": "315:02485:23",
  "pre_estimate_intersection": 3,
  "post_enhancement_intersection_declared": 4,
  "post_enhancement_intersection_measured": null,
  "enhancement_type": "axis_expansion",
  "da_2test_passed": true,
  "retrieval_stats": {
    "enhanced_query_top5_includes_target": "count/3_models",
    "baseline_query_top5_includes_target": "count/3_models_synthetic_if_available"
  }
}
```

#### 측정 항목
1. **Declared vs measured ∩ 정합성**: yaml `enhanced_intersection_post_query_expansion` 값이 retrofit_audit tokenizer 로 재계산한 실측 ∩ 값과 일치하는지 assert. 불일치 시 notes 수정 요청.
2. **Enhancement lift**: enhanced query 의 top-5 recall 이 baseline 대비 증가했는지 (baseline 은 enhancement 적용 전 쿼리 문자열이 eval 기록에 있는 경우에만 측정 가능 — Phase 3 는 enhancement 적용 전이므로 baseline=v2 에 해당 쿼리가 존재하지 않음. **limitation**: Phase 7 재측정 v3 결과만으로는 lift 계산 불가, 별도 baseline run 필요. Phase 7 결과에 "enhancement lift 측정 deferred" flag.)

### CLI 플래그
`audit-parser retrofit-audit --diagnostic-monitored` 로 §6.1/§6.2/§6.3 일괄 활성화. 과거 `--diagnostic-proximity` 는 deprecated alias (§6.1 만 활성화하는 하위 호환 모드).

---

## §7. Obs-3 Parser Limitation 입력 지점

### 배경
701:8444:9 본문 "문단9에 따라 결정된 사항 중..." 의 "문단9" cross-ref 가 현재 parser 에서 `refs=["A9"]` 만 추출되고 본문 inline "문단N" pattern 은 미추출. 발견: 2026-04-19 DE N6 pre-flight.

### P5 에서의 역할
- **Diagnostic 출력**: retrofit_audit §7 에 "inline para-ref 파싱 누락으로 인한 recall 저해 추정" 섹션 추가. 701:9 retrieval 성능이 inline "문단9" 파싱 전제 하에서는 더 높아야 했을 가능성 기록.
- **Scope 분리**: parser 수정 자체는 P5 scope 외 (P6 candidate). P5 는 영향 범위 식별 + 영향 받는 chunk 목록 제출.
- **식별 방법**: `grep -P "문단\s*\d+" data/chunks.jsonl` 로 전수 추출 후 oracle primary 와 교집합 산출.

---

## §8. N5 Axis-Weak False-Positive Tracking

### 배경
N5 (계속기업 trilogy) 의 3 primary 중 `705:08691:21` 은 axis 약 (705 본문에 "계속기업" 0건). N5 narrative 는 modification consequence chain 으로만 705:21 을 수용. 

### P5 에서의 측정
- **Target chunk**: 705:08691:21
- **Measure**: Non-N5 쿼리 (= N5 외 23 쿼리) 의 top-5 에 705:21 이 hit 한 횟수 / 3 models × 23 쿼리 = 69 opportunities.
- **해석**:
  - 높음 (e.g., >10%) → 705:21 이 KAM/modification cluster chunk 로 기능. N5 의 primary 선정이 proximity artefact 가능성.
  - 낮음 (<5%) → 705:21 이 N5 narrative-only 에 fit. structural limitation 수용 정당화.

### 출력
retrofit_audit §8 에 count table + judgment.

---

## §9. 재현 명세

### 입력 파일 경로 (절대)
- queries.yaml: `/home/shin/Home/_AuditStandards_parsing/docs/eval/queries.yaml`
- eval results: `/home/shin/Home/_AuditStandards_parsing/.work/eval_v2_{bge_on,bge_off,upstage_on}.json`
- phase3_failure_analysis.md: `/home/shin/Home/_AuditStandards_parsing/docs/eval/phase3_failure_analysis.md`
- chunks.jsonl: `/home/shin/Home/_AuditStandards_parsing/data/chunks.jsonl` (경로 확인 pending)

### Seed
- 해당 없음 (deterministic 집합 연산).

### 실행 명령 (예시)
```bash
python scripts/retrofit_audit.py \
  --queries docs/eval/queries.yaml \
  --eval-bge-on .work/eval_v2_bge_on.json \
  --eval-bge-off .work/eval_v2_bge_off.json \
  --eval-upstage .work/eval_v2_upstage_on.json \
  --failures docs/eval/phase3_failure_analysis.md \
  --chunks data/chunks.jsonl \
  --output docs/eval/phase4_p0_retrofit_audit.md \
  --diagnostic-proximity \
  --threshold-s3 0.50 \
  --threshold-s4 0.30
```

### 재현성 체크리스트
- [ ] 입력 파일 SHA-256 기록 (출력 §1 에 삽입)
- [ ] retrofit_audit.py git commit SHA 기록
- [ ] Python interpreter version 기록
- [ ] STOPWORDS SHA assert (DR-4 와 일치)

---

## §10. Appendix — Output Format Schema

### `docs/eval/phase4_p0_retrofit_audit.md` 본문 schema
§1 에서 기술한 10 섹션 구조 준수. 각 섹션은 **정량 table + 판정 1줄 + 근거 bullet 목록** 의 3단 구조.

### Blocking flag 발행 형식
FAIL 발생 시 report 상단 (meta frontmatter 바로 아래) 에 다음 블록 삽입:

```markdown
> [!WARNING] **BLOCKING FLAG — Phase 2/3 rework 요청**
>
> - 위반 signal: S3 (threshold 50%, measured X%) / S4 (threshold 30%, measured Y%)
> - 영향: P7 (task#6) 차단
> - 권고 조치: queries.yaml v3 의 T 쿼리 재설계 (list 포함) + Phase 3 재실행 여부 판단
> - Lead 통보: 본 report commit push 후 15분 이내 team lead 앞 SendMessage
```

### PASS 시 서명 형식
§9 하단에 inline:

```markdown
### Signoff
- signed: audit-domain-expert 2026-MM-DD HH:MM (peer review PASS)
- signed: planner 2026-MM-DD HH:MM (methodology PASS)
- signed: devils-advocate 2026-MM-DD HH:MM (DA 주도 작성, self-audit PASS)
```

3 서명 완료 후 task#6 (P7 3축 재측정) unblock.

---

## §11. TODO Markers (implementation 단계 처리)

- [ ] `.work/eval_v2_*.json` per-query schema 확인 (§5 breakdown 로직 finalize 선행).
- [ ] `data/chunks.jsonl` 경로/존재 확인 (§7 / §8 grep 전제).
- [ ] phase3_failure_analysis.md §5 의 17 failures 정확한 query_id + token 추출 (코드 내 하드코딩 vs 파일 parse 방식 선택).
- [ ] STOPWORDS SHA 일치 assert 로직 구현 (query_design_rules.md 에서 동적 추출 vs 스크립트 내 mirror).
- [ ] queries.yaml v3 merge 후 cross-oracle adjacent pair (P-2) 외 추가 monitored pair 발견 여부 재확인.
- [x] §6.1 P-1 schema reserved 확정 — no current case (2026-04-19 DE Clarification 2, N1~N9 전수 검증 완료). P3 확장 시 재검토.
- [ ] §6.2 cross-oracle primary-vs-related overlap list finalize (N4/N5/N6 evidence 완성 후 전수 스캔).
- [ ] §6.3 enhanced queries lift 측정 불가 (baseline 부재) 대안 — Phase 7 재측정 시 enhanced vs "plan §4.2 원안 unchanged" 쿼리 간 top-5 recall 비교를 lift proxy 로 제안.
- [ ] S3/S4 cell 임계 초과 시 blocking flag → lead 통보 자동 SendMessage 포함 여부 (현재는 수동).

---

## §12. Peer Review 요청 범위 (design 단계)

본 design skeleton 에 대한 peer review 항목 (task#5 open 이전 lead/DE 에 1회 요청):

1. **§1 inputs 완전성**: 누락된 입력 소스 있는지 (예: monitored pair JSON 입력 기대 시).
2. **§2 임계 정책**: 50% / 30% 고정 선언이 P0 signoff 조건과 부합하는지.
3. **§3 tokenization**: DR-4 복제본이 정확한지 (stopword 17 항목, 공백 split, lowercase).
4. **§5 breakdown 축**: cross vs non-cross 외 축 (예: ISA 간 거리, heading depth) 추가 필요성.
5. **§6 monitored pair schema**: DE 원안 + DA 보강 수용 여부 재확인.
6. **§7 / §8 diagnostic scope**: P5 범위에 적절한지 (P6 로 이관 제안 시 분리 방안).
7. **§10 blocking flag 문안**: 문구 수정 제안.

**Peer review timing**: DA 의 N3/N5/N6 spot-check 완료 + task#2 close 직후. 본 design 파일 git commit 은 Commit 4 (task#5 close 시) 가 아닌 별도 사전 commit (design-only) 로 lead 와 별도 조율.
