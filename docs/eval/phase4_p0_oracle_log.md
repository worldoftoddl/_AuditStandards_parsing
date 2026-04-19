# Phase 4 P0 — Oracle Evidence Log (DRAFT)

> 담당: `audit-domain-expert`
> 적용 phase: Phase 4 P0 oracle 작성 (queries.yaml v3 의 신규 24 쿼리 Q27-Q50)
> 출력 사용처: P4 단계에서 본 evidence block 을 `docs/eval/queries.yaml` v3 로
> merge.

## STATUS: DRAFT — N1 pilot pass, N2 착수 OK (DA 최종 서명 2026-04-19)

본 문서는 lead 승인 N1-N3 pilot scope (대화 ID `phase4-p0-query-expansion-v2`,
2026-04-19) 안의 oracle 초안만 포함한다. **`queries.yaml` 직접 편집 P4 까지
금지**. N4-N9 / Q36-Q50 는 N1-N3 검증 + lead 승인 후 별도 진행.

**DR 서명 상태**: `query_design_rules.md` NIT-N4 + NIT-N6 + NIT-N1 반영 후
DA 조건부 → 최종 서명 (2026-04-19). N1 advisory pass (DA spot-check),
S4 prescreen 2/3 IN 초기 신호 기록 (24 신규 primary 전체 대비 P2/P3 완료
시점에 trip 임계 30% 산정).

### Pilot 조건 (lead 승인, 2026-04-19)
1. ✓ Scope: N1-N3 only (N4-N9 건드리지 않음) → **승격: N1-N9 전체** (lead
   2026-04-19 N7/N9 배치 승인, N8 우선 small-ISA 검증 후)
2. ✓ Draft-only: `oracle_log.md` 에만 작성. `queries.yaml` 편집 금지.
3. ✓ DR change = rework 선언: NIT-N4 반영 / worked example 표면형 정정은
   DR 본문 수정이 아니라 evidence-가능성 보강이므로 N1-N3 본문 작성 0건
   상태에서 rework 트리거 아님.
4. ✓ DA incremental sharing: N1 → DA spot-check → reaction → N2 → ... 순차.
5. ✓ **Cross-reference 의무 (DE↔DA 쌍대 학습, 2026-04-19)**: plan §4.2 후보
   ↔ chunks.jsonl 실측 ↔ (cross 쿼리일 때) 기 작성 cross oracle primary
   union 3중 교차 확인 후 yaml block 작성. P2 cross-cutting §overlap
   검증이 본 템플릿의 첫 instance. P3 전파 판단은 P2 pilot 결과 후 lead
   제안.

### 5 DR 체크리스트 (각 oracle 마지막)
체크리스트는 `docs/eval/query_design_rules.md:421-446` 포맷 사용.
✗ 1건 이상이면 lead 보고 + DR 회피/재설계.

---

## Q27 — N1: 충분·적합한 감사증거 ↔ 추가감사절차 ↔ 왜곡표시 커뮤니케이션 (500↔330↔450)

```yaml
id: Q27
category: cross-standard
query: "감사인은 충분하고 적합한 감사증거를 어떻게 입수하고, 식별된 왜곡표시를 경영진과 커뮤니케이션하는가?"
expected_primary_chunks:
  - "500:04351:6"
  - "330:03681:7"
  - "450:04218:8"
expected_related_chunks:
  - "500:04353:7"   # 감사절차 설계·수행 시 고려사항 (요구사항 ¶7)
  - "330:03683:8"   # 추가감사절차의 성격·시기·범위 (요구사항 ¶8)
  - "450:04211:5"   # 왜곡표시 집계 (요구사항 ¶5, 왜곡표시 chain 시작)
  - "450:04221:10"  # 미수정왜곡표시 영향 평가 (요구사항 ¶10)
notes: |
  Cross-standard "감사증거 chain" 축. 500 (요구사항 일반) →
  330 (RMM 대응 절차) → 450 (식별된 왜곡표시 처리) 의 evidence 흐름.
  DR-4 시 330:7 framing gap 존재 (intentional, 아래 §DR-4 mini-table 참조).
```

### Evidence — chunks.jsonl 원문 (3 primary)

```jsonl
# Primary 1 — 500:04351:6 (요구사항, char_count=115)
chunk_id="500:04351:6"  isa_no=500  section=requirements  block_ordinal=4351
heading_trail=[
  "감사기준서 500  감사증거",
  "요구사항",
  "충분하고 적합한 감사증거"
]
paragraph_ids=["6"]
text="감사기준서 500  감사증거 > 요구사항 > 충분하고 적합한 감사증거\n\n
      6. 감사인은 충분하고 적합한 감사증거를 입수하기 위하여 상황에 적합한
      감사절차를 설계하고 수행하여야 한다. (문단 A5-A29 참조)"
refs=["A5".."A29"]   # 25개 application 지시
```

```jsonl
# Primary 2 — 330:03681:7 (요구사항, char_count=116)
chunk_id="330:03681:7"  isa_no=330  section=requirements  block_ordinal=3681
heading_trail=[
  "감사기준서 330  평가된 위험에 대한 감사인의 대응",
  "요구사항",
  "경영진주장 수준의 평가된 중요왜곡표시위험에 대응한 감사절차"
]
paragraph_ids=["7"]
text="감사기준서 330  평가된 위험에 대한 감사인의 대응 > 요구사항 >
      경영진주장 수준의 평가된 중요왜곡표시위험에 대응한 감사절차\n\n
      7. 감사인은 수행될 추가감사절차를 설계할 때, 다음 사항에 유의하여야 한다."
refs=[]   # 후속 (a)/(b) sub-item (block_ordinal 3682+) 으로 연계
```

```jsonl
# Primary 3 — 450:04218:8 (요구사항, char_count=184)
chunk_id="450:04218:8"  isa_no=450  section=requirements  block_ordinal=4218
heading_trail=[
  "감사기준서 450  감사 중 식별된 왜곡표시의 평가",
  "요구사항",
  "왜곡표시의 커뮤니케이션과 수정"
]
paragraph_ids=["8"]
text="감사기준서 450  감사 중 식별된 왜곡표시의 평가 > 요구사항 >
      왜곡표시의 커뮤니케이션과 수정\n\n
      8. 감사인은 법규상 금지되지 않는 한 감사 중 집계한 모든 왜곡표시에
      대하여 적합한 수준의 경영진과 적시에 커뮤니케이션하여야 한다.
      감사인은 경영진에게 이러한 왜곡표시를 수정할 것을 요청하여야 한다.
      (문단 A10-A12 참조)"
refs=["A10","A11","A12"]
```

### DR-1 — Intro-parent stub 검증 (NIT-N1 임계 ≤ 115)

| primary chunk_id | char_count | section | paragraph_ids | 본문 패턴 | stub? |
|---|---:|---|---|---|---|
| 500:04351:6 | 115 | requirements | ["6"] | "...감사증거를 입수하기 위하여 상황에 적합한 감사절차를..." | ✗ |
| 330:03681:7 | 116 | requirements | ["7"] | "...추가감사절차를 설계할 때, 다음 사항에 유의하여야 한다." | ✗ |
| 450:04218:8 | 184 | requirements | ["8"] | "...집계한 모든 왜곡표시에 대하여 적합한 수준의 경영진과..." | ✗ |

**판정**:
- 500:04351:6 cc=115 는 NIT-N1 신규 임계 (`≤ 115`) 의 경계 케이스. 단 DR-1
  §판정 기준 3번 (`section ∈ {definitions, objective, intro}` + paragraph_ids
  단일 숫자) 의 section 조건을 requirements 여서 불충족 → stub 아님.
- 330:03681:7 / 450:04218:8: char_count > 115 이면서 body 패턴 stub 아님 → ✗.
- 3건 모두 `"...는 다음과 같다."` 종결 패턴 없음.

→ DR-1 ✓ (3 primary 모두 non-stub).

(주의: 330:7 본문이 "다음 사항에 유의하여야 한다." 로 끝나며, 후속 sub-item
(a)/(b) 분산 구조이지만, DR-1 의 stub 정의는 "본문이 '다음과 같다' 로
종결되는 정의/목적 인트로" 에 한정. 330:7 은 절차적 요구사항으로 본문
116자에 의미 있는 substantive content 포함 → stub 아님.)

### DR-2 — Resolver 매핑 로그 (logical path 미사용)

본 oracle 의 3 primary 모두 **concrete chunk_id** 직접 지정 (`{isa}:{ordinal}:{paragraph_id}`
형태). logical path (`{isa}:{N}.(x)`) 사용 0건 → resolver 호출 없음 →
mini-table N/A. DR-2 ✓ (vacuously satisfied).

### DR-3 — Alphabetical (i) vs Roman (i) 모호성 검증

3 primary 의 paragraph_ids 모두 numeric (`["6"]`, `["7"]`, `["8"]`). `(i)`
sub-item 인용 0건. DR-3 ✓.

### DR-4 — Query phrasing ↔ primary framing 정합 (NIT-N4 정량)

**쿼리 표면형 토큰** (공백 split, stopword 후):
```text
["감사인은", "충분하고", "적합한", "감사증거를", "어떻게", "입수하고,",
 "식별된", "왜곡표시를", "경영진과", "커뮤니케이션하는가?"]
```
(stopword 매칭 0건 — 모두 agglutinated surface form)

**Primary mini-table** (각 primary top-20 ∩ query, strict surface-form):

| primary chunk_id | primary top-20 (요약) | 교집합 | 일치 (≥2) |
|---|---|---|---|
| 500:04351:6 | 적합한(3), 감사증거(2), 충분하고(2), >(2), 감사기준서, 500, 요구사항, 감사증거를, 6., 감사인은, 입수하기, 위하여, 상황에, 감사절차를, 설계하고, 수행하여야, 한다., (문단, A5-A29, 참조) | {감사인은, 충분하고, 적합한, 감사증거를} = 4 | ✓ |
| 330:03681:7 | 평가된(2), >(2), 감사기준서, 330, 위험에, 대한, 감사인의, 대응, 요구사항, 경영진주장, 수준의, 중요왜곡표시위험에, 대응한, 감사절차, 7., 감사인은, 수행될, 추가감사절차를, 설계할, 때, | {감사인은} = 1 | ✗ → (c) |
| 450:04218:8 | 감사인은(2), 감사(2), 중(2), 왜곡표시의(2), >(2), 한다.(2), 감사기준서, 450, 식별된, 평가, 요구사항, 커뮤니케이션과, 수정, 8., 법규상, 금지되지, 않는, 집계한, 모든, 왜곡표시에 | {감사인은, 식별된} = 2 | ✓ |

**(c) intentional gap 사유 — 330:03681:7**:
330:7 본문은 "감사인은 수행될 추가감사절차를 설계할 때, 다음 사항에 유의하여야
한다." 로, 후속 sub-item (a)/(b) 에 구체 유의사항 분산. 자연어 cross-standard
쿼리가 "추가감사절차" 어휘를 직접 인용하는 것은:
- (i) 모델 retrieval 에 명시적 단어 매칭 인플레이션 위험 (Phase 5 S2 one-way
  movement signal 트립 가능성),
- (ii) 쿼리가 ISA 별 본문 어휘를 모두 명시하는 paraphrase 가 되어 cross-link
  retrieval 능력 측정 본질을 훼손.

→ DR-5 (3 ISA primary 강제) 우선 trade-off 인정. 330:7 의 framing gap 은
intentional 로 분류 (DR-4 (c)). cross-standard category 의 (c) 누적 비율은
P5 S3 audit 에서 정량 측정 (`query_design_rules.md:318` "30% 초과 시 lead
보고" 임계 적용). 본 oracle 1건의 (c) 는 누적 1/9 = 11% 로 임계 미달.

### DR-5(a) — Cross-standard primary ISA ≥ 2

| primary chunk_id | isa_no |
|---|---|
| 500:04351:6 | 500 |
| 330:03681:7 | 330 |
| 450:04218:8 | 450 |

unique ISAs = {500, 330, 450} = **3 개** → DR-5(a) ✓ (≥ 2 만족, 강한 cross 신호).

### DR-5(b) — Cross 쿼리 간 primary disjoint (NIT-N6)

본 N1 = 첫 번째 작성 cross oracle. 다른 P2 cross 쿼리 (N2~N9, Q28~Q35) 미작성
상태이므로 disjoint 검증은 vacuously true. **N2 작성 시점에 N2 primary 와
{500:04351:6, 330:03681:7, 450:04218:8} 의 차집합 확인 절차** 수행 필요.
plan §4.2 사전 검증으로 N2 후보 (402:9, 315:12, 330:12) 가 N1 primary 3건과
disjoint 임을 미리 확인 — `330:12` ≠ `330:03681:7` (concrete chunk_id 다름)
→ disjoint 보장.

### DR 체크리스트

```text
[✓] DR-1 — Intro-parent stub 없음
    근거: 3 primary 모두 char_count > 115 (NIT-N1 임계 상향) + 본문 substantive
[✓] DR-2 — Resolver 매핑 로그 첨부
    근거: 모든 primary concrete chunk_id 직접 지정, logical path 미사용 (N/A)
[✓] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: paragraph_ids 모두 numeric ["6"]/["7"]/["8"]
[부분✗] DR-4 — Query phrasing ↔ primary framing 일치
    근거: 500:6, 450:8 ✓ (각 4, 2 교집합); 330:7 ✗ → (c) intentional gap
    (DR-5(a) 우선 trade-off, notes 정당화 + P5 S3 audit 모니터)
[✓] DR-5(a) (cross) — primary ISA 수 ≥ 2
    근거: unique ISAs = {500, 330, 450} = 3
[✓] DR-5(b) (cross, NIT-N6) — 다른 cross 와 primary disjoint
    근거: N1 = 첫 번째 cross. 후속 N2~N9 작성 시 disjoint 확인 절차 수행
```

→ 6 항목 중 5 ✓ + 1 (c) intentional. lead 보고 trigger 임계 (cross-standard
누적 (c) > 30%) 미달 (1/9 = 11%) — 본 oracle 채택 가능.

### (b) 330:5 대체 검토 결과 (DA spot-check §1 회신, 2026-04-19)

DA가 (b) "330:5 (전반적 대응) 1회 검토 후 (c) 유지/변경" 요청. 실측:

- **330:5 본문**: "감사인은 재무제표 수준의 평가된 중요왜곡표시위험에 대처하기
  위한 전반적인 대응을 설계하고 실행하여야 한다." (cc=124)
- **330:5 top-20** (strict surface form, freq desc): 평가된(2), 대응(2),
  전반적인(2), >(2), 감사기준서, 330, 위험에, 대한, 감사인의, 요구사항, 5.,
  감사인은, 재무제표, 수준의, 중요왜곡표시위험에, 대처하기, 위한, 대응을,
  설계하고, 실행하여야
- **Query ∩ 330:5 top-20**: {감사인은} = 1 → 교집합 < 2, **(c) 동일**.

추가로 330:5 는 "전반적 대응" (재무제표 수준, 추상화 한 단계 위) 으로
"감사증거 입수 → 추가감사절차" 흐름과 framing gap 이 330:7 ("추가감사절차
설계할 때") 보다 더 큼. semantic 측면에서도 330:7 우위.

**결정**: (b) 미수행, **(c) 330:7 primary 유지**. DA spot-check §1 종결.

### 평가 수행 지침 (P4 merge 시점)

1. resolver smoke (`eval-run --queries-only`) 에서 본 3 primary 모두
   `unresolved_paths` 0 확인.
2. P5 S3 audit 입력 으로 본 쿼리 토큰 + Phase 3 17 실패 쿼리 토큰 Jaccard
   계산. ≥ 0.3 시 retrofit 의심 신호.
3. P7 재측정 시 본 쿼리의 BGE/UPS recall@5 → top-5 중 330:7 회수 여부 별도
   체크 ((c) intentional 의 실측 영향 검증).

---

## P2 cross-cutting — N7/N9 overlap 검증 (lead 지시, 2026-04-19)

DA N1 spot-check §0 (그리고 사전 NIT-N6 motivation) 에서 "N7(250:22, 240:22) ∩
N9(550:18, 240:22) = 240:22 공유" 라고 기재했으나, plan §4.2 line 90 원본은
N9 = `550:18, 240:24` (NOT 240:22). lead 가 240:24 → 240:22 misread 가능성
지적, P2 entry 첫 작업으로 실측 확인 지시.

**chunks.jsonl 실측** (각 grep, 1줄 단일 매칭):

| 후보 | 실측 chunk_id | block_ordinal | 본문 핵심 |
|---|---|---:|---|
| N7-A 250:22 | `250:01628:22` | 1628 | 법규위반 시사점 평가, 적절한 조치 |
| N7-B 240:22 | `240:01098:22` | 1098 | 지배기구의 부정 인지 여부 질문 |
| N9-A 550:18 | `550:06012:18` | 6012 | 특수관계자 RMM 식별/평가, 유의적 위험 |
| N9-B 240:24 | `240:01102:24` | 1102 | 기타정보가 부정으로 인한 RMM 시사 여부 |

**결론**: `240:01098:22` ≠ `240:01102:24` (paragraph_id `22` vs `24`,
block_ordinal 1098 vs 1102). N7 ∩ N9 = ∅. **Phantom overlap 확정**.

**조치**:
- N7 = (250:22, 240:22), N9 = (550:18, 240:24) plan §4.2 원본대로 유지.
- Primary 교체 작업 불필요.
- DR-5(b) (`query_design_rules.md` line 381-405) 는 prophylactic design rule
  로 유효 — 실제 오버랩이 아닌 "미래 cross 쿼리 누적 시 dual-counting 차단"
  근거. DA 에게 DR-5(b) §motivating example 의 N9 `240:22` 기재를
  "phantom example, 실측 후 240:24 plan 원본 유효 확인" 노트 추가 권고.
- 향후 N7, N9 oracle 작성 시 본 표를 base 로 chunks.jsonl 본문 인용.

---

## Q34 — N8: 지배기구 소통 ↔ 내부통제 미비점 (260↔265)

**lead 우선순위 (small-ISA 위험 1순위 검증)**: plan §4.2 line 92 "N5/N8만 작은
ISA 포함 → Phase 2 우선 검증". `260:16` plan 명시 → 실측은 paragraph_id "2"
파싱 (block_ordinal 1824, "16" 가설 이상). **observation 기록은 §P0
post-close follow-up 섹션 참조** — chunker 수정은 P0 PR freeze 외.

```yaml
id: Q34
category: cross-standard
query: "감사인은 지배기구에게 감사에서의 유의적 발견사항을 어떻게 커뮤니케이션하며, 식별된 유의적 내부통제 미비점은 어떤 형식으로 보고해야 하는가?"
expected_primary_chunks:
  - "260:01824:2"
  - "265:02105:9"
expected_related_chunks:
  - "260:01825:(a)"   # 회계실무 유의적 질적 측면 견해
  - "260:01826:(b)"   # 감사 중 직면한 유의적 어려움
  - "260:01827:(c)"   # 경영진과의 유의적 사항/서면진술
  - "260:01830:(d)"   # 감사보고서 형태/내용 영향 상황
  - "260:01831:(e)"   # 기타 재무보고절차 감시 관련 사항
  - "260:01839:18"    # 커뮤니케이션 형태·시기·내용 절차 수립
notes: |
  Cross-standard "지배기구 커뮤니케이션 chain" 축. 260 (모든 발견사항
  parent + 5 sub-item 형식) → 265 (특정 미비점 서면 형식 강제) 의 흐름.
  N1 axis (감사증거) 와 disjoint. small-ISA (265) 포함 → Phase 7 재측정 시
  Upstage 95-row index 커버리지 pre-flight 필수 (R6).
  paragraph_id "2" parser 의심: plan 의 "260:16" 진의는 "발견사항 parent
  intro" 로, block_ordinal 1824 (1822=¶15 직후, 1825=(a) sub-item 직전)
  위치상 실제 ¶16 으로 추정. 본 oracle 은 chunk_id 그대로 채택.
```

### Evidence — chunks.jsonl 원문 (2 primary)

```jsonl
# Primary 1 — 260:01824:2 (요구사항, char_count=117)
chunk_id="260:01824:2"  isa_no=260  section=requirements  block_ordinal=1824
heading_trail=[
  "감사기준서 260  지배기구와의 커뮤니케이션",
  "요구사항",
  "커뮤니케이션할 사항",
  "감사에서의 유의적 발견사항"
]
paragraph_ids=["2"]   # ← parser 의심: ¶16 추정 (block_ordinal 1822=¶15 / 1825=(a))
text="감사기준서 260  지배기구와의 커뮤니케이션 > 요구사항 > 커뮤니케이션할
      사항 > 감사에서의 유의적 발견사항\n\n
      2. 감사인은 아래 사항에 대하여 지배기구와 커뮤니케이션하여야 한다.
      (문단 A17-A18 참조)"
refs=["A17","A18"]
```

```jsonl
# Primary 2 — 265:02105:9 (요구사항, char_count=134)
chunk_id="265:02105:9"  isa_no=265  section=requirements  block_ordinal=2105
heading_trail=[
  "감사기준서 265  내부통제 미비점에 대한 지배기구와 경영진과의 커뮤니케이션",
  "요구사항"
]
paragraph_ids=["9"]
text="감사기준서 265  내부통제 미비점에 대한 지배기구와 경영진과의
      커뮤니케이션 > 요구사항\n\n
      9. 감사인은 감사 중에 식별된 유의적 내부통제 미비점들을 지배기구에게
      적시에 서면으로 커뮤니케이션하여야 한다. (문단 A12-A18, A27 참조)"
refs=["A12".."A18","A27"]
```

### DR-1 — Intro-parent stub 검증 (NIT-N1 임계 ≤ 115)

| primary chunk_id | char_count | section | paragraph_ids | 본문 패턴 | stub? |
|---|---:|---|---|---|---|
| 260:01824:2 | 117 | requirements | ["2"] | "...아래 사항에 대하여 지배기구와 커뮤니케이션하여야 한다." | ✗ |
| 265:02105:9 | 134 | requirements | ["9"] | "...유의적 내부통제 미비점들을 지배기구에게 적시에 서면으로 커뮤니케이션하여야 한다." | ✗ |

**판정**:
- 260:01824:2 cc=117 > 115 임계 통과. 본문은 "...에 대하여 ... 하여야 한다."
  로 후속 (a)-(e) sub-item 분산이지만, DR-1 §판정 기준 1 ("다음과 같다."
  종결) 비매칭 + DR-1 §판정 기준 3 (`section ∈ {definitions, objective,
  intro}`) 의 section 조건 미충족 (requirements). action verb 포함
  substantive. → stub 아님.
- 265:02105:9 cc=134, 본문 단일 의무 명시 (서면 커뮤니케이션 강제). → stub 아님.

→ DR-1 ✓.

### DR-2 — Resolver 매핑 로그 (logical path 미사용)

2 primary 모두 concrete chunk_id 직접 지정. logical path 사용 0건. → DR-2 ✓
(N/A, vacuously satisfied).

### DR-3 — Alphabetical (i) vs Roman (i) 모호성 검증

paragraph_ids: 260:01824:2 = `["2"]`, 265:02105:9 = `["9"]`. 모두 numeric,
`(i)` sub-item 인용 0건. → DR-3 ✓.

### DR-4 — Query phrasing ↔ primary framing 정합 (NIT-N4 정량)

**쿼리 표면형 토큰** (공백 split, stopword 후):
```text
["감사인은", "지배기구에게", "감사에서의", "유의적", "발견사항을", "어떻게",
 "커뮤니케이션하며,", "식별된", "유의적", "내부통제", "미비점은", "어떤",
 "형식으로", "보고해야", "하는가?"]
```
(stopword 매칭 0건 — 모두 agglutinated surface form. "유의적" 중복 1회)

**Primary mini-table** (각 primary top-20 ∩ query, strict surface-form):

| primary chunk_id | primary top-20 (요약) | 교집합 | 일치 (≥2) |
|---|---|---|---|
| 260:01824:2 | >(3), 감사기준서, 260, 지배기구와의, 커뮤니케이션, 요구사항, 커뮤니케이션할, 사항, 감사에서의, 유의적, 발견사항, 2., 감사인은, 아래, 사항에, 대하여, 지배기구와, 커뮤니케이션하여야, 한다., (문단 | {감사인은, 유의적, 감사에서의} = 3 | ✓ |
| 265:02105:9 | 내부통제(2), 감사기준서, 265, 미비점에, 대한, 지배기구와, 경영진과의, 커뮤니케이션, >, 요구사항, 9., 감사인은, 감사, 중에, 식별된, 유의적, 미비점들을, 지배기구에게, 적시에, 서면으로 | {감사인은, 지배기구에게, 유의적, 식별된, 내부통제} = 5 | ✓ |

**판정**: 2 primary 모두 ≥ 2 통과. 본 oracle (c) intentional gap 0건.
N1 Q27 의 (c) 1건과 합산하여 cross-standard 누적 (c) = 1/2 oracle (50%) 단,
누적 임계 30% 는 cross 9 oracle 전수 산정 — 현 시점 산정 무의미 (P5 S3
audit 입력 으로 본 oracle 토큰 기록).

### DR-5(a) — Cross-standard primary ISA ≥ 2

| primary chunk_id | isa_no |
|---|---|
| 260:01824:2 | 260 |
| 265:02105:9 | 265 |

unique ISAs = {260, 265} = **2 개** → DR-5(a) ✓ (≥ 2 만족). plan §4.2 의
"small-ISA 포함" 위험 사항: 260 / 265 모두 작은 ISA 측에 속함 → P7 재측정
시 Upstage 인덱스 커버리지 pre-flight 우선 대상 (notes 명기).

### DR-5(b) — Cross 쿼리 간 primary disjoint (NIT-N6)

기 작성 cross oracle: N1 (Q27) primary {500:04351:6, 330:03681:7, 450:04218:8}.
본 N8 primary {260:01824:2, 265:02105:9} 와 차집합 = ∅ 교집합. → DR-5(b) ✓
(disjoint 보장).

추가 P2 진행 시 작성될 N7 (Q33) primary 후보 {250:01628:22, 240:01098:22}
와도 disjoint 사전 확인 (chunk_id 전수 차이) → 보장.

### DR 체크리스트

```text
[✓] DR-1 — Intro-parent stub 없음
    근거: 2 primary 모두 char_count > 115 + 본문 substantive action verb
[✓] DR-2 — Resolver 매핑 로그 첨부
    근거: 모든 primary concrete chunk_id 직접 지정 (N/A)
[✓] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: paragraph_ids 모두 numeric ["2"]/["9"]
[✓] DR-4 — Query phrasing ↔ primary framing 일치
    근거: 260:2 ∩=3, 265:9 ∩=5 (양 primary 모두 ≥ 2)
[✓] DR-5(a) (cross) — primary ISA 수 ≥ 2
    근거: unique ISAs = {260, 265} = 2
[✓] DR-5(b) (cross, NIT-N6) — 다른 cross 와 primary disjoint
    근거: N1 primary 와 ∅ 교집합 보장
```

→ 6 항목 전수 ✓. DA spot-check 대상 (N1 → N8 incremental).

### S4 prescreen (Phase 3 v2 top-5 union, 141 distinct chunks)

본 N8 2개 primary 를 v2 top-5 union 대조 (참고용, P5 S4 audit 정확 산정 전):
- `260:01824:2` → ? (v2 cross-standard 6 oracle 전수 chain 확인 필요, 본
  phase 4 P0 oracle 작성 단계에서는 측정 보류, P5 S4 audit 시점 일괄
  측정 권고)
- `265:02105:9` → ? (동상)

DA prescreen 시 N1 의 2/3 IN 패턴 누적 측정 (N8 결과 추가 시점).

---

## Q33 — N7: 법규위반 시사점 ↔ 지배기구 부정 질문 (250↔240)

```yaml
id: Q33
category: cross-standard
query: "감사인은 식별되거나 의심되는 법규위반의 시사점을 어떻게 평가하며, 부정에 대해서는 지배기구에게 어떤 질문을 해야 하는가?"
expected_primary_chunks:
  - "250:01628:22"
  - "240:01098:22"
expected_related_chunks:
  - "250:01625:21"   # ISA 250 ¶21 법규위반이 식별 시 추가 절차 (chain prior)
  - "240:01095:21"   # ISA 240 ¶21 경영진 부정 risk 질문
  - "240:01102:24"   # ISA 240 ¶24 기타정보 부정 RMM (N9 primary, but related로 chain)
  - "240:01098:22"   # (primary 중복, top-10 보조 채집 컨텍스트)
notes: |
  Cross-standard "법규위반 × 부정 risk 식별" 축. 250 (법규위반 시사점 평가)
  → 240 (지배기구 인지 여부 질문) 의 "감사인 detect → 지배기구 confirm"
  흐름. cc 가 큰 편 (176/258) 으로 substantive content 풍부, stub 위험 없음.
  N9 와 240:24 → 240:22 paragraph 분리로 DR-5(b) disjoint 보장 (P2
  cross-cutting overlap 검증 §결과 참조).
  related 의 240:01102:24 는 N9 primary 와 동일 chunk — DR-5(b) 적용 대상은
  primary set 만이며 related (top-10 보조) 는 chain semantic 보강 목적으로
  중복 허용 (NIT-N6 본문 §운용).
```

### Evidence — chunks.jsonl 원문 (2 primary)

```jsonl
# Primary 1 — 250:01628:22 (요구사항, char_count=176)
chunk_id="250:01628:22"  isa_no=250  section=requirements  block_ordinal=1628
heading_trail=[
  "감사기준서 250  재무제표감사에서 법률과 규정의 고려",
  "요구사항",
  "법규위반이 식별되거나 의심될 때의 감사절차"
]
paragraph_ids=["22"]
text="감사기준서 250  재무제표감사에서 법률과 규정의 고려 > 요구사항 >
      법규위반이 식별되거나 의심될 때의 감사절차\n\n
      22. 감사인은 감사인의 위험평가, 서면진술의 신뢰성 등 감사의 다른
      측면과 관련하여 식별되었거나 의심되는 법규위반의 시사점을 평가하고,
      적절한 조치를 취하여야 한다. (문단 A23- A 25 참조)"
refs=["A23"]
```

```jsonl
# Primary 2 — 240:01098:22 (요구사항, char_count=258)
chunk_id="240:01098:22"  isa_no=240  section=requirements  block_ordinal=1098
heading_trail=[
  "감사기준서 240  재무제표감사에서 부정에 관한 감사인의 책임",
  "요구사항",
  "위험평가절차 및 관련 활동",
  "지배기구"
]
paragraph_ids=["22"]
text="감사기준서 240  재무제표감사에서 부정에 관한 감사인의 책임 > 요구사항
      > 위험평가절차 및 관련 활동 > 지배기구\n\n
      22. 지배기구의 모든 구성원이 그 기업의 경영에 참여하고 있지 않는 한,
      감사인은 기업에 영향을 주는 부정으로서 실제로 발생하였거나 의심되는
      부정 또는 혐의중인 부정을 지배기구가 인지하고 있는지 여부를 결정하기
      위해 지배기구에 질문을 하여야 한다. 지배기구에게 이러한 질문을 하는
      것은 경영진에 대한 질문의 답변내용을 확인하는 목적도 있다."
refs=[]
```

### DR-1 — Intro-parent stub 검증 (NIT-N1 임계 ≤ 115)

| primary chunk_id | char_count | section | paragraph_ids | 본문 패턴 | stub? |
|---|---:|---|---|---|---|
| 250:01628:22 | 176 | requirements | ["22"] | "...법규위반의 시사점을 평가하고, 적절한 조치를 취하여야 한다." | ✗ |
| 240:01098:22 | 258 | requirements | ["22"] | "...지배기구가 인지하고 있는지 여부를 결정하기 위해 지배기구에 질문을 하여야 한다." | ✗ |

**판정**: 둘 다 cc > 115 임계 + 본문 substantive action verb. 분명한 non-stub.
→ DR-1 ✓.

### DR-2 — Resolver 매핑 로그 (logical path 미사용)

2 primary 모두 concrete chunk_id 직접 지정. → DR-2 ✓ (N/A).

### DR-3 — Alphabetical (i) vs Roman (i) 모호성 검증

paragraph_ids = `["22"]` 양 primary 동일. numeric, `(i)` 사용 0건. → DR-3 ✓.

### DR-4 — Query phrasing ↔ primary framing 정합 (NIT-N4 정량)

**쿼리 표면형 토큰** (공백 split, stopword 후):
```text
["감사인은", "식별되거나", "의심되는", "법규위반의", "시사점을", "어떻게",
 "평가하며,", "부정에", "대해서는", "지배기구에게", "어떤", "질문을", "해야",
 "하는가?"]
```
(stopword 매칭 0건)

**Primary mini-table** (각 primary top-20 ∩ query, strict surface-form):

| primary chunk_id | primary top-20 (요약) | 교집합 | 일치 (≥2) |
|---|---|---|---|
| 250:01628:22 | >(2), 감사기준서, 250, 재무제표감사에서, 법률과, 규정의, 고려, 요구사항, 법규위반이, 식별되거나, 의심될, 때의, 감사절차, 22., 감사인은, 감사인의, 위험평가,, 서면진술의, 신뢰성, 감사의 | {감사인은, 식별되거나} = 2 | ✓ |
| 240:01098:22 | >(3), 질문을(2), 감사기준서, 240, 재무제표감사에서, 부정에, 관한, 감사인의, 책임, 요구사항, 위험평가절차, 관련, 활동, 지배기구, 22., 지배기구의, 모든, 구성원이, 그, 기업의 | {질문을, 부정에} = 2 | ✓ |

**판정**: 양 primary ≥ 2 통과, (c) gap 0건. 250:22 의 "법규위반의" 토큰은
정확 일치하지만 본문 top-20 에는 "법규위반이" (조사 차이) 만 포함되어
표면형 매칭 미달 — strict surface form 의 한계 명시 사례. 240:22 의
"감사인은" 도 top-20 에는 "감사인의" 만 (주어/소유격 차이) — 동상.

### DR-5(a) — Cross-standard primary ISA ≥ 2

| primary chunk_id | isa_no |
|---|---|
| 250:01628:22 | 250 |
| 240:01098:22 | 240 |

unique ISAs = {250, 240} = **2 개** → DR-5(a) ✓.

### DR-5(b) — Cross 쿼리 간 primary disjoint (NIT-N6)

기 작성 cross oracle:
- N1 (Q27) primary {500:04351:6, 330:03681:7, 450:04218:8}
- N8 (Q34) primary {260:01824:2, 265:02105:9}
합집합 = 5 chunk_ids. 본 N7 primary {250:01628:22, 240:01098:22} 와 차집합:
∅ 교집합 → DR-5(b) ✓ (disjoint 보장).

P2 cross-cutting §overlap 검증 결과 N9 primary {550:06012:18, 240:01102:24}
와 사전 disjoint 보장 (240:22 ≠ 240:24). N9 작성 시 별도 disjoint 검증 절차
계속 적용.

### DR 체크리스트

```text
[✓] DR-1 — Intro-parent stub 없음
    근거: 2 primary cc 176/258 (충분 substantive)
[✓] DR-2 — Resolver 매핑 로그 첨부
    근거: concrete chunk_id 직접 (N/A)
[✓] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: paragraph_ids 모두 numeric ["22"]
[✓] DR-4 — Query phrasing ↔ primary framing 일치
    근거: 250:22 ∩=2, 240:22 ∩=2 (양 primary 모두 ≥ 2 정확 임계)
[✓] DR-5(a) (cross) — primary ISA 수 ≥ 2
    근거: unique ISAs = {250, 240} = 2
[✓] DR-5(b) (cross, NIT-N6) — 다른 cross 와 primary disjoint
    근거: N1 ∪ N8 ∪ {N9 prep} 와 ∅ 교집합 보장
```

→ 6 항목 전수 ✓. (c) intentional gap 0건. small-ISA 위험 없음 (250/240
모두 hub-class 표준).

### S4 prescreen 측정 보류 (P5 일괄)

N8 와 동일 정책 — P5 S4 audit 시점 v3 24 신규 primary 일괄 측정.

### 워크플로 메모 (DE 자체 학습)

본 oracle 의 DR-4 교집합 = 정확히 2 (임계 hit) — strict surface form
한계로 "법규위반의/법규위반이" "감사인은/감사인의" 등 한국어 조사 차이
토큰이 매칭에서 제외. 향후 N9 / N2-N6 작성 시 query 와 primary 본문 의
조사·어미 인접성 사전 검토 권고. 너무 빡빡하면 query 가 인위적 paraphrase
가 되어 cross-link 측정 본질 훼손 (Q27 N1 과 동일 trade-off).

---

## Q35 — N9: 특수관계자 거래 RMM ↔ 기타정보 부정 RMM (550↔240)

```yaml
id: Q35
category: cross-standard
query: "감사인은 특수관계자 거래에 연관된 중요왜곡표시위험을 어떻게 식별·평가하며, 입수한 기타정보가 부정으로 인한 위험을 시사하는 경우 이를 유의적 위험으로 어떻게 취급하는가?"
expected_primary_chunks:
  - "550:06012:18"
  - "240:01102:24"
expected_related_chunks:
  - "550:06010:17"   # ISA 550 ¶17 특수관계자 RMM 식별 절차 (chain prior)
  - "240:01098:22"   # ISA 240 ¶22 지배기구 부정 인지 질문 (N7 primary, related 중복 허용)
  - "240:01100:23"   # ISA 240 ¶23 분석적 절차 부정 RMM
  - "315:??:????"    # ISA 315 RMM 식별·평가 일반 규정 (logical link, 미지정)
notes: |
  Cross-standard "특수관계자 + 부정 RMM 식별" 축. 550 (특수관계자 거래의
  유의적 위험 분류 강제) → 240 (기타정보를 통한 부정 시사) 의 RMM 식별
  쌍. 550:18 본문은 "감사기준서 315의 요구사항을 충족시키기 위하여" 로
  ISA 315 와 명시적 logical reference — DR-5(a) 의 cross 본질 자체 강화.
  N7 의 240:22 (지배기구 질문) 는 related 로 cross-chain 보강.
  DA N7 spot-check §N9 작성 주의점 (2026-04-19) 권고 적용: query 가
  primary 본문 surface form 과 조사 일치 토큰 의도 배치 → DR-4 결과
  ∩=6/6 으로 N7 =2 margin 회복.
```

### Evidence — chunks.jsonl 원문 (2 primary)

```jsonl
# Primary 1 — 550:06012:18 (요구사항, char_count=288)
chunk_id="550:06012:18"  isa_no=550  section=requirements  block_ordinal=6012
heading_trail=[
  "감사기준서 550  특수관계자",
  "요구사항",
  "특수관계 및 특수관계자 거래에 연관된 중요왜곡표시위험의 식별과 평가"
]
paragraph_ids=["18"]
text="감사기준서 550  특수관계자 > 요구사항 > 특수관계 및 특수관계자 거래에
      연관된 중요왜곡표시위험의 식별과 평가\n\n
      18. 중요왜곡표시위험을 식별하고 평가하기 위한 감사기준서 315의
      요구사항을 충족시키기 위하여, 감사인은 특수관계 및 특수관계자 거래와
      연관된 중요왜곡표시위험을 식별하고 평가하여야 하며, 그러한 위험 중
      유의적 위험이 있는지 여부를 결정하여야 한다. 이러한 결정 시, 식별된
      유의적인 특수관계자 거래가 해당 기업의 정상적인 사업과정을 벗어난
      경우에는, 감사인은 이를 유의적 위험으로 취급해야 한다."
refs=[]
```

```jsonl
# Primary 2 — 240:01102:24 (요구사항, char_count=135)
chunk_id="240:01102:24"  isa_no=240  section=requirements  block_ordinal=1102
heading_trail=[
  "감사기준서 240  재무제표감사에서 부정에 관한 감사인의 책임",
  "요구사항",
  "위험평가절차 및 관련 활동",
  "기타정보"
]
paragraph_ids=["24"]
text="감사기준서 240  재무제표감사에서 부정에 관한 감사인의 책임 > 요구사항
      > 위험평가절차 및 관련 활동 > 기타정보\n\n
      24. 감사인은 입수한 기타정보가 부정으로 인한 중요왜곡표시위험을
      나타내는지 여부를 고려하여야 한다. (문단 A23 참조)"
refs=["A23"]
```

### Pilot 조건 5 — 3중 cross-reference 의무 (두 번째 instance)

| 출처 | 후보 | 정합 |
|---|---|---|
| plan §4.2 line 90 | N9 = `550:18, 240:24` | base |
| chunks.jsonl 실측 | `550:06012:18` / `240:01102:24` | ✓ (P2 cross-cutting §실측 표 참조) |
| 기 작성 cross primary union | N1 (3) ∪ N8 (2) ∪ N7 (2) = 7 chunks | N9 (2) ∩ union = ∅ ✓ |

→ 3중 교차 통과. yaml block 작성 진입 정당화.

### DR-1 — Intro-parent stub 검증 (NIT-N1 임계 ≤ 115)

| primary chunk_id | char_count | section | paragraph_ids | 본문 패턴 | stub? |
|---|---:|---|---|---|---|
| 550:06012:18 | 288 | requirements | ["18"] | "...감사인은 특수관계 및 특수관계자 거래와 연관된 ... 유의적 위험으로 취급해야 한다." | ✗ |
| 240:01102:24 | 135 | requirements | ["24"] | "...입수한 기타정보가 부정으로 인한 중요왜곡표시위험을 나타내는지 여부를 고려하여야 한다." | ✗ |

**판정**: 둘 다 cc > 115, 본문 substantive (multi-clause obligation +
specific action verbs). → DR-1 ✓.

### DR-2 — Resolver 매핑 로그 (logical path 미사용)

2 primary 모두 concrete chunk_id 직접 지정. → DR-2 ✓ (N/A).
참고: notes 의 related chain 중 `315:??:????` 는 logical reference 의도이나
구체 chunk_id 미확정 → expected_related_chunks 에서 제외하고 notes 본문에만
서술 (resolver 호출 없음).

### DR-3 — Alphabetical (i) vs Roman (i) 모호성 검증

paragraph_ids = `["18"]` / `["24"]`. numeric, `(i)` 사용 0건. → DR-3 ✓.

### DR-4 — Query phrasing ↔ primary framing 정합 (NIT-N4 정량)

**쿼리 표면형 토큰** (공백 split, stopword 후, 19개):
```text
["감사인은", "특수관계자", "거래에", "연관된", "중요왜곡표시위험을", "어떻게",
 "식별·평가하며,", "입수한", "기타정보가", "부정으로", "인한", "위험을",
 "시사하는", "경우", "이를", "유의적", "위험으로", "어떻게", "취급하는가?"]
```
(stopword 매칭 0건, "어떻게" 중복 1회 — DR-4 mini-table 중복 1회 집계 정책)

**Primary mini-table** (각 primary top-20 ∩ query, strict surface-form):

| primary chunk_id | primary top-20 (요약) | 교집합 | 일치 (≥2) |
|---|---|---|---|
| 550:06012:18 | 특수관계자(3), 감사기준서(2), 특수관계(2), >(2), 연관된(2), 중요왜곡표시위험을(2), 감사인은(2), 식별하고(2), 유의적(2), 한다.(2), 550, 요구사항, 거래에, 중요왜곡표시위험의, 식별과, 평가, 18., 평가하기, 위한, 315의 | {특수관계자, 감사인은, 유의적, 거래에, 중요왜곡표시위험을, 연관된} = 6 | ✓ |
| 240:01102:24 | >(3), 감사기준서, 240, 재무제표감사에서, 부정에, 관한, 감사인의, 책임, 요구사항, 위험평가절차, 관련, 활동, 기타정보, 24., 감사인은, 입수한, 기타정보가, 부정으로, 인한, 중요왜곡표시위험을 | {감사인은, 입수한, 기타정보가, 부정으로, 인한, 중요왜곡표시위험을} = 6 | ✓ |

**판정**: 양 primary ∩ = 6 (강한 매칭). N7 의 정확 임계 hit (=2) 대비 큰 margin
회복 — DA N7 spot-check §N9 권고 ("query 와 primary 본문 조사 일치 토큰
1-2개 의도 배치, narrowing 아닌 natural phrasing 범위") 적용 효과. (c) gap
0건.

### DR-5(a) — Cross-standard primary ISA ≥ 2

| primary chunk_id | isa_no |
|---|---|
| 550:06012:18 | 550 |
| 240:01102:24 | 240 |

unique ISAs = {550, 240} = **2 개** → DR-5(a) ✓. 추가로 550:18 본문에
"감사기준서 315의 요구사항을 충족시키기 위하여" 로 ISA 315 와 logical
chain — cross 본질 강화 (3 ISA 의도, primary 는 2 ISA 만 강제).

### DR-5(b) — Cross 쿼리 간 primary disjoint (NIT-N6)

기 작성 cross oracle primary union (4 oracles):
- N1 (Q27): {500:04351:6, 330:03681:7, 450:04218:8} (3)
- N8 (Q34): {260:01824:2, 265:02105:9} (2)
- N7 (Q33): {250:01628:22, 240:01098:22} (2)

union = 7 chunks. 본 N9 primary {550:06012:18, 240:01102:24} 와 차집합 = ∅
교집합 → DR-5(b) ✓. P2 cross-cutting §240:22 vs 240:24 phantom 검증
결과 사전 disjoint 보장 (240:01098:22 ≠ 240:01102:24, block_ordinal 1098 vs
1102, paragraph_id 22 vs 24).

### DR 체크리스트

```text
[✓] DR-1 — Intro-parent stub 없음
    근거: 2 primary cc 288/135 (충분 substantive)
[✓] DR-2 — Resolver 매핑 로그 첨부
    근거: concrete chunk_id 직접 (N/A)
[✓] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: paragraph_ids 모두 numeric ["18"]/["24"]
[✓] DR-4 — Query phrasing ↔ primary framing 일치
    근거: 550:18 ∩=6, 240:24 ∩=6 (양 primary 강한 매칭, ≥ 3 robustness)
[✓] DR-5(a) (cross) — primary ISA 수 ≥ 2
    근거: unique ISAs = {550, 240} = 2 (+ 본문 logical ref 315)
[✓] DR-5(b) (cross, NIT-N6) — 다른 cross 와 primary disjoint
    근거: N1 ∪ N8 ∪ N7 primary union 7 chunks 와 ∅ 교집합
```

→ 6 항목 전수 ✓. (c) intentional gap 0건. small-ISA 위험 없음 (550/240
hub-class).

### S4 prescreen 측정 보류 (P5 일괄)

N1/N8/N7 와 동일 — P5 audit 시점 v3 24 신규 primary 일괄 측정.

### DR-4 robustness margin 비교 (DA P7 분석 조건 입력)

DA N7 spot-check §1 P7 분석 조건 ("=2 hit oracle vs ≥ 3 hit oracle 의
recall@5 차이 t-test") 입력 자료:

| oracle | primary chunk_id | ∩ | margin 분류 |
|---|---|---:|---|
| N1 (Q27) | 500:04351:6 | 4 | ≥ 3 |
| N1 (Q27) | 330:03681:7 | 1 | (c) intentional |
| N1 (Q27) | 450:04218:8 | 2 | =2 hit |
| N8 (Q34) | 260:01824:2 | 3 | ≥ 3 |
| N8 (Q34) | 265:02105:9 | 5 | ≥ 3 |
| N7 (Q33) | 250:01628:22 | 2 | =2 hit |
| N7 (Q33) | 240:01098:22 | 2 | =2 hit |
| N9 (Q35) | 550:06012:18 | 6 | ≥ 3 |
| N9 (Q35) | 240:01102:24 | 6 | ≥ 3 |

현 누적: ≥ 3 margin = 5 / =2 hit = 3 / (c) = 1. P5 retrofit_audit 입력에
이 표 자동 추출 권고 (yaml block primary chunk_id + DR-4 mini-table
교집합 컬럼).

---

## Q28 — N2: 서비스조직 통제 ↔ 내부통제 미비점 ↔ 추가감사절차 설계 (402↔315↔330)

```yaml
id: Q28
category: cross-standard
query: "감사인은 서비스조직의 통제 미비점이 이용자기업의 재무제표에 미치는 영향을 어떻게 평가하고, 이용자기업 내부통제 시스템의 통제 미비점을 식별하며, 평가된 위험에 대응하는 추가감사절차의 성격·시기·범위를 어떻게 설계해야 하는가?"
expected_primary_chunks:
  - "402:04010:9"
  - "315:02482:22"
  - "330:03680:6"
expected_related_chunks:
  - "402:04012:10"   # ISA 402 ¶10 서비스조직 이해 추가절차
  - "315:02485:23"   # ISA 315 ¶23 RMM 식별 (315:22 직후)
  - "330:03681:7"    # ISA 330 ¶7 추가감사절차 설계 시 유의사항 (N1 primary, related 중복 허용)
  - "330:03687:8"    # ISA 330 ¶8 통제테스트 설계 (response detail)
notes: |
  Cross-standard "서비스조직 통제 → 내부통제 미비점 → 추가감사절차 설계" 축.
  402:9 본문이 "감사기준서 315에 따라" self-cross-ref → 402→315 chain
  본문 명시. 315:22 (통제 미비점 식별 framework) 가 402:9 (서비스조직 specific)
  의 일반화 모태. 330:6 (umbrella 추가감사절차 설계) 가 chain 의 response
  단계. 3 ISA × 3 layer (specific → general → response) 구조.

  plan §4.2 line 83 entry `315:12, 330:12` 를 P2 진행 중 swap:
    - 315:12 (`315:02411:12` cc=72, definitions stub) → **315:22** (DR-1 위반 회피)
    - 330:12 (`330:03701:12` heading_trail "중간기간 감사증거" axis-narrow)
      → **330:6** (umbrella axis alignment 회복)
  P9 plan diff log 에 정정 사유 기재 — DR 본문 불변, single-DR-change.

  §6/§7 semantic proximity 경계 (DA 2026-04-19 DM):
  330:03680:6 (N2 primary) 와 330:03681:7 (N1 primary) 는 chunk_id 형식적
  disjoint (DR-5(b) ✓) 이나 parent-child 의미 관계. BGE 임베딩 시 두 chunk
  semantic proximity 잠재 → P5 S4 retrofit audit 시 "semantic proximity
  artefact" diagnostic 컬럼 추가 추적. 두 oracle 의 query verb stem 분화
  ("입수·커뮤니케이션" N1 vs "설계" N2) 로 surface 회수 분리 의도.
  본 N2 가 DR-5(b) parent-child proximity pilot instance.

  DR-4 strict/loose 집계 (DA 2026-04-19 17:15+ 재확인):
  330:03680:6 의 공식 ∩ = 6 (strict surface form). 단 활용 변이 collapse
  적용 시 "대응하는"≡"대응한", "설계해야"≡"설계하고" 로 ∩=4 (loose).
  현 정책 = strict 만 공식. loose 4 는 informative only — P3 "활용 변이
  병합 옵션 재검토" ticket (DR-4 임계 재상향 논의와 묶음) 입력 자료.
```

### Evidence — chunks.jsonl 원문 (3 primary)

```jsonl
# Primary 1 — 402:04010:9 (요구사항, char_count=211)
chunk_id="402:04010:9"  isa_no=402  section=requirements  block_ordinal=4010
heading_trail=[
  "감사기준서 402  서비스조직을 이용하는 기업에 관한 감사 고려사항",
  "요구사항",
  "내부통제 등 서비스조직에 의하여 제공되는 서비스에 대한 이해"
]
paragraph_ids=["9"]
text="감사기준서 402  서비스조직을 이용하는 기업에 관한 감사 고려사항 >
      요구사항 > 내부통제 등 서비스조직에 의하여 제공되는 서비스에 대한
      이해\n\n
      9. 이용자기업 감사인은 감사기준서 315 에 따라 이용자기업을 이해할
      때, 이용자기업이 자신의 사업에 서비스조직의 서비스를 어떻게
      이용하는지를 이해하여야 하며, 이에는 다음과 같은 내용이 포함되어야
      한다. (문단 A1-A2 참조)"
refs=["A1", "A2"]
```

```jsonl
# Primary 2 — 315:02482:22 (요구사항, char_count=216)
chunk_id="315:02482:22"  isa_no=315  section=requirements  block_ordinal=2482
heading_trail=[
  "감사기준서 315  중요왜곡표시위험의 식별과 평가",
  "요구사항",
  "기업과 기업환경, 해당 재무보고체계 및 기업의 내부통제시스템에 대한 이해 (문단 A48-A49 참조)",
  "기업의 내부통제시스템 내의 통제 미비점"
]
paragraph_ids=["22"]
text="감사기준서 315  중요왜곡표시위험의 식별과 평가 > 요구사항 >
      기업과 기업환경, 해당 재무보고체계 및 기업의 내부통제시스템에
      대한 이해 (문단 A48-A49 참조) > 기업의 내부통제시스템 내의 통제
      미비점\n\n
      22. 기업의 내부통제시스템의 구성요소 각각에 대한 평가에 기초하여,
      감사인은 하나 이상의 통제 미비점이 식별되었는지 여부를 결정하여야
      한다. (문단 A182-A183 참조)"
refs=["A182", "A183"]
```

```jsonl
# Primary 3 — 330:03680:6 (요구사항, char_count=178)
chunk_id="330:03680:6"  isa_no=330  section=requirements  block_ordinal=3680
heading_trail=[
  "감사기준서 330  평가된 위험에 대한 감사인의 대응",
  "요구사항",
  "경영진주장 수준의 평가된 중요왜곡표시위험에 대응한 감사절차"
]
paragraph_ids=["6"]
text="감사기준서 330  평가된 위험에 대한 감사인의 대응 > 요구사항 >
      경영진주장 수준의 평가된 중요왜곡표시위험에 대응한 감사절차\n\n
      6. 감사인은 경영진주장 수준의 평가된 중요왜곡표시위험을 기초로
      하여 이에 대응하는 추가감사절차의 성격, 시기 및 범위를 설계하고
      수행하여야 한다. (문단 A4-A8, A42-A52 참조)"
refs=["A4", "A5", "A6", "A7", "A8"]
```

### Pilot 조건 5 — 3중 cross-reference 의무 (세 번째 instance)

| 출처 | 후보 | 정합 |
|---|---|---|
| plan §4.2 line 83 | N2 = `402:9, 315:12, 330:12` | base (단 315:12·330:12 DR 위반 → swap) |
| chunks.jsonl 실측 | `402:04010:9` ✓ / `315:02411:12` cc=72 stub ✗ → `315:02482:22` ✓ / `330:03701:12` axis-narrow → `330:03680:6` ✓ | swap 2건 (DA 2026-04-19 DM 승인) |
| 기 작성 cross primary union | N1 (3) ∪ N7 (2) ∪ N8 (2) ∪ N9 (2) = 9 chunks | N2 (3) ∩ union = ∅ ✓ |

→ 3중 교차 통과 (plan swap 정정 포함). yaml block 작성 정당화.

### DR-1 — Intro-parent stub 검증 (NIT-N1 임계 ≤ 115)

| primary chunk_id | char_count | section | paragraph_ids | 본문 패턴 | stub? |
|---|---:|---|---|---|---|
| 402:04010:9 | 211 | requirements | ["9"] | "...이용자기업이 자신의 사업에 서비스조직의 서비스를 어떻게 이용하는지를 이해하여야 하며..." | ✗ |
| 315:02482:22 | 216 | requirements | ["22"] | "...감사인은 하나 이상의 통제 미비점이 식별되었는지 여부를 결정하여야 한다." | ✗ |
| 330:03680:6 | 178 | requirements | ["6"] | "...경영진주장 수준의 평가된 중요왜곡표시위험을 기초로 하여 이에 대응하는 추가감사절차의 성격, 시기 및 범위를 설계하고 수행하여야 한다." | ✗ |

**판정**: 3 primary 모두 cc > 115, 본문 substantive (action verb + multi-clause obligation). → DR-1 ✓.

**Stub swap 기록**: `315:02411:12` (cc=72, "이 감사기준서에서 사용하는 용어의 정의는 다음과 같다.") → DR-1 위반 → §22 로 swap. plan §4.2 정정.

### DR-2 — Resolver 매핑 로그 (logical path 미사용)

3 primary 모두 concrete chunk_id 직접 지정. → DR-2 ✓ (N/A).
참고: 402:9 본문 자체가 "감사기준서 315에 따라" 로 ISA 315 logical chain 명시
→ DR-2 axis alignment 본문 수준 입증 (DA bonus signal).

### DR-3 — Alphabetical (i) vs Roman (i) 모호성 검증

paragraph_ids = `["9"]` / `["22"]` / `["6"]`. numeric, `(i)` 사용 0건. → DR-3 ✓.

### DR-4 — Query phrasing ↔ primary framing 정합 (NIT-N4 정량)

**쿼리 표면형 토큰** (공백 split, stopword 후, 28개):
```text
["감사인은", "서비스조직의", "통제", "미비점이", "이용자기업의", "재무제표에",
 "미치는", "영향을", "어떻게", "평가하고,", "이용자기업", "내부통제", "시스템의",
 "통제", "미비점을", "식별하며,", "평가된", "위험에", "대응하는", "추가감사절차의",
 "성격·시기·범위를", "어떻게", "설계해야", "하는가?"]
```
(stopword 매칭 0건; "통제" 중복 2회, "어떻게" 중복 2회 — 중복은 DR-4 mini-table 1회 집계 정책)

**Primary mini-table** (각 primary top-20 ∩ query, strict surface-form):

| primary chunk_id | primary top-20 (요약) | 교집합 | 일치 (≥2) |
|---|---|---|---|
| 402:04010:9 | 감사기준서, 402, 서비스조직을, 이용하는, 기업에, 감사, 고려사항, >(2), 요구사항, 내부통제, 등, 서비스조직에, 의하여, 제공되는, 서비스에, 대한, 이해, 이용자기업, 감사인은, 감사기준서, 315, 따라 | {감사인은, 이용자기업, 내부통제} = 3 | ✓ |
| 315:02482:22 | 감사기준서, 315, 중요왜곡표시위험의, 식별과, 평가, >(4), 요구사항, 기업과, 기업환경, 해당, 재무보고체계, 기업의, 내부통제시스템에, 대한, 이해, 통제, 미비점, 감사인은, 하나, 식별되었는지, 여부를, 결정하여야, 한다. | {감사인은, 통제, 미비점} = 3 | ✓ |
| 330:03680:6 | 감사기준서, 330, 평가된, 위험에, 대한, 감사인의, 대응, >(2), 요구사항, 경영진주장, 수준의, 중요왜곡표시위험에, 대응한, 감사절차, 감사인은, 위험을, 기초로, 추가감사절차의, 성격,, 시기, 범위를, 설계하고, 수행하여야, 한다. | {감사인은, 평가된, 위험에, 대응하는, 추가감사절차의, 설계해야} = 6 | ✓ |

**Strict 정책 적용** (DA spot-check 2026-04-19 17:15+ 재확인): query_design_rules.md
DR-4 § "strict surface form tokenization (공백 split, 형태소 분석 미적용)" +
stopword 만 제거. **활용 변이 병합 = 형태소 분석 lite → 정책 밖**. 따라서:
- 330:03680:6 공식 ∩ = **6 (strict)** 채택
- 활용 변이 collapse 시 ∩=4 (loose, "대응하는"≡"대응한", "설계해야"≡"설계하고")
  는 **informative only** — 본 mini-table 공식 집계 아님
- P3 재평가 ticket: "활용 변이 병합 옵션 재검토" — DR-4 임계 재상향 논의와 묶음

**판정**: 3 primary 모두 ∩ ≥ 3 (강한 매칭, strict 기준). 402 ∩=3, 315 ∩=3,
330 ∩=6. N9 와 동급 robustness. (c) gap 0건. N1·N7·N8 의 (c)/=2 hit 분포와
다르게 N2 는 axis 자연 정합으로 강 margin 확보.

### DR-5(a) — Cross-standard primary ISA ≥ 2

| primary chunk_id | isa_no |
|---|---|
| 402:04010:9 | 402 |
| 315:02482:22 | 315 |
| 330:03680:6 | 330 |

unique ISAs = {402, 315, 330} = **3 개** → DR-5(a) ✓ (3 ISA cross,
N1 ↔ N9 와 동급 wide-cross 형태).

### DR-5(b) — Cross 쿼리 간 primary disjoint (NIT-N6)

기 작성 cross oracle primary union (4 oracles):
- N1 (Q27): {500:04351:6, 330:03681:7, 450:04218:8} (3)
- N7 (Q33): {250:01628:22, 240:01098:22} (2)
- N8 (Q34): {260:01824:2, 265:02105:9} (2)
- N9 (Q35): {550:06012:18, 240:01102:24} (2)

union = 9 chunks. 본 N2 primary {402:04010:9, 315:02482:22, 330:03680:6} 와
차집합 = ∅ 교집합 → DR-5(b) ✓.

**§6/§7 parent-child proximity 경계 사항** (DA 2026-04-19 DM):
- `330:03680:6` (N2) ≠ `330:03681:7` (N1) — chunk_id ordinal 다름 (3680 vs 3681)
- 단 두 chunk 는 **parent-child 의미 관계**: §6 umbrella ("추가감사절차 성격·시기·범위 설계") + §7 detail ("설계 시 유의사항")
- BGE 임베딩 시 semantic proximity 잠재 → P5 S4 retrofit audit "semantic
  proximity artefact" diagnostic 컬럼 추가 추적
- 두 oracle query verb stem 분화 ("입수·커뮤니케이션" N1 vs "설계" N2) 로
  surface 회수 분리 의도
- 본 N2 가 DR-5(b) parent-child proximity **pilot instance** — P5 audit 결과
  로 DR-5(b) 운용 절차 보강 사유 (P9 plan diff log 별도 항목)

### DR 체크리스트

```text
[✓] DR-1 — Intro-parent stub 없음
    근거: 3 primary cc 211/216/178 (모두 substantive). 315:12 stub swap 처리.
[✓] DR-2 — Resolver 매핑 로그 첨부
    근거: concrete chunk_id 직접 (N/A). 402:9 본문 "감사기준서 315에 따라" bonus.
[✓] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: paragraph_ids 모두 numeric ["9"]/["22"]/["6"]
[✓] DR-4 — Query phrasing ↔ primary framing 일치
    근거: 402 ∩=3, 315 ∩=3, 330 ∩=6 (보수적 4) — 모두 ≥ 3 강 margin
[✓] DR-5(a) (cross) — primary ISA 수 ≥ 2
    근거: unique ISAs = {402, 315, 330} = 3 (wide-cross)
[✓] DR-5(b) (cross, NIT-N6) — 다른 cross 와 primary disjoint
    근거: N1 ∪ N7 ∪ N8 ∪ N9 union 9 chunks 와 ∅ 교집합
    경계: 330:6 vs 330:7 parent-child proximity (P5 S4 diagnostic 추적)
```

→ 6 항목 전수 ✓. (c) intentional gap 0건. small-ISA 위험 없음 (402 hub-class,
315/330 mega-class). DR-5(b) parent-child proximity 경계 P5 추적 항목.

### S4 prescreen 측정 보류 (P5 일괄)

N1/N7/N8/N9 와 동일 — P5 audit 시점 v3 24 신규 primary 일괄 측정 + §6/§7
proximity diagnostic 컬럼 추가.

### DR-4 robustness margin 비교 (DA P7 분석 조건 입력)

DA N7 spot-check §1 P7 분석 조건 누적 입력:

| oracle | primary chunk_id | ∩ | margin 분류 |
|---|---|---:|---|
| N1 (Q27) | 500:04351:6 | 4 | ≥ 3 |
| N1 (Q27) | 330:03681:7 | 1 | (c) intentional |
| N1 (Q27) | 450:04218:8 | 2 | =2 hit |
| N7 (Q33) | 250:01628:22 | 2 | =2 hit |
| N7 (Q33) | 240:01098:22 | 2 | =2 hit |
| N8 (Q34) | 260:01824:2 | 3 | ≥ 3 |
| N8 (Q34) | 265:02105:9 | 5 | ≥ 3 |
| N9 (Q35) | 550:06012:18 | 6 | ≥ 3 |
| N9 (Q35) | 240:01102:24 | 6 | ≥ 3 |
| N2 (Q28) | 402:04010:9 | 3 | ≥ 3 |
| N2 (Q28) | 315:02482:22 | 3 | ≥ 3 |
| N2 (Q28) | 330:03680:6 | 6 (strict; loose 4 informative only) | ≥ 3 |

현 누적 (5/9 oracle, 12 primary): ≥ 3 margin = 8 / =2 hit = 3 / (c) = 1.
P7 t-test sample size: ≥3 vs =2 = 8 vs 3 (n_total=11, 단 oracle 단위 평균
recall@5 비교 시 5 vs 3 oracle, 추후 sample-size 검토 필요).

---

## Q29 — N3: 그룹재무제표 감사 RMM ↔ 부문중요성 (600↔315)

```yaml
id: Q29
category: cross-standard
query: "감사인은 그룹재무제표 감사에서 그룹·부문과 그 환경에 대한 이해를 바탕으로 중요왜곡표시위험을 어느 수준에서 식별·평가하며, 유의적 부문에 대해서는 부문중요성을 사용하여 부문재무정보 감사를 어떻게 수행하여야 하는가?"
expected_primary_chunks:
  - "600:06962:17"
  - "600:06990:26"
  - "315:02485:23"
expected_related_chunks:
  - "600:06964:18"   # ISA 600 ¶18 그룹·부문 환경 이해 추가절차
  - "600:06992:27"   # ISA 600 ¶27 비유의적 부문 분석적절차
  - "315:02482:22"   # ISA 315 ¶22 통제 미비점 (N2 primary, related 중복 허용; cross-oracle adjacent ¶ → P-2)
  - "315:02498:27"   # ISA 315 ¶27 유의적 위험 결정 (N6 primary 후보)
notes: |
  Cross-standard "그룹감사 RMM × 부문중요성" 축. 600 (그룹감사 framework) →
  315 (RMM 식별·평가 일반) 의 cross application.

  ## Option D 적용 (DR-5(c) 신규 조항, 2026-04-19)
  N3 primary 3 chunk 모두 section=requirements (Option D 준수).
  315:11 (objective, cc=163, generic ISA 315 목적 선언) 후보 결격 →
  315:23 (requirements, cc=165, RMM 식별 framework) 채택.
  plan §4.2 line 84 정정 single-DR-change combined diff log 등록 (P9).

  ## DR-4 query enhancement justification (DA 2-test precedent, 2026-04-19)
  315:23 ∩ pre-estimate (strict surface, top-20) =3 정확 임계 hit
  ({감사인은, 중요왜곡표시위험을, 식별}) → 쿼리 보강 검토 trigger.

  DA 2-test 판정 (2026-04-19 17:35):
  1. **Axis 확장 test**: 쿼리 보강 ("어느 수준에서 식별·평가") 은 §23 본문
     핵심 axis (재무제표 수준 vs 경영진주장 수준) **확장** — DR-4 gaming 아님.
  2. **자연 phrasing test**: 보강 phrasing 은 감사인 실무 질문 자연 형식
     유지, 인위적 토큰 stacking 아님.
  3. **보강 token 출처 test**: {수준, 식별, 평가} 모두 §23 본문 top-20
     freq token 내 실재 surface token — artificial stacking 아님.
  → 2-test 통과, (a) 쿼리 보강 수락.

  Pre-estimate ∩=3 → 실측 ∩ (strict surface) 보강 후 재검증 값:
  enhanced_intersection_post_query_expansion: 4 (DE 사전 측정, P5 시 재확인)
  enhanced: true   # P5 retrofit_audit.py 정합성 signal 컬럼 입력
  # DR-6 (P3 신규 조항 후보) 1st precedent

  ## Cross-oracle proximity (2nd instance, P5 S4 diagnostic)
  N3 primary 315:02485:23 (¶23) 은 N2 primary 315:02482:22 (¶22) 와
  동일 ISA 315 인접 ¶ — cross-oracle adjacent.
  BGE semantic embedding 에서 N2-쿼리 top-5 ↔ N3-primary 상호 회수
  가능성 (contamination). P5 S4 diagnostic "cross-oracle proximity"
  subtype 추적.

  monitored_pair:
    pair_id: "P-2"
    oracles: ["N2", "N3"]
    isa: "315"
    paragraph_distance: 1        # §22 vs §23
    block_ordinal_distance: 3    # 2482 vs 2485
    section_A: "requirements"
    section_B: "requirements"
    heading_prefix_depth: 3      # ISA 315 > 요구사항 > RMM 식별·평가
    proximity_subtype: "cross-oracle adjacent"

  ## DR 7/7 ✓ (DR-5 3 sub-rule)
  DR-1: cc 175/228/165 모두 substantive
  DR-2: concrete chunk_id 직접 (N/A)
  DR-3: paragraph_ids ["17"]/["26"]/["23"] all numeric, (i) 0건
  DR-4: ∩ pre-estimate 모두 ≥3 (보강 후 600:17=5, 600:26=8, 315:23=4)
  DR-5(a): 2 ISA cross {600, 315} ✓
  DR-5(b): union 12 chunks (N1+N2+N7+N8+N9) 와 ∅
  DR-5(c) Option D: 3 primary 모두 section=requirements ✓
```

### Evidence — chunks.jsonl 원문 (3 primary)

```jsonl
# Primary 1 — 600:06962:17 (요구사항, char_count=175)
chunk_id="600:06962:17"  isa_no=600  section=requirements  block_ordinal=6962
heading_trail=[
  "감사기준서 600  그룹재무제표 감사 – 부문감사인이 수행한 업무 등 특별 고려사항",
  "요구사항",
  "그룹∙부문과 그 환경에 대한 이해"
]
paragraph_ids=["17"]
text="감사기준서 600  그룹재무제표 감사 ... > 요구사항 > 그룹∙부문과 그
      환경에 대한 이해\n\n
      17. 감사인은 해당 실체와 그 환경, 해당 재무보고체계 및
      내부통제시스템을 이해함으로써 중요왜곡표시위험을 식별하고 평가하여야
      한다. 그룹업무팀은 다음의 절차를 수행하여야 한다."
refs=[]
```

```jsonl
# Primary 2 — 600:06990:26 (요구사항, char_count=228)
chunk_id="600:06990:26"  isa_no=600  section=requirements  block_ordinal=6990
heading_trail=[
  "감사기준서 600  그룹재무제표 감사 – 부문감사인이 수행한 업무 등 특별 고려사항",
  "요구사항",
  "평가된 위험에 대한 대응",
  "부문재무정보에 대하여 수행할 업무유형의 결정 (문단 A47 참조)",
  "유의적 부문"
]
paragraph_ids=["26"]
text="감사기준서 600  그룹재무제표 감사 ... > 요구사항 > 평가된 위험에 대한
      대응 > 부문재무정보에 대하여 수행할 업무유형의 결정 > 유의적 부문\n\n
      26. 그룹에 대한 개별적인 재무적 유의성으로 인하여 유의적인 부문에
      대해서는, 그룹업무팀 또는 그룹업무팀을 대신하는 부문감사인은
      부문중요성을 사용하여 부문재무정보에 대한 감사를 수행하여야 한다."
refs=[]
```

```jsonl
# Primary 3 — 315:02485:23 (요구사항, char_count=165)
chunk_id="315:02485:23"  isa_no=315  section=requirements  block_ordinal=2485
heading_trail=[
  "감사기준서 315  중요왜곡표시위험의 식별과 평가",
  "요구사항",
  "중요왜곡표시위험의 식별과 평가 (문단 A184-A185 참조)",
  "중요왜곡표시위험의 식별"
]
paragraph_ids=["23"]
text="감사기준서 315  중요왜곡표시위험의 식별과 평가 > 요구사항 >
      중요왜곡표시위험의 식별과 평가 > 중요왜곡표시위험의 식별\n\n
      23. 감사인은 중요왜곡표시위험을 식별하고 해당 위험이 다음 중 어느
      수준에서 존재하는지 결정하여야 한다. (문단 A186-A192 참조)"
refs=["A186","A187","A188","A189","A190","A191","A192"]
```

### Pilot 조건 5 — 3중 cross-reference 의무 (네 번째 instance)

| 출처 | 후보 | 정합 |
|---|---|---|
| plan §4.2 line 84 | N3 = `600:17, 600:26, 315:11` | base (단 315:11 DR-5(c) Option D 결격 → swap) |
| chunks.jsonl 실측 | `600:06962:17` ✓ / `600:06990:26` ✓ / `315:02409:11` cc=163 + section=objective + generic framing → swap → `315:02485:23` ✓ | swap 1건 (DA 2026-04-19 Option D 공식화 후) |
| 기 작성 cross primary union | N1 (3) ∪ N2 (3) ∪ N7 (2) ∪ N8 (2) ∪ N9 (2) = 12 chunks | N3 (3) ∩ union = ∅ ✓ (단 315:23 ↔ N2 315:22 cross-oracle adjacent ¶ — pair P-2 P5 추적) |

→ 3중 교차 통과 (plan §4.2 line 84 swap 정정 + cross-oracle proximity P-2 명시 포함). yaml block 작성 정당화.

### DR-1 — Intro-parent stub 검증 (NIT-N1 임계 ≤ 115)

| primary chunk_id | char_count | section | paragraph_ids | 본문 패턴 | stub? |
|---|---:|---|---|---|---|
| 600:06962:17 | 175 | requirements | ["17"] | "...해당 실체와 그 환경...중요왜곡표시위험을 식별하고 평가하여야 한다..." | ✗ |
| 600:06990:26 | 228 | requirements | ["26"] | "...유의적인 부문에 대해서는...부문중요성을 사용하여 부문재무정보에 대한 감사를 수행..." | ✗ |
| 315:02485:23 | 165 | requirements | ["23"] | "...중요왜곡표시위험을 식별하고 해당 위험이 다음 중 어느 수준에서 존재하는지 결정..." | ✗ |

**판정**: 3 primary 모두 cc > 115, 본문 substantive (RMM 식별·평가 framework, 부문중요성 적용 규칙, RMM 식별 결정 framework). → DR-1 ✓.

**Stub swap 기록**: `315:02409:11` (cc=163, section=objective, "이 감사기준서는 ...중요왜곡표시위험을 식별하고 평가...할 책임을 다룬다") → DR-5(c) Option C (cc ≥ 180 강제) 시도 후 cc=163 + objective generic framing 이중 fail → Option D 공식화 (objective 제외) → §23 swap.

### DR-2 — Resolver 매핑 로그 (logical path 미사용)

3 primary 모두 concrete chunk_id 직접 지정. → DR-2 ✓ (N/A).

### DR-3 — Alphabetical (i) vs Roman (i) 모호성 검증

paragraph_ids = `["17"]` / `["26"]` / `["23"]`. numeric, `(i)` 사용 0건. → DR-3 ✓.

### DR-4 — Query phrasing ↔ primary framing 정합 (NIT-N4 정량)

**쿼리 표면형 토큰** (공백 split, stopword 후, 23개):
```text
["감사인은", "그룹재무제표", "감사에서", "그룹·부문과", "그", "환경에", "대한",
 "이해를", "바탕으로", "중요왜곡표시위험을", "어느", "수준에서", "식별·평가하며,",
 "유의적", "부문에", "대해서는", "부문중요성을", "사용하여", "부문재무정보",
 "감사를", "어떻게", "수행하여야", "하는가?"]
```

(stopword 매칭 0건; 중복 0건. "그" 는 관형사 — stopword 목록 외 보존.)

**Primary mini-table** (각 primary top-20 ∩ query, strict surface-form):

| primary chunk_id | primary top-20 (요약) | 교집합 | 일치 (≥2) |
|---|---|---|---|
| 600:06962:17 | 감사기준서, 600, 그룹재무제표, 감사, 부문감사인이, >(2), 요구사항, 그룹∙부문과, 그, 환경에, 대한, 이해, 감사인은, 해당, 실체와, 환경,, 재무보고체계, 내부통제시스템을, 이해함으로써, 중요왜곡표시위험을, 식별하고, 평가하여야, 그룹업무팀은, 수행하여야 | {감사인은, 그, 그룹재무제표, 중요왜곡표시위험을, 수행하여야} = 5 | ✓ |
| 600:06990:26 | 감사기준서, 600, 그룹재무제표, 부문감사인이, >(4), 요구사항, 평가된, 위험에, 부문재무정보에, 부문, 유의적, 그룹에, 재무적, 유의성으로, 유의적인, 부문에, 대해서는, 그룹업무팀, 부문감사인은, 부문중요성을, 사용하여, 감사를, 수행하여야 | {그룹재무제표, 유의적, 부문에, 대해서는, 부문중요성을, 사용하여, 감사를, 수행하여야} = 8 | ✓ |
| 315:02485:23 | 감사기준서, 315, 중요왜곡표시위험의, 식별과, 평가, >(3), 요구사항, 식별, 감사인은, 중요왜곡표시위험을, 식별하고, 해당, 위험이, 다음, 중, 어느, 수준에서, 존재하는지, 결정하여야 | {감사인은, 중요왜곡표시위험을, 어느, 수준에서} = 4 | ✓ |

**Strict 정책 적용**: query_design_rules.md DR-4 § "strict surface form tokenization (공백 split, 형태소 분석 미적용)" 준수. **활용 변이 병합 미적용**.

**판정**: 3 primary 모두 ∩ ≥ 3 (강한 매칭, strict 기준). 600:17 ∩=5, 600:26 ∩=8, 315:23 ∩=4. (c) gap 0건. 단 315:23 는 DR-4 query enhancement 적용 사례 — DR-6 (P3 신규 조항 후보) **1st precedent**. yaml notes §"DA 2-test" 정당화 기록 참조.

### DR-5(a) — Cross-standard primary ISA ≥ 2 (Option D 적용)

| primary chunk_id | isa_no | section |
|---|---|---|
| 600:06962:17 | 600 | requirements |
| 600:06990:26 | 600 | requirements |
| 315:02485:23 | 315 | requirements |

unique ISAs = {600, 315} = **2 개** → DR-5(a) ✓.

**ISA 분포 의도**: 600 (그룹감사 framework) 의 RMM 식별 (¶17) + 부문중요성 적용 (¶26) **2 step within 600** + 315 (RMM 일반 framework) 1 primary. 그룹감사 specific × RMM 일반 cross-application 표현. (small-cross 형태, N6 와 동급 분포.)

### DR-5(b) — Cross 쿼리 간 primary disjoint (NIT-N6)

기 작성 cross oracle primary union (5 oracles):
- N1 (Q27): {500:04351:6, 330:03681:7, 450:04218:8} (3)
- N2 (Q28): {402:04010:9, 315:02482:22, 330:03680:6} (3)
- N7 (Q33): {250:01628:22, 240:01098:22} (2)
- N8 (Q34): {260:01824:2, 265:02105:9} (2)
- N9 (Q35): {550:06012:18, 240:01102:24} (2)

union = 12 chunks. 본 N3 primary {600:06962:17, 600:06990:26, 315:02485:23} 와
차집합 = ∅ 교집합 → DR-5(b) ✓.

**Cross-oracle adjacent ¶ proximity 경계 사항** (DA 2026-04-19 DM, 2nd instance):
- `315:02485:23` (N3) ↔ `315:02482:22` (N2) — chunk_id ordinal 다름 (2485 vs 2482, ¶ distance 1)
- 동일 ISA 315 + 동일 heading_trail prefix depth=3 ("ISA 315 > 요구사항 > RMM 식별·평가")
- BGE 임베딩 시 semantic proximity 잠재 → P5 S4 retrofit audit "cross-oracle proximity" subtype diagnostic 추가 추적
- 두 oracle query topic 분화 (N2 "통제 미비점 식별" / N3 "RMM 식별 수준 결정") 로 surface 회수 분리 의도
- 본 N3 가 cross-oracle adjacent ¶ proximity **1st instance** (P-1 "within-oracle parent-child" schema reserved — 현재 해당 case 없음, 미래 대비; DA 2026-04-19 Clarification 2 반영) — P5 audit 결과로 monitored_pair schema 운용 사유 (P9 plan diff log 별도 항목)

### DR-5(c) — Option D (objective 제외) (2026-04-19 신규 조항)

**Option D**: cross-standard primary 적격 section ∈ {requirements, application, definitions} (objective 제외).

| primary chunk_id | section | Option D PASS |
|---|---|---|
| 600:06962:17 | requirements | ✓ |
| 600:06990:26 | requirements | ✓ |
| 315:02485:23 | requirements | ✓ |

→ 3/3 PASS. 본 N3 가 Option D 조항 적용 **pilot precedent** (315:11 → 315:23 swap 사례).

### DR 체크리스트

```text
[✓] DR-1 — Intro-parent stub 없음
    근거: 3 primary cc 175/228/165 (모두 substantive). 315:11 stub swap 처리.
[✓] DR-2 — Resolver 매핑 로그 첨부
    근거: concrete chunk_id 직접 (N/A).
[✓] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: paragraph_ids 모두 numeric ["17"]/["26"]/["23"]
[✓] DR-4 — Query phrasing ↔ primary framing 일치
    근거: 600:17 ∩=5, 600:26 ∩=8, 315:23 ∩=4 (보강 후) — 모두 ≥ 3 margin
        DR-6 precedent (P3 신규 조항 후보): 315:23 query enhancement 정당화 기록 yaml notes §DA 2-test
[✓] DR-5(a) (cross) — primary ISA 수 ≥ 2
    근거: unique ISAs = {600, 315} = 2 (small-cross, 600 specific × 315 general application)
[✓] DR-5(b) (cross, NIT-N6) — 다른 cross 와 primary disjoint
    근거: N1 ∪ N2 ∪ N7 ∪ N8 ∪ N9 union 12 chunks 와 ∅ 교집합
    경계: 315:23 vs N2 315:22 cross-oracle adjacent ¶ (P-2, P5 S4 diagnostic 추적)
[✓] DR-5(c) (cross, Option D) — primary section ∈ {requirements, application, definitions}
    근거: 3 primary 모두 section=requirements (Option D PASS, pilot precedent)
```

→ 7 항목 (DR-5 3 sub-rule) 전수 ✓. (c) intentional gap 0건. small-ISA 위험 없음 (600 hub-class, 315 mega-class). cross-oracle adjacent ¶ proximity 경계 P5 추적 항목.

### S4 prescreen 측정 보류 (P5 일괄)

N1/N2/N7/N8/N9 와 동일 — P5 audit 시점 v3 24 신규 primary 일괄 측정 + cross-oracle adjacent ¶ proximity diagnostic 컬럼 추가.

### DR-4 robustness margin 비교 (DA P7 분석 조건 입력)

DA N7 spot-check §1 P7 분석 조건 누적 입력:

| oracle | primary chunk_id | ∩ | margin 분류 |
|---|---|---:|---|
| N1 (Q27) | 500:04351:6 | 4 | ≥ 3 |
| N1 (Q27) | 330:03681:7 | 1 | (c) intentional |
| N1 (Q27) | 450:04218:8 | 2 | =2 hit |
| N7 (Q33) | 250:01628:22 | 2 | =2 hit |
| N7 (Q33) | 240:01098:22 | 2 | =2 hit |
| N8 (Q34) | 260:01824:2 | 3 | ≥ 3 |
| N8 (Q34) | 265:02105:9 | 5 | ≥ 3 |
| N9 (Q35) | 550:06012:18 | 6 | ≥ 3 |
| N9 (Q35) | 240:01102:24 | 6 | ≥ 3 |
| N2 (Q28) | 402:04010:9 | 3 | ≥ 3 |
| N2 (Q28) | 315:02482:22 | 3 | ≥ 3 |
| N2 (Q28) | 330:03680:6 | 6 (strict; loose 4 informative only) | ≥ 3 |
| N3 (Q29) | 600:06962:17 | 5 | ≥ 3 |
| N3 (Q29) | 600:06990:26 | 8 | ≥ 3 |
| N3 (Q29) | 315:02485:23 | 4 (DR-6 enhanced; pre-estimate 3) | ≥ 3 |

현 누적 (6/9 oracle, 15 primary): ≥ 3 margin = 11 / =2 hit = 3 / (c) = 1.
P7 t-test sample size: ≥3 vs =2 = 11 vs 3 (n_total=14, oracle 단위 평균
recall@5 비교 시 6 vs 3 oracle, 추후 sample-size 검토 필요).

---

## Q30 — N4: 미수정왜곡표시 평가 ↔ 감사의견 변형 chain (450↔700↔705)

```yaml
id: Q30
category: cross-standard
query: "감사인은 감사 중 식별된 왜곡표시가 재무제표에 개별적으로 또는 집합적으로 중요하며 동시에 전반적이라고 결론을 내리는 경우 부적정의견을 표명하여야 하며, 공정표시체계의 요구사항에 따라 작성된 재무제표가 공정한 표시목적을 달성하지 못하는 경우 감사기준서 705에 따라 감사의견을 변형시킬 필요가 있는지 여부를 어떻게 결정하며, 감사 중 식별된 미수정왜곡표시가 개별적으로 또는 집합적으로 중요한지 어떻게 평가하여야 하는가?"
expected_primary_chunks:
  - "705:08655:8"
  - "700:08024:18"
  - "450:04222:11"
expected_related_chunks:
  - "705:08691:21"   # ISA 705 ¶21 감사의견근거 단락 (N5 primary 후보; cross-oracle adjacent ¶ → P-4)
  - "700:08044:26"   # ISA 700 ¶26 계속기업 별도 단락 (N5 primary 후보)
  - "450:04218:8"    # ISA 450 ¶8 식별된 왜곡표시 누적 (N1 primary; cross-oracle adjacent ¶ → P-3)
  - "705:08646:6"    # ISA 705 ¶6 변형의견 stub (deep-stub, plan §4.2 base 후보 — DR-1 fail 기록)
  - "700:08021:17"   # ISA 700 ¶17 변형의견 결정 stub (deep-stub, plan §4.2 base 후보 — DR-1 fail 기록)
notes: |
  Cross-standard "왜곡표시 → 의견변형 → 부적정의견" 3-stage chain 축.
  450 (미수정왜곡표시 평가) → 700 (의견형성, 705 delegating) → 705 (부적정의견
  표명) 의 cross-standard chain. **3 ISA full-cross** (small-cross 아님).

  ## Option α 적용 (N4 swap 2건, 2026-04-19)
  plan §4.2 line 86 (N4: `705:6, 450:11, 700:17`) base 의 705:6 + 700:17 가
  모두 deep-stub (cc=86, cc=101) → DR-1 fail. DA 2-test 검증 후 Option α 채택:
    - 705:6 (cc=86, "감사인은 감사의견을 변형시킬 수 있다" 일반선언) →
      705:8 (cc=157, requirements §"부적정의견" 본문 "왜곡표시가 ... 중요하며
      동시에 전반적이라고 결론 내리는 경우 부적정의견 표명")
    - 700:17 (cc=101, "감사인은 ... 705 에 따라 변형시킬 필요" 단순 cross-ref) →
      700:18 (cc=234, "공정표시체계 요구사항 미충족 시 705 에 따라 감사의견
      변형시킬 필요 결정") — body cross-ref to 705 보존 (refs=["A16"])
    - 450:11 (cc=143, "미수정왜곡표시 ... 개별적으로 또는 집합적으로 중요한지
      여부 결정") — base 유지

  Option β (705:6+700:17 keep) 기각 근거: deep-stub primary 는 retrieval 시
  noise 만 회수 (axis surface token 부재). plan §4.2 base 가 chunks.jsonl
  실측 미반영 → semantic-drift pattern (N3 315:11 → N4 705:6+700:17 → N5
  700:26 = 3 연속 swap, P9 plan diff log meta note 권고 — DA peer endorsed).

  ## DR-2 cross-ref signal 강 (700:18 → 705 delegating clause)
  700:18 본문 "감사기준서 705에 따라 감사의견을 변형시킬 필요가 있는지 여부를
  결정하여야 한다" 는 700 → 705 delegating clause. N4 chain "왜곡표시 →
  의견변형" 의 핵심 hub edge. retrieval 시 700:18 의 cross-ref 신호가
  705:8 hit 을 강화 (chain coherence 보강). DR-2 evidence 의 paradigm case.

  ## DR-4 query enhancement 적용 (DR-6 P3 후보 2nd precedent, 2026-04-19)
  pre-estimate (단순 query): 700:18 ∩ ≈ 2 (감사인은, 재무제표에) — DR-6
  trigger zone {2, 3} 진입.
  DA 2-test 판정:
  1. **Axis 확장 test**: "공정표시체계 요구사항 + 감사기준서 705 에 따라
     감사의견을 변형" 추가는 700:18 본문 axis (공정표시 fairness 위반 →
     ISA 705 변형 결정) 의 명시적 표현 — axis 확장 ✓ (gaming 아님)
  2. **자연 phrasing test**: "공정표시체계 요구사항 ... 표시목적 달성하지
     못하는 경우 감사기준서 705 에 따라 변형" 은 감사인 실무 자연 형식 ✓
  3. **보강 token 출처 test**: {공정표시체계의, 요구사항에, 작성된,
     재무제표가, 공정한, 표시목적을, 달성하지, 감사기준서, 705에, 감사의견을,
     변형시킬, 필요가, 있는지, 여부를} 모두 700:18 본문 top-20 freq token
     실재 — artificial stacking 아님 ✓
  → 2-test 통과, query enhancement 수락 (DR-6 P3 후보 2nd precedent).

  Pre-estimate 700:18 ∩=2 → 보강 후 ∩=14:
  enhanced_intersection_post_query_expansion: 14
  enhanced: true   # P5 retrofit_audit.py 정합성 signal 컬럼

  ## Cross-oracle proximity (3rd, 4th instance — N1·N5 인접)
  N4 primary 2건이 cross-oracle adjacent ¶ proximity 발생:

  monitored_pair_a:
    pair_id: "P-3"
    oracles: ["N1", "N4"]
    isa: "450"
    paragraph_distance: 3        # ¶8 vs ¶11
    block_ordinal_distance: 4    # 4218 vs 4222
    section_A: "requirements"
    section_B: "requirements"
    heading_prefix_depth: 2      # ISA 450 > 요구사항
    proximity_subtype: "cross-oracle adjacent"
    notes: "N1 450:8 (식별된 왜곡표시 그룹화/누적) ↔ N4 450:11 (미수정왜곡표시
            중요성 평가) — chain 상 직전 단계 정합. axis 분화 (N1 누적 절차 /
            N4 중요성 결정) 로 surface 회수 분리 의도."

  monitored_pair_b:
    pair_id: "P-4"
    oracles: ["N4", "N5"]
    isa: "705"
    paragraph_distance: 13       # ¶8 vs ¶21
    block_ordinal_distance: 36   # 8655 vs 8691
    section_A: "requirements"
    section_B: "requirements"
    heading_prefix_depth: 2      # ISA 705 > 요구사항
    proximity_subtype: "cross-oracle distant-same-ISA"
    notes: "동일 ISA 705 내 distant ¶ — 부적정의견 본문 (N4) vs 감사의견근거
            단락 (N5). heading_trail 후속 segment 분화 (감사의견에 대한 변형 /
            의견이 변형된 경우 형태와 내용). semantic proximity 약 — P-2/P-3
            대비 위험 낮음. 단 ISA 705 hit cluster 형성 시 N4↔N5 cross-oracle
            confusion 가능성 배제 불가."

  ## DR 7/7 ✓ (DR-5 3 sub-rule)
  DR-1: cc 157/234/143 모두 substantive (705:6 stub + 700:17 stub swap)
  DR-2: 700:18 → 705 cross-ref strong (delegating clause, refs=["A16"])
  DR-3: paragraph_ids ["8"]/["18"]/["11"] all numeric, (i) 0건
  DR-4: ∩ pre-estimate {2, 14, ?} → 보강 후 700:18=14 (DR-6 2nd precedent)
        실측 ∩ 보강 후 705:8=14, 700:18=14, 450:11=10
  DR-5(a): 3 ISA full-cross {705, 700, 450} — N1 (3 ISA) 와 동급 분포
  DR-5(b): N1+N2+N3+N7+N8+N9 union 15 chunks 와 ∅ 교집합
  DR-5(c) Option D: 3 primary 모두 section=requirements ✓
```

### Evidence — chunks.jsonl 원문 (3 primary)

```jsonl
# Primary 1 — 705:08655:8 (요구사항, char_count=157) — Option α swap from 705:6
chunk_id="705:08655:8"  isa_no=705  section=requirements  block_ordinal=8655
heading_trail=[
  "감사기준서 705  감사의견의 변형",
  "요구사항",
  "감사의견에 대한 변형 유형의 결정",
  "부적정의견"
]
paragraph_ids=["8"]
text="감사기준서 705  감사의견의 변형 > 요구사항 > 감사의견에 대한 변형
      유형의 결정 > 부적정의견\n\n
      8. 감사인은 충분하고 적합한 감사증거를 입수한 결과 왜곡표시가
      재무제표에 개별적으로 또는 집합적으로 중요하며 동시에 전반적이라고
      결론을 내리는 경우 부적정의견을 표명하여야 한다."
refs=[]
```

```jsonl
# Primary 2 — 700:08024:18 (요구사항, char_count=234) — Option α swap from 700:17
chunk_id="700:08024:18"  isa_no=700  section=requirements  block_ordinal=8024
heading_trail=[
  "감사기준서 700  재무제표에 대한 의견형성과 보고",
  "요구사항",
  "의견의 형태"
]
paragraph_ids=["18"]
text="감사기준서 700  재무제표에 대한 의견형성과 보고 > 요구사항 > 의견의
      형태\n\n
      18. 공정표시체계의 요구사항에 따라 작성된 재무제표가 공정한 표시목적을
      달성하지 못하고 있는 경우, 감사인은 경영진과 이 사항을 논의하여야 한다.
      또한, 감사인은 해당 재무보고체계의 요구사항과 해당 사항이 해결되는
      방법을 고려하여 감사기준서 705에 따라 감사의견을 변형시킬 필요가 있는지
      여부를 결정하여야 한다. (문단 A16 참조)"
refs=["A16"]
```

```jsonl
# Primary 3 — 450:04222:11 (요구사항, char_count=143) — base 유지
chunk_id="450:04222:11"  isa_no=450  section=requirements  block_ordinal=4222
heading_trail=[
  "감사기준서 450  감사 중 식별된 왜곡표시의 평가",
  "요구사항",
  "미수정왜곡표시의 영향에 대한 평가"
]
paragraph_ids=["11"]
text="감사기준서 450  감사 중 식별된 왜곡표시의 평가 > 요구사항 >
      미수정왜곡표시의 영향에 대한 평가\n\n
      11. 감사인은 미수정왜곡표시가 개별적으로 또는 집합적으로 중요한지
      여부를 결정하여야 한다. 이를 결정하기 위하여 감사인은 다음 사항을
      고려하여야 한다."
refs=[]
```

### Pilot 조건 5 — 3중 cross-reference 의무 (다섯 번째 instance)

| 출처 | 후보 | 정합 |
|---|---|---|
| plan §4.2 line 86 | N4 = `705:6, 450:11, 700:17` | base (705:6 cc=86 deep-stub + 700:17 cc=101 deep-stub → 2 swap) |
| chunks.jsonl 실측 | `705:08655:8` ✓ cc=157 / `700:08024:18` ✓ cc=234 + refs=["A16"] / `450:04222:11` ✓ cc=143 | swap 2건 (DA 2026-04-19 Option α) |
| 기 작성 cross primary union | N1 (3) ∪ N2 (3) ∪ N3 (3) ∪ N7 (2) ∪ N8 (2) ∪ N9 (2) = 15 chunks | N4 (3) ∩ union = ∅ ✓ (단 N4 450:11 ↔ N1 450:8 cross-oracle adjacent ¶ — P-3 / N4 705:8 ↔ N5 705:21 cross-oracle distant-same-ISA — P-4) |

→ 3중 교차 통과 (plan §4.2 line 86 swap 2 정정 + cross-oracle proximity P-3/P-4 명시 포함). yaml block 작성 정당화.

### DR-1 — Intro-parent stub 검증 (NIT-N1 임계 ≤ 115)

| primary chunk_id | char_count | section | paragraph_ids | 본문 패턴 | stub? |
|---|---:|---|---|---|---|
| 705:08655:8 | 157 | requirements | ["8"] | "...왜곡표시가 ... 중요하며 동시에 전반적이라고 결론 내리는 경우 부적정의견을 표명..." | ✗ |
| 700:08024:18 | 234 | requirements | ["18"] | "...공정표시체계 요구사항 미충족 시 ... 감사기준서 705에 따라 감사의견을 변형시킬 필요 결정..." | ✗ |
| 450:04222:11 | 143 | requirements | ["11"] | "...미수정왜곡표시가 개별적으로 또는 집합적으로 중요한지 여부 결정..." | ✗ |

**판정**: 3 primary 모두 cc > 115, 본문 substantive (부적정의견 표명 조건, 공정표시 미충족 → 705 변형 결정, 미수정왜곡표시 중요성 평가). → DR-1 ✓.

**Stub swap 기록 2건**:
- `705:08646:6` (cc=86, requirements, "감사인은 감사의견을 변형시킬 수 있다" 일반선언) → DR-1 fail (cc < 115) → §8 swap (cc=157, 부적정의견 본문)
- `700:08021:17` (cc=101, requirements, "감사인은 ... 705 에 따라 ... 변형시킬 필요" 단순 cross-ref stub) → DR-1 fail (cc < 115) → §18 swap (cc=234, 공정표시 미충족 본문, body cross-ref to 705 보존)

semantic-drift pattern 사례: plan §4.2 base (705:6 + 700:17) 가 retrieval coverage 가능 chunk 가 아닌 deep-stub 지정 → P9 plan diff log meta note 4번째 swap entry.

### DR-2 — Resolver 매핑 로그 (logical path 미사용) — body cross-ref 강

3 primary 모두 concrete chunk_id 직접 지정. → DR-2 ✓ (resolver path N/A).

**Body cross-ref 신호 (DR-2 axis 정당화 paradigm case)**:
- `700:08024:18` 본문: "감사기준서 705에 따라 감사의견을 변형시킬 필요가 있는지 여부를 결정하여야 한다" → 700 → 705 delegating clause. N4 chain "의견변형 결정 → 부적정의견 표명" 의 hub edge.
- refs=["A16"] (application 문단 reference) — N4 axis 의 application support.
- `450:04222:11` 본문: 후속 ¶12-15 와 chain (미수정왜곡표시 누적/평가 절차 분기) — P5 retrieval 시 ISA 450 cluster 회수 가능성 ↑.

### DR-3 — Alphabetical (i) vs Roman (i) 모호성 검증

paragraph_ids = `["8"]` / `["18"]` / `["11"]`. numeric, `(i)` 사용 0건. → DR-3 ✓.

### DR-4 — Query phrasing ↔ primary framing 정합 (NIT-N4 정량)

**쿼리 표면형 토큰** (공백 split, stopword 후, unique 36개):
```text
["감사인은", "감사", "중", "식별된", "왜곡표시가", "재무제표에", "개별적으로",
 "또는", "집합적으로", "중요하며", "동시에", "전반적이라고", "결론을", "내리는",
 "경우", "부적정의견을", "표명하여야", "하며,", "공정표시체계의", "요구사항에",
 "따라", "작성된", "재무제표가", "공정한", "표시목적을", "달성하지", "못하는",
 "감사기준서", "705에", "감사의견을", "변형시킬", "필요가", "있는지", "여부를",
 "어떻게", "결정하며,", "미수정왜곡표시가", "중요한지", "평가하여야", "하는가?"]
```

(중복 제거: "감사" 2회, "중" 2회, "식별된" 2회, "개별적으로" 2회, "또는" 2회, "집합적으로" 2회, "어떻게" 3회, "경우" 2회. stopword 매칭 0건.)

**Primary mini-table** (각 primary top-20 ∩ query, strict surface-form):

| primary chunk_id | primary top-20 (요약) | 교집합 | 일치 (≥2) |
|---|---|---|---|
| 705:08655:8 | 감사기준서, 705, 감사의견의, 변형, 요구사항, 감사의견에, 변형, 유형의, 결정, 부적정의견, 8., 감사인은, 충분하고, 적합한, 감사증거를, 입수한, 결과, 왜곡표시가, 재무제표에, 개별적으로, 또는, 집합적으로, 중요하며, 동시에, 전반적이라고, 결론을, 내리는, 경우, 부적정의견을, 표명하여야 | {감사인은, 왜곡표시가, 재무제표에, 개별적으로, 또는, 집합적으로, 중요하며, 동시에, 전반적이라고, 결론을, 내리는, 경우, 부적정의견을, 표명하여야} = 14 | ✓ |
| 700:08024:18 | 감사기준서, 700, 재무제표에, 대한, 의견형성과, 보고, 요구사항, 의견의, 형태, 18., 공정표시체계의, 요구사항에, 따라, 작성된, 재무제표가, 공정한, 표시목적을, 달성하지, 못하고, 있는, 경우,, 감사인은, 경영진과, 이, 사항을, 논의하여야, 또한,, 해당, 재무보고체계의, 요구사항과, 해결되는, 방법을, 고려하여, 705에, 감사의견을, 변형시킬, 필요가, 있는지, 여부를, 결정하여야 | {감사인은, 재무제표에, 공정표시체계의, 요구사항에, 따라, 작성된, 재무제표가, 공정한, 표시목적을, 달성하지, 감사기준서, 705에, 감사의견을, 변형시킬, 필요가, 있는지, 여부를} = 17 (DR-6 enhanced; pre-estimate 2) | ✓ |
| 450:04222:11 | 감사기준서, 450, 감사, 중, 식별된, 왜곡표시의, 평가, 요구사항, 미수정왜곡표시의, 영향에, 대한, 11., 감사인은, 미수정왜곡표시가, 개별적으로, 또는, 집합적으로, 중요한지, 여부를, 결정하여야, 이를, 결정하기, 위하여, 다음, 사항을, 고려하여야 | {감사인은, 감사, 중, 식별된, 미수정왜곡표시가, 개별적으로, 또는, 집합적으로, 중요한지, 여부를} = 10 | ✓ |

**Strict 정책 적용**: query_design_rules.md DR-4 § "strict surface form tokenization (공백 split, 형태소 분석 미적용)" 준수. **활용 변이 병합 미적용** (예: "왜곡표시가" ≠ "왜곡표시의", "결정하며," ≠ "결정하여야", "못하는" ≠ "못하고").

**판정**: 3 primary 모두 ∩ ≥ 10 (강한 매칭, strict 기준). 705:8 ∩=14, 700:18 ∩=17 (보강 후), 450:11 ∩=10. (c) gap 0건. 단 700:18 는 DR-4 query enhancement 적용 사례 — DR-6 (P3 신규 조항 후보) **2nd precedent**. yaml notes §"DA 2-test" 정당화 기록 참조 (N3 Q29 1st precedent 와 동일 procedure).

### DR-5(a) — Cross-standard primary ISA ≥ 2 (Option D 적용)

| primary chunk_id | isa_no | section |
|---|---|---|
| 705:08655:8 | 705 | requirements |
| 700:08024:18 | 700 | requirements |
| 450:04222:11 | 450 | requirements |

unique ISAs = {705, 700, 450} = **3 개** → DR-5(a) ✓.

**ISA 분포 의도**: 450 (왜곡표시 평가 framework) → 700 (의견형성, 705 delegating) → 705 (부적정의견 표명) **3-stage chain** (450 식별/평가 → 700 결정 → 705 표명). N1 과 동급 full-cross 분포 (N1 = {500, 330, 450}).

### DR-5(b) — Cross 쿼리 간 primary disjoint (NIT-N6)

기 작성 cross oracle primary union (6 oracles):
- N1 (Q27): {500:04351:6, 330:03681:7, 450:04218:8} (3)
- N2 (Q28): {402:04010:9, 315:02482:22, 330:03680:6} (3)
- N3 (Q29): {600:06962:17, 600:06990:26, 315:02485:23} (3)
- N7 (Q33): {250:01628:22, 240:01098:22} (2)
- N8 (Q34): {260:01824:2, 265:02105:9} (2)
- N9 (Q35): {550:06012:18, 240:01102:24} (2)

union = 15 chunks. 본 N4 primary {705:08655:8, 700:08024:18, 450:04222:11} 와
차집합 = ∅ 교집합 → DR-5(b) ✓.

**Cross-oracle adjacent ¶ proximity 경계 사항** (DA 2026-04-19 DM, 3rd-4th instance):
- `450:04222:11` (N4) ↔ `450:04218:8` (N1) — 동일 ISA 450, ¶ distance 3, block_ordinal distance 4, heading_trail prefix depth=2 ("ISA 450 > 요구사항") → cross-oracle adjacent ¶ (P-3)
- `705:08655:8` (N4) ↔ `705:08691:21` (N5) — 동일 ISA 705, ¶ distance 13, block_ordinal distance 36, heading_trail prefix depth=2 후속 segment 분화 → cross-oracle distant-same-ISA (P-4)
- 두 oracle 쌍 모두 axis 분화 (N1 누적 절차 / N4 중요성 결정 / N5 감사의견근거 단락 계량화) 로 surface 회수 분리 의도
- BGE 임베딩 시 동일 ISA cluster 내부 회수 위험 → P5 S4 retrofit audit "cross-oracle adjacent" + "cross-oracle distant-same-ISA" subtype diagnostic 추가 추적
- 본 N4 가 cross-oracle adjacent ¶ proximity **2nd instance** + distant-same-ISA **1st instance** (P-1 reserved; DA 2026-04-19 Clarification 2 반영) — P5 audit 결과로 monitored_pair schema 운용 사유 (P9 plan diff log 별도 항목)

### DR-5(c) — Option D (objective 제외) (2026-04-19 신규 조항)

**Option D**: cross-standard primary 적격 section ∈ {requirements, application, definitions} (objective 제외).

| primary chunk_id | section | Option D PASS |
|---|---|---|
| 705:08655:8 | requirements | ✓ |
| 700:08024:18 | requirements | ✓ |
| 450:04222:11 | requirements | ✓ |

→ 3/3 PASS. N3 Option D pilot precedent 후속 적용 (3/3 PASS 누적 6/6).

### DR 체크리스트

```text
[✓] DR-1 — Intro-parent stub 없음
    근거: 3 primary cc 157/234/143 (모두 substantive). 705:6 + 700:17 deep-stub swap 2건.
[✓] DR-2 — Resolver 매핑 로그 첨부
    근거: concrete chunk_id 직접 (resolver N/A). body cross-ref 강 (700:18 → 705 delegating, refs=["A16"]) — DR-2 paradigm case.
[✓] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: paragraph_ids 모두 numeric ["8"]/["18"]/["11"]
[✓] DR-4 — Query phrasing ↔ primary framing 일치
    근거: 705:8 ∩=14, 700:18 ∩=17 (보강 후), 450:11 ∩=10 — 모두 ≥ 10 robust
        DR-6 precedent (P3 신규 조항 후보) **2nd precedent**: 700:18 query enhancement 정당화 기록 yaml notes §DA 2-test
[✓] DR-5(a) (cross) — primary ISA 수 ≥ 2
    근거: unique ISAs = {705, 700, 450} = 3 (full-cross, 3-stage chain)
[✓] DR-5(b) (cross, NIT-N6) — 다른 cross 와 primary disjoint
    근거: N1∪N2∪N3∪N7∪N8∪N9 union 15 chunks 와 ∅ 교집합
    경계: 450:11 vs N1 450:8 cross-oracle adjacent ¶ (P-3), 705:8 vs N5 705:21 cross-oracle distant-same-ISA (P-4) — 모두 P5 S4 diagnostic 추적
[✓] DR-5(c) (cross, Option D) — primary section ∈ {requirements, application, definitions}
    근거: 3 primary 모두 section=requirements (Option D PASS, N3 pilot precedent 후속 6/6 누적)
```

→ 7 항목 (DR-5 3 sub-rule) 전수 ✓. (c) intentional gap 0건. small-ISA 위험 없음 (705 mid-class, 700 hub-class, 450 mid-class). cross-oracle adjacent ¶ + distant-same-ISA proximity 경계 P5 추적 항목.

### S4 prescreen 측정 보류 (P5 일괄)

N1/N2/N3/N7/N8/N9 와 동일 — P5 audit 시점 v3 24 신규 primary 일괄 측정 + cross-oracle adjacent ¶ + distant-same-ISA proximity diagnostic 컬럼 추가.

### DR-4 robustness margin 비교 (DA P7 분석 조건 입력)

DA N7 spot-check §1 P7 분석 조건 누적 입력:

| oracle | primary chunk_id | ∩ | margin 분류 |
|---|---|---:|---|
| N1 (Q27) | 500:04351:6 | 4 | ≥ 3 |
| N1 (Q27) | 330:03681:7 | 1 | (c) intentional |
| N1 (Q27) | 450:04218:8 | 2 | =2 hit |
| N7 (Q33) | 250:01628:22 | 2 | =2 hit |
| N7 (Q33) | 240:01098:22 | 2 | =2 hit |
| N8 (Q34) | 260:01824:2 | 3 | ≥ 3 |
| N8 (Q34) | 265:02105:9 | 5 | ≥ 3 |
| N9 (Q35) | 550:06012:18 | 6 | ≥ 3 |
| N9 (Q35) | 240:01102:24 | 6 | ≥ 3 |
| N2 (Q28) | 402:04010:9 | 3 | ≥ 3 |
| N2 (Q28) | 315:02482:22 | 3 | ≥ 3 |
| N2 (Q28) | 330:03680:6 | 6 (strict; loose 4 informative only) | ≥ 3 |
| N3 (Q29) | 600:06962:17 | 5 | ≥ 3 |
| N3 (Q29) | 600:06990:26 | 8 | ≥ 3 |
| N3 (Q29) | 315:02485:23 | 4 (DR-6 enhanced; pre-estimate 3) | ≥ 3 |
| N4 (Q30) | 705:08655:8 | 14 | ≥ 3 |
| N4 (Q30) | 700:08024:18 | 17 (DR-6 enhanced; pre-estimate 2) | ≥ 3 |
| N4 (Q30) | 450:04222:11 | 10 | ≥ 3 |

현 누적 (7/9 oracle, 18 primary): ≥ 3 margin = 14 / =2 hit = 3 / (c) = 1.
P7 t-test sample size: ≥3 vs =2 = 14 vs 3 (n_total=17, oracle 단위 평균
recall@5 비교 시 7 vs 3 oracle, 추후 sample-size 검토 필요).

---

## Q31 — N5: 계속기업 ↔ 감사보고서 보고 chain (570↔700↔705)

```yaml
id: Q31
category: cross-standard
query: "감사인은 재무제표에 계속기업 가정의 사용이 적합하나 중요한 불확실성이 존재하는 경우, 적절한 공시가 이루어진 경우 적정의견을 표명하여야 하며 '계속기업 관련 중요한 불확실성' 이라는 제목의 별도 단락을 감사보고서에 포함하여야 하며, 해당되는 경우 감사기준서 570에 따라 보고하여야 하고, 의견이 변형된 경우 감사의견근거 단락에 재무제표의 중요한 왜곡표시의 재무적 영향의 설명과 계량화한 내용을 어떻게 포함하여야 하는가?"
expected_primary_chunks:
  - "570:06480:22"
  - "700:08053:29"
  - "705:08691:21"
expected_related_chunks:
  - "570:06477:21"   # ISA 570 ¶21 부적정의견 (적절한 공시 미수행 시)
  - "700:08044:26"   # ISA 700 ¶26 KAM 별도 단락 (N6 인접)
  - "705:08655:8"    # ISA 705 ¶8 부적정의견 본문 (N4 primary; cross-oracle distant-same-ISA → P-4)
  - "700:08063:(b)"  # ISA 700 ¶29(b) sub-item (Obs-4 sub-item chunk_id convention 후보, P3 정책 분리)
notes: |
  Cross-standard "계속기업 보고 chain" 축. 570 (계속기업 적정의견 + 별도 단락
  보고 framework) → 700 (감사보고서 본문 70029 — 570 delegating clause) →
  705 (변형의견 시 감사의견근거 단락 계량화). **3 ISA full-cross**.

  ## Option N5-β-prime 적용 (1-swap, 2026-04-19)
  plan §4.2 line 86 (N5: `570:22, 705:21, 700:26`) base 의 700:26 가 KAM
  별도 단락 (axis off) → DR-2 cross-ref signal 약. DA β-prime vs β-prime+
  비교 후 β-prime 채택:
    - 570:06480:22 (cc=260, axis 최강 "중요한 불확실성/적정의견/별도 단락") — base 유지
    - 700:08053:29 (cc=121, "감사인은 감사기준서 570에 따라 보고" delegating
      clause) — **swap from 700:26**. heading_trail "감사보고서 > 계속기업"
      세그먼트 명시 → DR-2 cross-ref signal 강 (700 → 570 delegation).
    - 705:08691:21 (cc=254, "감사의견근거 단락 재무적 영향 계량화") — base 유지

  Option β-prime+ (700:08063:(b), cc=252) 기각 근거 (DA 2026-04-19):
  1. DR-2 cross-ref signal 우선 — N5 axis 본질 = 570↔700↔705 보고 chain.
     700:29 본문 "570에 따라 보고하여야 한다" = delegating clause, retrieval
     관점에서 cross-ref signal > cc 크기.
  2. sub-item chunk_id convention risk — `700:08063:(b)` 는 paragraph_id
     "(b)" sub-item. plan §4.2 변칙 표기 "700:32:(b)" 필요. 이 convention
     은 N5 단건 선례로 확립하기 risky → **Obs-4 ticket** 으로 분리, P3 진입
     전 별도 정책 DM 권고.
  3. cc≥130 strict pre-screen 미적용 — 700:29 cc=121 marginal pass DR-1
     (>115). cc≥130 upgrade 는 P9 plan diff log future-applicability flag
     이지 현재 P0 gate 아님. axis-weak 성 (705:21) 은 yaml notes 명시 기록
     으로 transparency 확보.

  ## N5 structural limitation (DA 2026-04-19, Q31 yaml notes)
  ISA 705 본문 "계속기업" 직접 언급 0건 (chunks.jsonl grep 검증 완료).
  705:21 "감사의견근거 단락 재무적 영향 계량화" 는 N5 axis 와 직접 맞물림
  부족 — modification consequence chain 논거로 narrative 수용.
  Retrieval 측면: 705:21 primary hit 은 705 가 KAM/modification 측 cluster
  로 기능할 때 chance hit 가능성 존재 → P5 retrofit S4 "axis-weak primary
  false-positive rate" diagnostic 추적.

  axis_weak_primary:
    chunk_id: "705:08691:21"
    axis_label: "계속기업 보고 chain"
    actual_axis: "재무적 영향 계량화"
    surface_intersection: 16   # query enhancement 후 strict ∩
    semantic_alignment: "weak"
    diagnostic_target: "P5 S4 axis-weak FP rate"
    structural_reason: "ISA 705 본문 '계속기업' 토큰 0건 (chunks.jsonl grep)"

  ## DR-2 cross-ref signal (700:29 → 570 delegating clause)
  700:29 본문 "감사기준서 570에 따라 보고하여야 한다" 는 700 → 570
  delegating clause. heading_trail 끝 세그먼트 "계속기업" 으로 chain
  topology 명시. retrieval 시 700:29 의 cross-ref 신호가 570:22 hit 을
  강화 (chain coherence 보강). β-prime+ (700:32:(b), 2-3 자리 sub-item)
  대비 chain hub edge 정합성 압도적 우위.

  ## DR-4 query enhancement 적용 (DR-6 P3 후보 3rd precedent, 2026-04-19)
  pre-estimate (단순 query): 700:29 ∩ ≈ 3 (감사인은, 감사기준서, 570에) —
  DR-6 trigger zone {2, 3} 진입.
  DA 2-test 판정:
  1. **Axis 확장 test**: "재무제표 계속기업 가정 사용 적합 + 중요한
     불확실성 + 적절한 공시 + 적정의견 별도 단락" 추가는 570:22 본문 axis
     의 명시적 표현 — axis 확장 ✓ (gaming 아님)
  2. **자연 phrasing test**: 감사인 실무 자연 형식 — "계속기업 관련 중요한
     불확실성 별도 단락" 은 570 표제 그대로 사용 ✓
  3. **보강 token 출처 test**: {계속기업, 가정의, 사용이, 적합하나, 중요한,
     불확실성이, 존재하는, 적절한, 공시가, 이루어진, 적정의견을, 표명하여야,
     관련, 이라는, 제목의, 별도, 단락을, 감사보고서에, 포함하여야, 해당되는,
     보고하여야, 의견이, 변형된, 감사의견근거, 재무적, 영향의, 설명과,
     계량화한, 내용을} 모두 570:22 + 700:29 + 705:21 본문/heading top-20
     freq token 실재 ✓
  → 2-test 통과, query enhancement 수락 (DR-6 P3 후보 3rd precedent).

  Pre-estimate 700:29 ∩=3 → 보강 후 ∩=8:
  enhanced_intersection_post_query_expansion:
    "570:06480:22": 22   # base 강
    "700:08053:29": 8    # pre-estimate 3 → 8 (보강)
    "705:08691:21": 16   # base + 보강 (axis-weak surface 강)
  enhanced: true   # P5 retrofit_audit.py 정합성 signal 컬럼

  ## Cross-oracle proximity (4th instance — N4 인접, distant-same-ISA; P-1 reserved)
  monitored_pair:
    pair_id: "P-4"  # N4 evidence block 에 정의, 본 N5 에서 재참조
    oracles: ["N4", "N5"]
    isa: "705"
    paragraph_distance: 13       # ¶8 vs ¶21
    block_ordinal_distance: 36   # 8655 vs 8691
    proximity_subtype: "cross-oracle distant-same-ISA"
    additional_note_n5: "axis-weak (N5 705:21) × axis-strong (N4 705:8)
                          본문 surface 분화 (계량화 vs 부적정의견 표명)
                          이지만 동일 ISA cluster 회수 시 confusion 가능"

  ## DR 7/7 ✓ (DR-5 3 sub-rule)
  DR-1: cc 260/121/254 모두 substantive (700:29 cc=121 marginal pass >115)
  DR-2: 700:29 → 570 cross-ref strong (delegating clause + heading "계속기업")
  DR-3: paragraph_ids ["22"]/["29"]/["21"] all numeric, (i) 0건
  DR-4: ∩ pre-estimate {very strong, 3, 4-6} → 보강 후 22/8/16 (DR-6 3rd precedent)
  DR-5(a): 3 ISA full-cross {570, 700, 705}
  DR-5(b): N1+N2+N3+N4+N7+N8+N9 union 18 chunks 와 ∅ 교집합
  DR-5(c) Option D: 3 primary 모두 section=requirements ✓
```

### Evidence — chunks.jsonl 원문 (3 primary)

```jsonl
# Primary 1 — 570:06480:22 (요구사항, char_count=260) — base 유지
chunk_id="570:06480:22"  isa_no=570  section=requirements  block_ordinal=6480
heading_trail=[
  "감사기준서 570  계속기업",
  "요구사항",
  "감사보고서에 대한 시사점",
  "회계의 계속기업전제의 사용이 적합하나 중요한 불확실성이 존재하는 경우",
  "재무제표에 중요한 불확실성에 대한 적절한 공시가 이루어진 경우"
]
paragraph_ids=["22"]
text="감사기준서 570  계속기업 > 요구사항 > 감사보고서에 대한 시사점 > 회계의
      계속기업전제의 사용이 적합하나 중요한 불확실성이 존재하는 경우 >
      재무제표에 중요한 불확실성에 대한 적절한 공시가 이루어진 경우\n\n
      22. 재무제표에 중요한 불확실성에 대한 적절한 공시가 이루어진 경우,
      감사인은 적정의견을 표명하여야 하며 다음의 목적을 위한 \"계속기업 관련
      중요한 불확실성\" 이라는 제목의 별도 단락을 감사보고서에 포함하여야
      한다. (문단 A28-A31, A34 참조)"
refs=["A28","A29","A30","A31"]
```

```jsonl
# Primary 2 — 700:08053:29 (요구사항, char_count=121) — Option β-prime swap from 700:26
chunk_id="700:08053:29"  isa_no=700  section=requirements  block_ordinal=8053
heading_trail=[
  "감사기준서 700  재무제표에 대한 의견형성과 보고",
  "요구사항",
  "감사보고서",
  "감사기준에 따라 수행된 감사에 대한 감사보고서",
  "계속기업"
]
paragraph_ids=["29"]
text="감사기준서 700  재무제표에 대한 의견형성과 보고 > 요구사항 > 감사보고서
      > 감사기준에 따라 수행된 감사에 대한 감사보고서 > 계속기업\n\n
      29. 해당되는 경우, 감사인은 감사기준서 570에 따라 보고하여야 한다."
refs=[]
```

```jsonl
# Primary 3 — 705:08691:21 (요구사항, char_count=254) — base 유지 (axis-weak structural limitation)
chunk_id="705:08691:21"  isa_no=705  section=requirements  block_ordinal=8691
heading_trail=[
  "감사기준서 705  감사의견의 변형",
  "요구사항",
  "의견이 변형된 경우 감사보고서의 형태와 내용",
  "감사의견근거"
]
paragraph_ids=["21"]
text="감사기준서 705  감사의견의 변형 > 요구사항 > 의견이 변형된 경우
      감사보고서의 형태와 내용 > 감사의견근거\n\n
      21. 재무제표의 특정 금액(양적 공시 포함)과 관련하여 재무제표의 중요한
      왜곡표시가 존재하는 경우, 감사인은 실행불가능하지 않는 한 해당
      왜곡표시의 재무적 영향의 설명과 계량화한 내용을 감사의견근거 단락에
      포함하여야 한다. 재무적 영향을 계량화하는 것이 실행가능하지 않다면,
      그러한 사실을 이 단락에 기술하여야 한다. (문단 A22 참조)"
refs=["A22"]
```

### Pilot 조건 5 — 3중 cross-reference 의무 (여섯 번째 instance)

| 출처 | 후보 | 정합 |
|---|---|---|
| plan §4.2 line 86 | N5 = `570:22, 705:21, 700:26` | base (700:26 axis off, KAM 별도 단락 → swap) |
| chunks.jsonl 실측 | `570:06480:22` ✓ cc=260 + refs=["A28..A31"] / `700:08053:29` ✓ cc=121 + heading "계속기업" + 본문 "570에 따라 보고" / `705:08691:21` ✓ cc=254 + refs=["A22"] | swap 1건 (DA 2026-04-19 Option N5-β-prime; β-prime+ 기각 → Obs-4 sub-item convention 분리) |
| 기 작성 cross primary union | N1 (3) ∪ N2 (3) ∪ N3 (3) ∪ N4 (3) ∪ N7 (2) ∪ N8 (2) ∪ N9 (2) = 18 chunks | N5 (3) ∩ union = ∅ ✓ (단 N5 705:21 ↔ N4 705:8 cross-oracle distant-same-ISA — P-4 재참조) |

→ 3중 교차 통과 (plan §4.2 line 86 swap 1 정정 + axis-weak structural limitation 명시 + cross-oracle proximity P-4 재참조). yaml block 작성 정당화.

### DR-1 — Intro-parent stub 검증 (NIT-N1 임계 ≤ 115)

| primary chunk_id | char_count | section | paragraph_ids | 본문 패턴 | stub? |
|---|---:|---|---|---|---|
| 570:06480:22 | 260 | requirements | ["22"] | "...적절한 공시가 이루어진 경우 적정의견을 표명 ... '계속기업 관련 중요한 불확실성' 별도 단락..." | ✗ |
| 700:08053:29 | 121 | requirements | ["29"] | "해당되는 경우, 감사인은 감사기준서 570에 따라 보고하여야 한다." (marginal pass DR-1, body cross-ref strong) | ✗ |
| 705:08691:21 | 254 | requirements | ["21"] | "...왜곡표시의 재무적 영향의 설명과 계량화한 내용을 감사의견근거 단락에 포함..." | ✗ |

**판정**: 3 primary 모두 cc > 115. 700:29 marginal pass (cc=121, threshold 115 +6). 단 본문이 cross-ref delegating clause + heading "계속기업" 명시 → semantic substantive 정합 (DR-2 axis 정당화). → DR-1 ✓.

**Stub swap 기록 1건**:
- `700:08044:26` 또는 plan §4.2 base "700:26" 의 실제 후보 chunk (KAM 별도 단락 axis off) → DR-2 cross-ref signal 약 → §29 swap (cc=121, "570 에 따라 보고" delegating, heading "계속기업").

**Marginal cc 정당화**: 700:29 cc=121 (현재 DR-1 임계 115 +6). cc≥130 strict pre-screen 은 P9 plan diff log future-applicability flag (DA peer endorsed) — 현재 P0 gate 미적용. body cross-ref signal 강 (DR-2) 으로 cc marginal 보완.

### DR-2 — Resolver 매핑 로그 (logical path 미사용) — body cross-ref 강

3 primary 모두 concrete chunk_id 직접 지정. → DR-2 ✓ (resolver path N/A).

**Body cross-ref 신호 (DR-2 axis 정당화 paradigm case)**:
- `700:08053:29` 본문: "감사인은 감사기준서 570에 따라 보고하여야 한다" → 700 → 570 delegating clause. heading_trail 끝 세그먼트 "계속기업" 으로 chain topology 명시.
- `570:06480:22` refs=["A28","A29","A30","A31"] (application 4건 reference) — N5 axis 의 application support 강.
- `705:08691:21` refs=["A22"] (application 1건) — N5 axis 의 application support.

### DR-3 — Alphabetical (i) vs Roman (i) 모호성 검증

paragraph_ids = `["22"]` / `["29"]` / `["21"]`. numeric, `(i)` 사용 0건. → DR-3 ✓.

### DR-4 — Query phrasing ↔ primary framing 정합 (NIT-N4 정량)

**쿼리 표면형 토큰** (공백 split, stopword 후, unique 약 45개):
```text
["감사인은", "재무제표에", "계속기업", "가정의", "사용이", "적합하나", "중요한",
 "불확실성이", "존재하는", "경우,", "적절한", "공시가", "이루어진", "경우",
 "적정의견을", "표명하여야", "하며", "'계속기업", "관련", "불확실성'", "이라는",
 "제목의", "별도", "단락을", "감사보고서에", "포함하여야", "하며,", "해당되는",
 "감사기준서", "570에", "따라", "보고하여야", "하고,", "의견이", "변형된",
 "감사의견근거", "단락에", "재무제표의", "왜곡표시의", "재무적", "영향의",
 "설명과", "계량화한", "내용을", "어떻게", "하는가?"]
```

(중복: "재무제표에" 2회, "중요한" 3회, "경우" 2회, "포함하여야" 2회. stopword 매칭 0건; "의" 단독은 stopword 이지만 query 토큰에 단독 형태 없음.)

**Primary mini-table** (각 primary top-20 ∩ query, strict surface-form):

| primary chunk_id | primary top-20 (요약) | 교집합 | 일치 (≥2) |
|---|---|---|---|
| 570:06480:22 | 감사기준서, 570, 계속기업, 요구사항, 감사보고서에, 대한, 시사점, 회계의, 계속기업전제의, 사용이, 적합하나, 중요한, 불확실성이, 존재하는, 경우, 재무제표에, 적절한, 공시가, 이루어진, 22., 감사인은, 적정의견을, 표명하여야, 하며, "계속기업, 관련, 불확실성", 이라는, 제목의, 별도, 단락을, 감사보고서에, 포함하여야 | {감사인은, 재무제표에, 계속기업, 사용이, 적합하나, 중요한, 불확실성이, 존재하는, 경우, 적절한, 공시가, 이루어진, 적정의견을, 표명하여야, 하며, 관련, 이라는, 제목의, 별도, 단락을, 감사보고서에, 포함하여야} = 23 | ✓ |
| 700:08053:29 | 감사기준서, 700, 재무제표에, 대한, 의견형성과, 보고, 요구사항, 감사보고서, 감사기준에, 따라, 수행된, 감사에, 계속기업, 29., 해당되는, 경우,, 감사인은, 570에, 보고하여야 | {감사인은, 재무제표에, 계속기업, 따라, 감사기준서, 570에, 보고하여야, 해당되는, 경우,} = 9 (DR-6 enhanced; pre-estimate 3) | ✓ |
| 705:08691:21 | 감사기준서, 705, 감사의견의, 변형, 요구사항, 의견이, 변형된, 경우, 감사보고서의, 형태와, 내용, 감사의견근거, 21., 재무제표의, 특정, 금액(양적, 공시, 포함)과, 관련하여, 중요한, 왜곡표시가, 존재하는, 감사인은, 실행불가능하지, 않는, 한, 해당, 왜곡표시의, 재무적, 영향의, 설명과, 계량화한, 내용을, 단락에, 포함하여야 | {감사인은, 의견이, 변형된, 경우, 감사의견근거, 중요한, 존재하는, 단락에, 재무제표의, 왜곡표시의, 재무적, 영향의, 설명과, 계량화한, 내용을, 포함하여야} = 16 | ✓ |

**Strict 정책 적용**: query_design_rules.md DR-4 § "strict surface form tokenization (공백 split, 형태소 분석 미적용)" 준수. **활용 변이 병합 미적용** (예: "단락을" ≠ "단락에" 단, query 에 "단락을" 과 "단락에" 둘 다 등장 → 본문 매칭 가능).

**판정**: 3 primary 모두 ∩ ≥ 9 (strict 기준). 570:22 ∩=23 (axis 최강), 700:29 ∩=9 (보강 후, pre-est 3), 705:21 ∩=16 (axis-weak 이나 surface 보강 강 — semantic vs surface gap 표면). (c) gap 0건. 단 700:29 는 DR-4 query enhancement 적용 사례 — DR-6 (P3 신규 조항 후보) **3rd precedent**. yaml notes §"DA 2-test" 정당화 기록 참조 (N3/N4 1st-2nd precedent 동일 procedure).

**axis-weak 표면 매칭 caveat**: 705:21 ∩=16 strict surface 강 ↔ axis "계속기업 보고 chain" semantic alignment weak. ISA 705 본문 "계속기업" 토큰 0건 (chunks.jsonl grep 검증). → P5 retrofit S4 axis-weak FP rate diagnostic 추적 (yaml notes §"axis_weak_primary").

### DR-5(a) — Cross-standard primary ISA ≥ 2 (Option D 적용)

| primary chunk_id | isa_no | section |
|---|---|---|
| 570:06480:22 | 570 | requirements |
| 700:08053:29 | 700 | requirements |
| 705:08691:21 | 705 | requirements |

unique ISAs = {570, 700, 705} = **3 개** → DR-5(a) ✓.

**ISA 분포 의도**: 570 (계속기업 보고 framework) → 700 (감사보고서 본문 70029, 570 delegating) → 705 (변형의견 시 감사의견근거 단락 계량화) **3-stage chain** (570 framework → 700 hub → 705 modification consequence). N1/N4 와 동급 full-cross 분포.

### DR-5(b) — Cross 쿼리 간 primary disjoint (NIT-N6)

기 작성 cross oracle primary union (7 oracles):
- N1 (Q27): {500:04351:6, 330:03681:7, 450:04218:8} (3)
- N2 (Q28): {402:04010:9, 315:02482:22, 330:03680:6} (3)
- N3 (Q29): {600:06962:17, 600:06990:26, 315:02485:23} (3)
- N4 (Q30): {705:08655:8, 700:08024:18, 450:04222:11} (3)
- N7 (Q33): {250:01628:22, 240:01098:22} (2)
- N8 (Q34): {260:01824:2, 265:02105:9} (2)
- N9 (Q35): {550:06012:18, 240:01102:24} (2)

union = 18 chunks. 본 N5 primary {570:06480:22, 700:08053:29, 705:08691:21} 와
차집합 = ∅ 교집합 → DR-5(b) ✓.

**Cross-oracle distant-same-ISA proximity 경계 사항** (DA 2026-04-19 DM, 4th instance — P-4 재참조; P-1 reserved):
- `705:08691:21` (N5) ↔ `705:08655:8` (N4) — 동일 ISA 705, ¶ distance 13, block_ordinal distance 36, heading_trail prefix depth=2 후속 segment 분화 ("감사의견에 대한 변형 유형" / "의견이 변형된 경우 감사보고서의 형태와 내용") → cross-oracle distant-same-ISA (P-4)
- 두 oracle axis 분화 (N4 부적정의견 표명 / N5 감사의견근거 단락 계량화) 로 surface 회수 분리 의도 — 단 동일 ISA 705 cluster 회수 시 confusion 가능
- **N5-specific risk**: 705:21 axis-weak (semantic alignment 약, surface 매칭 강) → P5 S4 axis-weak FP rate diagnostic 의 1차 검증 사례
- 본 N5 가 cross-oracle distant-same-ISA proximity **1st instance, 4th instance overall** (P-2 ~ P-4 누적; P-1 reserved)

### DR-5(c) — Option D (objective 제외) (2026-04-19 신규 조항)

**Option D**: cross-standard primary 적격 section ∈ {requirements, application, definitions} (objective 제외).

| primary chunk_id | section | Option D PASS |
|---|---|---|
| 570:06480:22 | requirements | ✓ |
| 700:08053:29 | requirements | ✓ |
| 705:08691:21 | requirements | ✓ |

→ 3/3 PASS. N3 Option D pilot precedent 후속 적용 (3/3 PASS 누적 9/9).

### DR 체크리스트

```text
[✓] DR-1 — Intro-parent stub 없음
    근거: 3 primary cc 260/121/254 (모두 substantive). 700:26 axis-off swap 1건.
        marginal cc 700:29=121 정당화 (DR-2 cross-ref signal 강 + heading "계속기업")
[✓] DR-2 — Resolver 매핑 로그 첨부
    근거: concrete chunk_id 직접 (resolver N/A). body cross-ref 강 (700:29 → 570 delegating, heading "계속기업") — DR-2 paradigm case (β-prime+ 기각 핵심 근거).
[✓] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: paragraph_ids 모두 numeric ["22"]/["29"]/["21"]
[✓] DR-4 — Query phrasing ↔ primary framing 일치
    근거: 570:22 ∩=23 (axis 최강), 700:29 ∩=9 (보강 후), 705:21 ∩=16 (surface 강) — 모두 ≥ 9
        DR-6 precedent **3rd precedent**: 700:29 query enhancement 정당화 yaml notes §DA 2-test
        axis-weak caveat: 705:21 surface 강 / semantic 약 → P5 S4 axis-weak FP rate diagnostic
[✓] DR-5(a) (cross) — primary ISA 수 ≥ 2
    근거: unique ISAs = {570, 700, 705} = 3 (full-cross, 3-stage chain)
[✓] DR-5(b) (cross, NIT-N6) — 다른 cross 와 primary disjoint
    근거: N1∪N2∪N3∪N4∪N7∪N8∪N9 union 18 chunks 와 ∅ 교집합
    경계: 705:21 vs N4 705:8 cross-oracle distant-same-ISA (P-4 재참조) — P5 S4 diagnostic 추적
[✓] DR-5(c) (cross, Option D) — primary section ∈ {requirements, application, definitions}
    근거: 3 primary 모두 section=requirements (Option D PASS, N3 pilot precedent 후속 9/9 누적)
```

→ 7 항목 (DR-5 3 sub-rule) 전수 ✓. (c) intentional gap 0건. small-ISA 위험 없음 (570 mid-class, 700 hub-class, 705 mid-class). cross-oracle distant-same-ISA proximity (P-4) + axis-weak primary (705:21) 경계 P5 추적 항목.

### S4 prescreen 측정 보류 (P5 일괄)

N1/N2/N3/N4/N7/N8/N9 와 동일 — P5 audit 시점 v3 24 신규 primary 일괄 측정 + cross-oracle proximity 4 subtype (within-parent-child / cross-adjacent / cross-distant-same-ISA / axis-weak primary FP) diagnostic 컬럼 추가.

### DR-4 robustness margin 비교 (DA P7 분석 조건 입력)

DA N7 spot-check §1 P7 분석 조건 누적 입력:

| oracle | primary chunk_id | ∩ | margin 분류 |
|---|---|---:|---|
| N1 (Q27) | 500:04351:6 | 4 | ≥ 3 |
| N1 (Q27) | 330:03681:7 | 1 | (c) intentional |
| N1 (Q27) | 450:04218:8 | 2 | =2 hit |
| N7 (Q33) | 250:01628:22 | 2 | =2 hit |
| N7 (Q33) | 240:01098:22 | 2 | =2 hit |
| N8 (Q34) | 260:01824:2 | 3 | ≥ 3 |
| N8 (Q34) | 265:02105:9 | 5 | ≥ 3 |
| N9 (Q35) | 550:06012:18 | 6 | ≥ 3 |
| N9 (Q35) | 240:01102:24 | 6 | ≥ 3 |
| N2 (Q28) | 402:04010:9 | 3 | ≥ 3 |
| N2 (Q28) | 315:02482:22 | 3 | ≥ 3 |
| N2 (Q28) | 330:03680:6 | 6 (strict; loose 4 informative only) | ≥ 3 |
| N3 (Q29) | 600:06962:17 | 5 | ≥ 3 |
| N3 (Q29) | 600:06990:26 | 8 | ≥ 3 |
| N3 (Q29) | 315:02485:23 | 4 (DR-6 enhanced; pre-estimate 3) | ≥ 3 |
| N4 (Q30) | 705:08655:8 | 14 | ≥ 3 |
| N4 (Q30) | 700:08024:18 | 17 (DR-6 enhanced; pre-estimate 2) | ≥ 3 |
| N4 (Q30) | 450:04222:11 | 10 | ≥ 3 |
| N5 (Q31) | 570:06480:22 | 23 | ≥ 3 |
| N5 (Q31) | 700:08053:29 | 9 (DR-6 enhanced; pre-estimate 3) | ≥ 3 |
| N5 (Q31) | 705:08691:21 | 16 (axis-weak surface 강) | ≥ 3 |

현 누적 (8/9 oracle, 21 primary): ≥ 3 margin = 17 / =2 hit = 3 / (c) = 1.
P7 t-test sample size: ≥3 vs =2 = 17 vs 3 (n_total=20, oracle 단위 평균
recall@5 비교 시 8 vs 3 oracle, 추후 sample-size 검토 필요).

**axis-weak primary subset**: 705:21 (N5) — surface 강 (∩=16) / semantic 약. P5 S4 axis-weak FP rate 1차 검증 사례.

---

## Q32 — N6: 유의적 위험 → KAM 결정 → KAM 별도 단락 chain (701↔315)

```yaml
id: Q32
category: cross-standard
query: "감사인은 평가된 중요왜곡표시위험 중에서 유의적 위험이 있는지 결정하여야 하며, 그러한 사항 중 당기 재무제표감사에서 가장 유의적인 사항들 즉 핵심감사사항인지를 결정하여야 하고, 감사보고서의 '핵심감사사항' 이라는 제목의 별도 단락에 적절한 소제목을 사용하여 각각의 핵심감사사항을 어떻게 기술하여야 하는가?"
expected_primary_chunks:
  - "701:08444:9"
  - "701:08446:10"
  - "315:02498:27"
expected_related_chunks:
  - "701:08443:8"    # ISA 701 ¶8 핵심감사사항 결정 base (¶9 의 "문단9에 따라" 가 가리키는 본문 추정 — Obs-3)
  - "315:02482:22"   # ISA 315 ¶22 통제 미비점 (N2 primary; cross-oracle 동일 ISA 315)
  - "315:02485:23"   # ISA 315 ¶23 RMM 식별 framework (N3 primary; cross-oracle 동일 ISA 315)
  - "260:01824:2"    # ISA 260 ¶2 KAM 커뮤니케이션 (N8 primary; KAM 인접 axis)
notes: |
  Cross-standard "유의적 위험 → KAM 결정 → KAM 별도 단락" lifecycle chain 축.
  315 (유의적 위험 식별) → 701 (KAM 결정 §9, KAM 별도 단락 §10) 의 cross-
  standard chain. **2 ISA cross** ({701, 315}, small-cross 형태, N3 와 동급).

  ## Distribution rationale (DA 2026-04-19, mini-table 신규 column)
  701×2 + 315×1 의도적 설계 — 분포 편향 정당화:

  distribution_rationale: |
    701×2 + 315×1 의도적 설계.
    701:9 (KAM 결정 criteria) + 701:10 (KAM 별도 단락 reporting) =
    KAM lifecycle 2-stage (decision → reporting) narrative.
    315:27 (유의적 위험 식별) = KAM 결정 근원 (precedent risk).
    → 3 primary 가 "유의적 위험 → KAM 결정 → KAM 별도 단락" 단일 chain.
    DR-5(a) Option D "2 distinct ISA ≥ 2" 충족 (701, 315).
    701 within-ISA lifecycle 2-stage 정당화 — 단일 ISA 내 procedural
    chain 표현 의도, 분포 편향 (1 ISA 가 2 primary) acceptable.
    cf. N3 = 600×2+315×1 (그룹감사 within-ISA 2-step + 외부 framework 1)
        과 동일 패턴.

  ## DR-4 query enhancement 미적용 (DR-6 trigger zone 미진입)
  pre-estimate 결과: 701:9 ∩≈9, 701:10 ∩≈11, 315:27 ∩≈8 — 모두 robust.
  DR-6 trigger zone {2, 3} 미진입 → 자연 phrasing 유지, enhancement
  미적용. Q32 query 는 DA 조건부 허용 ("∩ ≈ 3-4 임계 hit 시 axis 확장
  적용") 의 trigger 조건 미충족 → 자연 phrasing 채택.

  ## Cross-oracle primary-vs-related overlap (DA 2026-04-19 Clarification 1)
  315:02498:27 은 N3 (Q29) 의 expected_related_chunks 로도 등록됨 — 동일
  chunk 가 한 oracle 의 관련 참조 (N3 related) + 다른 oracle 의 정답
  (N6 primary) 이중 역할. DR-5(b) 는 primary 간 disjoint 만 요구하므로
  **형식 위반 없음**. P5 retrofit_audit.py §6 monitored_pair schema 에
  "primary_vs_related_overlap" 필드 추가 권고 (DA design 업데이트 예정):

  primary_vs_related_overlap:
    - source_oracle: "N3"
      source_role: "related"
      target_oracle: "N6"
      target_role: "primary"
      chunk_id: "315:02498:27"
      diagnostic_target: "P5 S4 cross-oracle primary-vs-related overlap"

  ## Obs-3 ticket reference (701:9 inline cross-ref "문단9" 파싱 누락)
  701:08444:9 본문 "감사인은 **문단9**에 따라 결정된 사항 중 어떤 사항들이
  ... 핵심감사사항인지를 결정" → 본문 inline cross-ref "문단9" 가 refs 필드
  에 미추출 (refs=["A9"] 만; "문단9" 누락).

  3 가능성 cross-ref 후보 (P5 retrofit 단계 교차 검증):
  - (α) ISA 701 §9 자기참조 (순환 risk)
  - (β) ISA 260 §9 delegation (KAM 결정 맥락 부합)
  - (γ) 기타 ISA

  현재 parser 구조적 한계 (inline "문단N" 패턴 미파싱) → Obs-3 ticket
  P6 candidate. P0 P9 종결 후 별도 maintenance ticket. **P0 non-blocking**.

  obs3_reference:
    ticket_id: "Obs-3"
    discovered_at: "2026-04-19"
    discovered_in: "N6 (Q32) primary 701:08444:9 본문 검증"
    type: "parser structural limitation"
    pattern: "본문 inline '문단N' cross-ref → refs 필드 미추출"
    impact: "DR-2 cross-ref 신호 누락 → retrieval recall 저해 가능"
    p0_blocking: false
    target_phase: "P6"

  ## Cross-oracle proximity (5th instance — N2/N3 동일 ISA 315)
  N6 primary 315:27 은 N2 primary 315:22 + N3 primary 315:23 와 동일 ISA
  315 — within-ISA cross-oracle proximity 다중 instance.

  monitored_pair_a:
    pair_id: "P-5"
    oracles: ["N2", "N6"]
    isa: "315"
    paragraph_distance: 5        # ¶22 vs ¶27
    block_ordinal_distance: 16   # 2482 vs 2498
    section_A: "requirements"
    section_B: "requirements"
    heading_prefix_depth: 2      # ISA 315 > 요구사항 (depth 3+ 분화)
    proximity_subtype: "cross-oracle adjacent"
    notes: "N2 통제 미비점 식별 (¶22) ↔ N6 유의적 위험 결정 (¶27) — axis
            분화 (통제평가 / 위험식별)"

  monitored_pair_b:
    pair_id: "P-6"
    oracles: ["N3", "N6"]
    isa: "315"
    paragraph_distance: 4        # ¶23 vs ¶27
    block_ordinal_distance: 13   # 2485 vs 2498
    section_A: "requirements"
    section_B: "requirements"
    heading_prefix_depth: 2      # ISA 315 > 요구사항 (depth 3+ 분화)
    proximity_subtype: "cross-oracle adjacent"
    notes: "N3 RMM 식별 framework (¶23) ↔ N6 유의적 위험 결정 (¶27) —
            axis 분화 (RMM 식별 수준 / 유의적 위험 결정). RMM 식별의
            후속 단계로 narrative 정합 — chain 상 직전 단계."

  → ISA 315 가 N2/N3/N6 3개 oracle 의 primary 로 등장 — N2-N3 (P-2),
    N2-N6 (P-5), N3-N6 (P-6) 3개 pair 형성. P5 S4 retrofit audit "ISA-315
    cluster within-ISA cross-oracle FP rate" sub-diagnostic 추적 권고.

  ## DR 7/7 ✓ (DR-5 3 sub-rule)
  DR-1: cc 157/196/192 모두 substantive
  DR-2: 701:9 refs=["A9"] (단 본문 "문단9" inline 누락 — Obs-3),
        701:10 refs=["14","15"] (본문 cross-ref to ISA 701 §14, §15),
        315:27 refs=["A218"~"A221"]
  DR-3: paragraph_ids ["9"]/["10"]/["27"] all numeric, (i) 0건
  DR-4: ∩ pre-estimate {9, 11, 8} 모두 ≥3 robust (DR-6 미적용)
  DR-5(a): 2 ISA cross {701, 315} (small-cross, N3 와 동급)
  DR-5(b): N1+N2+N3+N4+N5+N7+N8+N9 union 21 chunks 와 ∅ 교집합
  DR-5(c) Option D: 3 primary 모두 section=requirements ✓
```

### Evidence — chunks.jsonl 원문 (3 primary)

```jsonl
# Primary 1 — 701:08444:9 (요구사항, char_count=157)
chunk_id="701:08444:9"  isa_no=701  section=requirements  block_ordinal=8444
heading_trail=[
  "감사기준서 701  감사보고서 핵심감사사항 커뮤니케이션",
  "요구사항",
  "핵심감사사항의 결정"
]
paragraph_ids=["9"]
text="감사기준서 701  감사보고서 핵심감사사항 커뮤니케이션 > 요구사항 >
      핵심감사사항의 결정\n\n
      9. 감사인은 문단9에 따라 결정된 사항 중 어떤 사항들이 당기 재무제표감사
      에서 가장 유의적인 사항들, 즉 핵심감사사항인지를 결정하여야 한다.
      (문단 A9, A11, A27, A30 참조)"
refs=["A9"]
# Note: 본문 inline "문단9" cross-ref 누락 → Obs-3 ticket (P6 candidate)
```

```jsonl
# Primary 2 — 701:08446:10 (요구사항, char_count=196)
chunk_id="701:08446:10"  isa_no=701  section=requirements  block_ordinal=8446
heading_trail=[
  "감사기준서 701  감사보고서 핵심감사사항 커뮤니케이션",
  "요구사항",
  "핵심감사사항에 대한 커뮤니케이션"
]
paragraph_ids=["10"]
text="감사기준서 701  감사보고서 핵심감사사항 커뮤니케이션 > 요구사항 >
      핵심감사사항에 대한 커뮤니케이션\n\n
      10. 감사인은 문단 14 또는 문단 15의 상황이 아니라면 감사보고서의
      \"핵심감사사항\"이라는 제목의 별도 단락에 적절한 소제목을 사용하여
      각각의 핵심감사사항을 기술하여야 한다. 감사보고서의 이 단락에서 도입
      문구는 다음 사항을 기술하여야 한다."
refs=["14", "15"]
```

```jsonl
# Primary 3 — 315:02498:27 (요구사항, char_count=192)
chunk_id="315:02498:27"  isa_no=315  section=requirements  block_ordinal=2498
heading_trail=[
  "감사기준서 315  중요왜곡표시위험의 식별과 평가",
  "요구사항",
  "중요왜곡표시위험의 식별과 평가 (문단 A184-A185 참조)",
  "경영진주장 수준의 중요왜곡표시위험의 평가",
  "고유위험의 평가 (문단 A205-A217 참조)"
]
paragraph_ids=["27"]
text="감사기준서 315  중요왜곡표시위험의 식별과 평가 > 요구사항 >
      중요왜곡표시위험의 식별과 평가 > 경영진주장 수준의 중요왜곡표시위험의
      평가 > 고유위험의 평가\n\n
      27. 감사인은 평가된 중요왜곡표시위험 중에서 유의적 위험이 있는지
      결정하여야 한다. (문단 A218-A221 참조)"
refs=["A218","A219","A220","A221"]
```

### Pilot 조건 5 — 3중 cross-reference 의무 (일곱 번째 instance, 최종)

| 출처 | 후보 | 정합 |
|---|---|---|
| plan §4.2 line 87 | N6 = `701:9, 701:10, 315:27` | base 그대로 채택 (swap 0건) |
| chunks.jsonl 실측 | `701:08444:9` ✓ cc=157 + refs=["A9"] / `701:08446:10` ✓ cc=196 + refs=["14","15"] / `315:02498:27` ✓ cc=192 + refs=["A218..A221"] | swap 0건 (DA spot-check 3/3 PASS) |
| 기 작성 cross primary union | N1 (3) ∪ N2 (3) ∪ N3 (3) ∪ N4 (3) ∪ N5 (3) ∪ N7 (2) ∪ N8 (2) ∪ N9 (2) = 21 chunks | N6 (3) ∩ union = ∅ ✓ (단 N6 315:27 ↔ N2 315:22 cross-oracle adjacent ¶ — P-5, N6 315:27 ↔ N3 315:23 cross-oracle adjacent ¶ — P-6) |

→ 3중 교차 통과 (plan §4.2 line 87 base 그대로 + cross-oracle proximity P-5/P-6 (ISA 315 cluster) 명시 + 701:9 Obs-3 메모 포함). yaml block 작성 정당화.

### DR-1 — Intro-parent stub 검증 (NIT-N1 임계 ≤ 115)

| primary chunk_id | char_count | section | paragraph_ids | 본문 패턴 | stub? |
|---|---:|---|---|---|---|
| 701:08444:9 | 157 | requirements | ["9"] | "...문단9에 따라 결정된 사항 중 ... 가장 유의적인 사항들 즉 핵심감사사항인지를 결정..." | ✗ |
| 701:08446:10 | 196 | requirements | ["10"] | "...감사보고서의 '핵심감사사항' 이라는 제목의 별도 단락에 ... 각각의 핵심감사사항 기술..." | ✗ |
| 315:02498:27 | 192 | requirements | ["27"] | "...평가된 중요왜곡표시위험 중에서 유의적 위험이 있는지 결정..." | ✗ |

**판정**: 3 primary 모두 cc > 115, 본문 substantive (KAM 결정 criteria, KAM 별도 단락 reporting, 유의적 위험 결정). → DR-1 ✓.

**Stub swap 기록**: 0건 (plan §4.2 base 그대로 채택).

### DR-2 — Resolver 매핑 로그 (logical path 미사용) — body cross-ref 中

3 primary 모두 concrete chunk_id 직접 지정. → DR-2 ✓ (resolver path N/A).

**Body cross-ref 신호**:
- `701:08444:9` 본문: "**문단9**에 따라 결정된 사항" → inline cross-ref ("문단9") 누락 — **Obs-3 ticket** 등록 (parser 한계, P6 candidate). refs=["A9"] 는 추출 정상.
- `701:08446:10` 본문: "**문단 14** 또는 **문단 15**의 상황이 아니라면" → inline cross-ref refs=["14","15"] 정상 추출 (자기 ISA 본문 paragraph 참조).
- `315:02498:27` refs=["A218","A219","A220","A221"] (application 4건) — DR-2 application support 강.

### DR-3 — Alphabetical (i) vs Roman (i) 모호성 검증

paragraph_ids = `["9"]` / `["10"]` / `["27"]`. numeric, `(i)` 사용 0건. → DR-3 ✓.

### DR-4 — Query phrasing ↔ primary framing 정합 (NIT-N4 정량)

**쿼리 표면형 토큰** (공백 split, stopword 후, unique 약 32개):
```text
["감사인은", "평가된", "중요왜곡표시위험", "중에서", "유의적", "위험이",
 "있는지", "결정하여야", "하며,", "그러한", "사항", "중", "당기",
 "재무제표감사에서", "가장", "유의적인", "사항들", "즉", "핵심감사사항인지를",
 "하고,", "감사보고서의", "'핵심감사사항'", "이라는", "제목의", "별도",
 "단락에", "적절한", "소제목을", "사용하여", "각각의", "핵심감사사항을",
 "어떻게", "기술하여야", "하는가?"]
```

(중복 0건. stopword 매칭 0건; 단 "있는지" 는 "있다" stopword 활용형 — strict 정책상 활용 변이 비병합 → 보존.)

**Primary mini-table** (각 primary top-20 ∩ query, strict surface-form):

| primary chunk_id | primary top-20 (요약) | 교집합 | 일치 (≥2) |
|---|---|---|---|
| 701:08444:9 | 감사기준서, 701, 감사보고서, 핵심감사사항, 커뮤니케이션, 요구사항, 핵심감사사항의, 결정, 9., 감사인은, 문단9에, 따라, 결정된, 사항, 중, 어떤, 사항들이, 당기, 재무제표감사에서, 가장, 유의적인, 사항들,, 즉, 핵심감사사항인지를, 결정하여야 | {감사인은, 사항, 중, 당기, 재무제표감사에서, 가장, 유의적인, 핵심감사사항인지를, 결정하여야} = 9 | ✓ |
| 701:08446:10 | 감사기준서, 701, 감사보고서, 핵심감사사항, 커뮤니케이션, 요구사항, 핵심감사사항에, 대한, 10., 감사인은, 문단, 14, 또는, 15의, 상황이, 아니라면, 감사보고서의, 제목의, 별도, 단락에, 적절한, 소제목을, 사용하여, 각각의, 핵심감사사항을, 기술하여야, 도입, 문구는, 다음, 사항을 | {감사인은, 감사보고서의, 제목의, 별도, 단락에, 적절한, 소제목을, 사용하여, 각각의, 핵심감사사항을, 기술하여야} = 11 | ✓ |
| 315:02498:27 | 감사기준서, 315, 중요왜곡표시위험의, 식별과, 평가, 요구사항, 경영진주장, 수준의, 고유위험의, 27., 감사인은, 평가된, 중요왜곡표시위험, 중에서, 유의적, 위험이, 있는지, 결정하여야, 문단, A218-A221, 참조 | {감사인은, 평가된, 중요왜곡표시위험, 중에서, 유의적, 위험이, 있는지, 결정하여야} = 8 | ✓ |

**Strict 정책 적용**: query_design_rules.md DR-4 § "strict surface form tokenization (공백 split, 형태소 분석 미적용)" 준수. **활용 변이 병합 미적용**.

**판정**: 3 primary 모두 ∩ ≥ 8 (강한 매칭, strict 기준). 701:9 ∩=9, 701:10 ∩=11, 315:27 ∩=8. (c) gap 0건. **DR-6 trigger zone {2, 3} 미진입 → query enhancement 미적용**. 자연 phrasing 유지.

### DR-5(a) — Cross-standard primary ISA ≥ 2 (Option D 적용)

| primary chunk_id | isa_no | section | distribution_rationale |
|---|---|---|---|
| 701:08444:9 | 701 | requirements | KAM 결정 criteria (lifecycle stage 2: decision) |
| 701:08446:10 | 701 | requirements | KAM 별도 단락 reporting (lifecycle stage 3: reporting) |
| 315:02498:27 | 315 | requirements | 유의적 위험 식별 (lifecycle stage 1: precedent risk) |

unique ISAs = {701, 315} = **2 개** → DR-5(a) ✓.

**ISA 분포 의도** (distribution_rationale, DA 권고 신규 column):
N6 = 701×2 + 315×1 의도적 설계 — KAM lifecycle 3-stage chain 표현.
- stage 1 (precedent risk): 315:27 유의적 위험 식별 — RMM 평가 결과 → KAM 결정 근원.
- stage 2 (decision): 701:9 KAM 결정 criteria — 유의적 사항 중 가장 유의적 사항 선별.
- stage 3 (reporting): 701:10 KAM 별도 단락 reporting — 감사보고서 별도 단락 기술.

701 within-ISA 2-stage 정당화: 단일 ISA 내 procedural chain (decision → reporting) 표현 의도, 분포 편향 (1 ISA 가 2 primary) acceptable. **N3 와 동일 패턴** (N3 = 600×2+315×1, 그룹감사 within-ISA 2-step + 외부 framework 1).

### DR-5(b) — Cross 쿼리 간 primary disjoint (NIT-N6)

기 작성 cross oracle primary union (8 oracles, 최종):
- N1 (Q27): {500:04351:6, 330:03681:7, 450:04218:8} (3)
- N2 (Q28): {402:04010:9, 315:02482:22, 330:03680:6} (3)
- N3 (Q29): {600:06962:17, 600:06990:26, 315:02485:23} (3)
- N4 (Q30): {705:08655:8, 700:08024:18, 450:04222:11} (3)
- N5 (Q31): {570:06480:22, 700:08053:29, 705:08691:21} (3)
- N7 (Q33): {250:01628:22, 240:01098:22} (2)
- N8 (Q34): {260:01824:2, 265:02105:9} (2)
- N9 (Q35): {550:06012:18, 240:01102:24} (2)

union = 21 chunks. 본 N6 primary {701:08444:9, 701:08446:10, 315:02498:27} 와
차집합 = ∅ 교집합 → DR-5(b) ✓.

**Cross-oracle adjacent ¶ proximity 경계 사항** (DA 2026-04-19 DM, 5th instance — ISA 315 cluster):
- `315:02498:27` (N6) ↔ `315:02482:22` (N2) — 동일 ISA 315, ¶ distance 5, block_ordinal distance 16, heading_trail prefix depth=2 → cross-oracle adjacent (P-5)
- `315:02498:27` (N6) ↔ `315:02485:23` (N3) — 동일 ISA 315, ¶ distance 4, block_ordinal distance 13, heading_trail prefix depth=2 → cross-oracle adjacent (P-6)
- 3 oracle (N2, N3, N6) 의 ISA 315 primary 가 **ISA 315 within-ISA cluster** 형성. axis 분화 (N2 통제 미비점 / N3 RMM 식별 framework / N6 유의적 위험 결정) 로 surface 회수 분리 의도 — 단 BGE 임베딩 시 ISA 315 cluster 내부 회수 위험 ↑
- → P5 S4 retrofit audit "ISA-315 cluster within-ISA cross-oracle FP rate" sub-diagnostic 추적 권고
- 본 N6 가 within-ISA cross-oracle proximity **2-instance burst** (P-5 + P-6, 누적 5th-6th instance overall; P-1 reserved)

### DR-5(c) — Option D (objective 제외) (2026-04-19 신규 조항)

**Option D**: cross-standard primary 적격 section ∈ {requirements, application, definitions} (objective 제외).

| primary chunk_id | section | Option D PASS |
|---|---|---|
| 701:08444:9 | requirements | ✓ |
| 701:08446:10 | requirements | ✓ |
| 315:02498:27 | requirements | ✓ |

→ 3/3 PASS. N3 Option D pilot precedent 후속 적용 (3/3 PASS 누적 12/12 — N3 + N4 + N5 + N6 모두 100% PASS).

### DR 체크리스트

```text
[✓] DR-1 — Intro-parent stub 없음
    근거: 3 primary cc 157/196/192 (모두 substantive). swap 0건 (plan §4.2 base 그대로).
[✓] DR-2 — Resolver 매핑 로그 첨부
    근거: concrete chunk_id 직접 (resolver N/A). body cross-ref 中 (701:10 refs=["14","15"] / 315:27 refs=["A218..A221"]).
        Obs-3 메모: 701:9 본문 inline "문단9" 미파싱 (P6 candidate, P0 non-blocking)
[✓] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: paragraph_ids 모두 numeric ["9"]/["10"]/["27"]
[✓] DR-4 — Query phrasing ↔ primary framing 일치
    근거: 701:9 ∩=9, 701:10 ∩=11, 315:27 ∩=8 — 모두 ≥ 8 robust
        DR-6 trigger zone {2, 3} 미진입 → query enhancement 미적용 (자연 phrasing 유지)
[✓] DR-5(a) (cross) — primary ISA 수 ≥ 2
    근거: unique ISAs = {701, 315} = 2 (small-cross, N3 와 동급)
        distribution_rationale: 701×2+315×1 = KAM lifecycle 3-stage chain (precedent risk → decision → reporting)
[✓] DR-5(b) (cross, NIT-N6) — 다른 cross 와 primary disjoint
    근거: N1∪N2∪N3∪N4∪N5∪N7∪N8∪N9 union 21 chunks 와 ∅ 교집합
    경계: 315:27 vs N2 315:22 (P-5) + 315:27 vs N3 315:23 (P-6) — ISA 315 cluster within-ISA cross-oracle, P5 S4 sub-diagnostic 추적
[✓] DR-5(c) (cross, Option D) — primary section ∈ {requirements, application, definitions}
    근거: 3 primary 모두 section=requirements (Option D PASS, 누적 12/12 N3+N4+N5+N6 100%)
```

→ 7 항목 (DR-5 3 sub-rule) 전수 ✓. (c) intentional gap 0건. small-ISA 위험 없음 (701 mid-class, 315 mega-class). within-ISA cross-oracle proximity (ISA 315 cluster: N2/N3/N6 3-oracle burst) 경계 P5 추적 + Obs-3 ticket 본문 inline cross-ref 누락 메모.

### S4 prescreen 측정 보류 (P5 일괄)

N1/N2/N3/N4/N5/N7/N8/N9 와 동일 — P5 audit 시점 v3 24 신규 primary 일괄 측정 + cross-oracle proximity 4 subtype + ISA 315 cluster sub-diagnostic + axis-weak primary FP diagnostic 컬럼 추가.

### DR-4 robustness margin 비교 (DA P7 분석 조건 입력) — 최종 누적

DA N7 spot-check §1 P7 분석 조건 누적 입력 (9 oracle 최종):

| oracle | primary chunk_id | ∩ | margin 분류 |
|---|---|---:|---|
| N1 (Q27) | 500:04351:6 | 4 | ≥ 3 |
| N1 (Q27) | 330:03681:7 | 1 | (c) intentional |
| N1 (Q27) | 450:04218:8 | 2 | =2 hit |
| N7 (Q33) | 250:01628:22 | 2 | =2 hit |
| N7 (Q33) | 240:01098:22 | 2 | =2 hit |
| N8 (Q34) | 260:01824:2 | 3 | ≥ 3 |
| N8 (Q34) | 265:02105:9 | 5 | ≥ 3 |
| N9 (Q35) | 550:06012:18 | 6 | ≥ 3 |
| N9 (Q35) | 240:01102:24 | 6 | ≥ 3 |
| N2 (Q28) | 402:04010:9 | 3 | ≥ 3 |
| N2 (Q28) | 315:02482:22 | 3 | ≥ 3 |
| N2 (Q28) | 330:03680:6 | 6 (strict; loose 4 informative only) | ≥ 3 |
| N3 (Q29) | 600:06962:17 | 5 | ≥ 3 |
| N3 (Q29) | 600:06990:26 | 8 | ≥ 3 |
| N3 (Q29) | 315:02485:23 | 4 (DR-6 enhanced; pre-est 3) | ≥ 3 |
| N4 (Q30) | 705:08655:8 | 14 | ≥ 3 |
| N4 (Q30) | 700:08024:18 | 17 (DR-6 enhanced; pre-est 2) | ≥ 3 |
| N4 (Q30) | 450:04222:11 | 10 | ≥ 3 |
| N5 (Q31) | 570:06480:22 | 23 | ≥ 3 |
| N5 (Q31) | 700:08053:29 | 9 (DR-6 enhanced; pre-est 3) | ≥ 3 |
| N5 (Q31) | 705:08691:21 | 16 (axis-weak surface 강) | ≥ 3 |
| N6 (Q32) | 701:08444:9 | 9 | ≥ 3 |
| N6 (Q32) | 701:08446:10 | 11 | ≥ 3 |
| N6 (Q32) | 315:02498:27 | 8 | ≥ 3 |

**최종 누적 (9/9 oracle, 24 primary)**: ≥ 3 margin = 20 / =2 hit = 3 / (c) = 1.
P7 t-test sample size: ≥3 vs =2 = 20 vs 3 (n_total=23, oracle 단위 평균
recall@5 비교 시 9 vs 3 oracle, 추후 sample-size 검토 필요).

**DR-6 적용 누적**: 3 cases (N3 315:23 / N4 700:18 / N5 700:29) — DA 2-test 통과, P3 신규 조항 후보.
**axis-weak primary 누적**: 1 case (N5 705:21) — surface 강 / semantic 약, P5 S4 axis-weak FP rate diagnostic 추적.
**Obs ticket 누적**: Obs-1 (260:1824:2 paragraph_id), Obs-2 (250:1628:22 cross-ref spacing), Obs-3 (701:9 inline 문단N), Obs-4 (sub-item chunk_id convention) — 모두 P0 non-blocking, post-close maintenance.

---

## Phase 4 P0 oracle 진척 — task#2 close ready

**oracle 9/9 complete** (N1/N2/N3/N4/N5/N6/N7/N8/N9 모두 evidence block 작성 완료).

| oracle | query | primary count | DR 7/7 | DR-6 enhanced | axis-weak | swap 건수 | proximity pair |
|---|---|---:|---|---|---|---:|---|
| N1 (Q27) | full-cross | 3 | ✓ | - | - | 0 | - |
| N2 (Q28) | full-cross | 3 | ✓ | - | - | 0 | - |
| N3 (Q29) | small-cross | 3 | ✓ | 315:23 (1) | - | 1 (315:11→23) | P-2 (cross-adj) |
| N4 (Q30) | full-cross | 3 | ✓ | 700:18 (2) | - | 2 (705:6→8, 700:17→18) | P-3, P-4 |
| N5 (Q31) | full-cross | 3 | ✓ | 700:29 (3) | 705:21 (1) | 1 (700:26→29) | P-4 재참조 |
| N6 (Q32) | small-cross | 3 | ✓ | - | - | 0 | P-5, P-6 |
| N7 (Q33) | small-cross | 2 | ✓ | - | - | 0 | - |
| N8 (Q34) | small-cross | 2 | ✓ | - | - | 0 | - |
| N9 (Q35) | small-cross | 2 | ✓ | - | - | 0 | - |

**총합**: primary 24 / DR-6 enhanced 3 / axis-weak 1 / swap 4건 / proximity pair 6건.

**Commit 2 trigger ready** — task#2 close 후 oracle_log.md 일괄 commit (DA 2026-04-19 commit schedule).

DA 통합 spot-check 대기 → 통과 시 task#2 close → Commit 2 → P3 진입 ([P3] requirements +5 / application +5 / definitions +5 oracle, DR-6 정식 도입).

---

## P0 post-close follow-up — chunker observations

P0 PR freeze (plan §11.4 condition 3) 외 사항. `src/audit_parser/chunk.py` /
`structure.py` / `numbering.py` 수정 시 P0 일시 중단 후 chunks.jsonl 재생성
필수. 본 섹션은 P0 종결 (P9) 후 별도 maintenance ticket 으로 이전.

### Obs-1 — `260:01824:2` paragraph_id 파싱 의심 (N8 검증 중 발견)

- **fact**: chunks.jsonl line 722 (block_ordinal 1824) `paragraph_ids=["2"]`
  로 파싱됨. 그러나 block_ordinal 1822 = ¶15, block_ordinal 1825 = `(a)`
  sub-item (¶16 의 첫 번째 sub) 위치상 실제 본문 paragraph 는 **¶16** 으로
  추정.
- **plan match**: `phase4_p0_plan.md:89` "N8: ... 260:16, 265:9" 와 정합 시
  본 chunk 가 plan 의 `260:16` 임이 확실 (positional + semantic). parser 가
  "16" 의 일의자리 "6" 을 누락하고 "1" 도 누락한 결과로 보이며, 다른 가능성은
  본문 시작이 "2." 로 잘못 표기된 원본 docx 인용 (확인 미완).
- **impact (P0 scope 내)**:
  - oracle_log.md 본 oracle 의 chunk_id 는 `260:01824:2` 그대로 채택
    (chunks.jsonl 불변성 R7 준수).
  - resolver 호출 (P4 smoke) 시 `260:01824:2` 직접 지정 → 정상 resolve 예상.
  - 단 retrieval 시 모델이 본 chunk 텍스트의 헤더 `2.` 토큰을 학습 → 의미적
    관련도 영향 미미 (heading_trail 에 ¶ 번호 없음).
- **post-close action**: chunker numbering.py 의 multi-digit 파싱 로직
  점검 ("16" 같은 2자리 + 직후 sub-item 시작 시 truncation 케이스) — P0 P9
  종결 후 별도 ticket.

### Obs-2 — `250:01628:22` cross-ref 토큰 spacing 깨짐 (N7 검증 중 발견)

- **fact**: chunks.jsonl line 644 (block_ordinal 1628) 본문 끝 부분
  `"(문단 A23- A 25 참조)"` 로 파싱됨. 원본 docx 는 통상 `(문단 A23-A25 참조)`
  형식이며, 같은 chunk 의 `refs=["A23"]` 만 추출되고 `A24`, `A25` 누락.
  하이픈 직후 + "A" 이후 공백 삽입으로 토큰 경계가 깨진 결과로 추정.
- **plan match**: cross-ref 정규화 (Phase 2c PR2 — `refs` 필드) 의 in-line
  range 처리 (`A23-A25` → `["A23","A24","A25"]` 확장) 가 spacing-tolerant
  하지 않은 것으로 보임. 비교 사례: 240:01098:22 `(문단 ... 참조)` 누락 없음
  (해당 chunk 는 refs 자체 부재 → 본 사례와 직접 비교 불가).
- **impact (P0 scope 내)**:
  - oracle_log.md N7 primary `250:01628:22` 채택 유지 (chunks.jsonl R7 불변).
  - resolver 호출 (P4 smoke) 시 `250:01628:22` 직접 지정 → 정상 resolve.
  - retrieval 영향 미미: 본문 의미 토큰 ("법규위반", "시사점", "감사인") 은
    spacing 문제와 무관하게 보존됨. cross-ref 기반 검색 (예: "ISA 250 A24")
    수행 시에만 누락 영향 (P5 retrofit S2/S3 신호 가능성).
- **post-close action**: cross-ref 정규화 모듈 (Phase 2c PR2 산출물,
  `src/audit_parser/structure.py` 또는 별도 ref-resolver) 의
  range-expansion regex 점검 — `A\d+\s*-\s*A?\s*\d+` 패턴 허용 여부.
  P0 P9 종결 후 별도 ticket.

---

## P3 — Requirements +5 / Application +5 / Definitions +5 oracle (Q36~Q50)

**Status**: in_progress (DE owner, 2026-04-19, task#3)
**Predecessor**: Commit 2.5 완료 (design skeleton freeze, oracle_log.md `96adad7`).
**Plan ref**: `docs/eval/phase4_p0_plan.md` §7 Phase 3 (분배 (B) req 12 / app 11 / cross 15 / def 12).

### Pilot rules (P3 적용)

1. **DR-1~5 전수 적용** (P2 cross 와 동일).
2. **DR-5(a) 완화**: P3 는 cross-standard 가 아니므로 "최소 2개 ISA primary" 미적용. category-별 single-ISA 가 자연 default.
3. **DR-5(b)**: cross-section disjoint 만 적용 — P3 oracle 의 primary 가 P2 N1~N9 + P3 다른 oracle 의 primary 와 disjoint.
4. **DR-5(c) Option D 적용**: primary section ∈ {requirements, application, definitions} (objective 제외). category 와 일치 (req oracle → section=requirements).
5. **DR-6 ad-hoc review**: query 작성 후 DR-4 strict tokenization ∩ ∈ {2, 3} 발견 시 DA peer-DM 2-test (axis expansion + natural phrasing + token from primary top-20). PASS 시 enhanced query 채택, FAIL 시 그대로 수용 + (c) intentional gap 처리.
6. **Phase 진행**: Requirements (Q36~Q40) → Application (Q41~Q45) → Definitions (Q46~Q50). 묶음 단위 DA spot-check.

### Q36 — ISA 230 감사문서 형태·취합·보존 요구사항 (requirements)

```yaml
query_id: "Q36"
category: "requirements"
isa_focus: "230"
question: "감사인은 감사문서를 어떻게 작성해야 하며, 최종감사파일을 취합하고, 보존기간 종료 전까지 감사문서를 어떻게 보존해야 하는가"
oracle_primary:
  - chunk_id: "230:00893:8"     # ¶8 감사문서 형태·내용·범위 (감사인은 감사문서를 작성해야 한다)
  - chunk_id: "230:00911:14"    # ¶14 최종감사파일 취합
  - chunk_id: "230:00912:15"    # ¶15 보존기간 종료 전 폐기 금지
oracle_related:
  expected_related_chunks:
    - "230:00890:7"   # ¶7 적시 감사문서 작성 (선행 paragraph)
    - "230:00897:9"   # ¶9 감사절차의 식별자 / 검토자
    - "230:00901:10"  # ¶10 검토 사항
    - "230:00902:11"  # ¶11 토의·결론
    - "230:00904:12"  # ¶12 변경 사항
    - "230:00906:13"  # ¶13 수행 시기
```

**chunk 본문 인용 (DR-1 stub 검증)**

- `230:00893:8` (cc=165, refs=["A2","A3","A4","A5"]) heading_trail = ["감사기준서 230  감사문서", "요구사항", "수행한 감사절차와 입수한 감사증거의 문서화", "감사문서의 형태, 내용 및 범위"]
  > "8. 감사인은 이전에 해당 감사에 관여되지 아니한 숙련된 감사인이 다음 사항을 충분히 이해할 수 있도록 감사문서를 작성해야 한다. (문단 A2-A5, A16-A17 참조)"
- `230:00911:14` (cc=139, refs=["A21","A22"]) heading_trail = ["감사기준서 230  감사문서", "요구사항", "최종감사파일의 취합"]
  > "14. 감사인은 감사와 관련된 문서들을 하나의 감사파일로 취합하여야 하며, 감사보고서일 후 최종감사파일을 취합하는 행정적인 절차를 적시에 완료하여야 한다. (문단 A21-A22 참조)"
- `230:00912:15` (cc=172, refs=["A23"]) heading_trail = ["감사기준서 230  감사문서", "요구사항", "최종감사파일의 취합"]
  > "15. 감사인은 최종감사파일의 취합이 완료된 후에는 그 보존기간 (주식회사 등의 외부감사에 관한 법률에 따른 감사의 경우 감사종료 시점부터 법정기한) 종료 전까지 어떠한 성격의 감사문서도 삭제하거나 폐기하여서는 안 된다. (문단 A23 참조)"

**DR check**

```
[✓] DR-1 (req, NIT-Q36) — stub 패턴 부재
    근거: 3 primary 모두 substantive 본문 (cc 165/139/172 > 115). lead-in "다음과 같다" 패턴 없음. ¶8 본문이 "다음 사항" 도입이지만 본 chunk 자체에 substantive 진술 ("감사문서를 작성해야 한다") 포함 → stub 아님 (substantive lead-in)
[✓] DR-2 (req, NIT-Q36) — heading_trail 정합
    근거: 230:8 = 요구사항/감사문서의 형태·내용·범위; 230:14/15 = 요구사항/최종감사파일의 취합. resolver 매핑 시 path-suffix `230:?:8/14/15` 직접 hit
[✓] DR-3 (req, NIT-Q36) — paragraph_id numeric
    근거: ["8"]/["14"]/["15"] 모두 numeric, Roman/alpha (i) 모호성 부재
[✓] DR-4 (req, NIT-Q36) — strict tokenization ∩ ≥ 2
    근거 (whitespace + lowercase + stopword {의,은,는,이,가,에,와,과,을,를,수,등,및,한,한다,있다,하는} 제거):
    query top-20: [감사인은, 감사문서를(2), 어떻게(2), 작성해야, 하며, 최종감사파일을, 취합하고, 보존기간, 종료, 전까지, 보존해야, 하는가]
    primary 230:8 ∩ {감사인은, 감사문서를, 작성해야} = 3
    primary 230:14 ∩ {감사인은, 최종감사파일을} = 2 (hit, =2)
    primary 230:15 ∩ {감사인은, 보존기간, 종료, 전까지} = 4
[✓] DR-5(a) — req 카테고리, single-ISA 자연 default (P3 pilot rule §2)
    근거: 모두 ISA 230 (intra-standard), DR-5(a) min 2 ISA 미적용 (P2 cross 전용)
[✓] DR-5(b) (req, NIT-Q36) — 다른 oracle primary disjoint
    근거: P2 N1~N9 primary 24개 ∪ P3 (Q37~Q50 미작성, 후속 점진 확장 시 재검증) 와 230:8/14/15 disjoint 확인 (N1~N9 중 ISA 230 chunk 없음)
[✓] DR-5(c) (req, Option D) — primary section ∈ {requirements, application, definitions}
    근거: 3 primary 모두 section=requirements (Option D 누적 P3 3/3 = 100% 유지)
```

→ 7 항목 (DR-5 3 sub-rule) 전수 ✓.

**∩ margin 분류**: 230:8 ∩=3 (≥3) / 230:14 ∩=2 (=2 hit, DR-6 ad-hoc 후보) / 230:15 ∩=4 (≥3).

**DR-6 ad-hoc trigger** (230:14 ∩=2):

```yaml
dr6_adhoc_review:
  candidate_chunk_id: "230:00911:14"
  current_intersection: 2
  zone: "{2,3}_strict"
  proposed_enhancement: "감사인은 감사문서를 작성해야 하며, 감사파일로 취합하여야 하고, 최종감사파일을 어떻게 취합하며 보존기간 종료 전까지 감사문서를 보존해야 하는가"
  enhancement_added_tokens: ["감사파일로", "취합하여야"]
  expected_intersection_post: 4   # +감사파일로, +취합하여야
  da_2test_status: "pending"      # DA peer-DM 회부 예정 (Q36~Q40 묶음 발송)
```

### S4 prescreen 측정 보류 (P5 일괄)

P2 N1~N9 와 동일 — P5 audit 시점 v3 신규 24 primary 일괄 측정.
```

### Q37 — ISA 450 왜곡표시 집계·평가·커뮤니케이션 요구사항 (requirements)

```yaml
query_id: "Q37"
category: "requirements"
isa_focus: "450"
question: "감사인은 식별된 왜곡표시를 어떻게 집계하고, 경영진이 수정을 거절한 경우 그 사유를 어떻게 평가하며, 미수정왜곡표시를 지배기구와 어떻게 커뮤니케이션하여야 하는가"
oracle_primary:
  - chunk_id: "450:04211:5"     # ¶5 식별된 왜곡표시 집계 (lifecycle 1단계)
  - chunk_id: "450:04219:9"     # ¶9 경영진 수정 거절 시 사유 평가 (lifecycle 2단계)
  - chunk_id: "450:04226:12"    # ¶12 지배기구 커뮤니케이션 (lifecycle 3단계)
oracle_related:
  expected_related_chunks:
    - "450:04213:6"   # ¶6 전반감사전략 수정 결정
    - "450:04216:7"   # ¶7 적시 검토
    - "450:04221:10"  # ¶10 미수정왜곡표시 평가 사전 중요성 재평가
    - "450:04222:11"  # ¶11 미수정왜곡표시 중요성 결정 (N4 primary, related 로만 등록)
    - "450:04227:13"  # ¶13 과거 미수정왜곡표시 영향
    - "450:04229:14"  # ¶14 경영진 커뮤니케이션
```

**chunk 본문 인용 (DR-1 stub 검증)**

- `450:04211:5` (cc=133, refs=["A2","A3","A4","A5","A6"]) heading_trail = ["감사기준서 450  감사 중 식별된 왜곡표시의 평가", "요구사항", "식별된 왜곡표시의 집계"]
  > "5. 감사인은 명백하게 사소한(clearly trivial) 것을 제외하고는 감사 중 식별된 왜곡표시를 집계하여야 한다. (문단 A2-A6 참조)"
- `450:04219:9` (cc=204, refs=["A13"]) heading_trail = ["감사기준서 450  감사 중 식별된 왜곡표시의 평가", "요구사항", "왜곡표시의 커뮤니케이션과 수정"]
  > "9. 만약 경영진이 감사인이 커뮤니케이션한 왜곡표시의 일부 또는 전부에 대하여 수정을 거절하는 경우, 감사인은 경영진이 수정하지 않는 사유를 이해하여야 하며 재무제표 전체에 중요한 왜곡표시가 없는지 여부를 평가할 때 그 사유를 고려하여야 한다. (문단 A13 참조)"
- `450:04226:12` (cc=259, refs=["A26","A27","A28"]) heading_trail = ["감사기준서 450  감사 중 식별된 왜곡표시의 평가", "요구사항", "미수정왜곡표시의 영향에 대한 평가", "지배기구와의 커뮤니케이션"]
  > "12. 감사인은 법규상 금지되지 않는 한 미수정왜곡표시 및 이것이 개별적으로 또는 집합적으로 감사의견에 미칠 영향에 대하여 지배기구와 커뮤니케이션하여야 한다. 감사인은 커뮤니케이션을 할 때 중요한 미수정왜곡표시들을 개별적으로 식별하여야 한다. 감사인은 그러한 미수정왜곡표시들을 수정하도록 요청하여야 한다. (문단 A26-A28참조)"

**DR check**

```
[✓] DR-1 (req, NIT-Q37) — stub 패턴 부재
    근거: 3 primary 모두 substantive 본문 (cc 133/204/259 > 115). lead-in "다음과 같다" 패턴 없음
[✓] DR-2 (req, NIT-Q37) — heading_trail 정합
    근거: 450:5 = 요구사항/식별된 왜곡표시의 집계; 450:9 = 요구사항/왜곡표시의 커뮤니케이션과 수정; 450:12 = 요구사항/미수정왜곡표시의 영향에 대한 평가/지배기구와의 커뮤니케이션. resolver 매핑 path-suffix `450:?:5/9/12` 직접 hit
[✓] DR-3 (req, NIT-Q37) — paragraph_id numeric
    근거: ["5"]/["9"]/["12"] 모두 numeric, Roman/alpha (i) 모호성 부재
[✓] DR-4 (req, NIT-Q37) — strict tokenization ∩ ≥ 2
    근거 (whitespace + lowercase + stopword 제거):
    query top-20: [감사인은, 식별된, 왜곡표시를, 어떻게(3), 집계하고,, 경영진이, 수정을, 거절한, 경우, 그, 사유를, 평가하며,, 미수정왜곡표시를, 지배기구와, 커뮤니케이션하여야, 하는가]
    primary 450:5 ∩ {감사인은, 식별된, 왜곡표시를} = 3
    primary 450:9 ∩ {감사인은, 경영진이(2), 수정을, 사유를, 그} = 5
    primary 450:12 ∩ {감사인은, 지배기구와, 커뮤니케이션하여야} = 3 (hit, =3 — DR-6 ad-hoc 후보)
[✓] DR-5(a) — req 카테고리, single-ISA 자연 default
    근거: 모두 ISA 450 (intra-standard)
[✓] DR-5(b) (req, NIT-Q37) — 다른 oracle primary disjoint
    근거: P2 N4 primary {705:08655:8, 700:08024:18, 450:04222:11} ∩ Q37 primary {450:5, 9, 12} = ∅. 단 450:11 (N4) 가 본 Q37 expected_related 에 등록됨 → DA Clarification 1 schema (`primary_vs_related_overlap` reverse: N4 primary ↔ Q37 related). P5 retrofit 추적 필요
[✓] DR-5(c) (req, Option D) — primary section ∈ {requirements, application, definitions}
    근거: 3 primary 모두 section=requirements (Option D 누적 P3 6/6 = 100% 유지)
```

→ 7 항목 (DR-5 3 sub-rule) 전수 ✓.

**∩ margin 분류**: 450:5 ∩=3 (=3 hit, DR-6 ad-hoc 후보) / 450:9 ∩=5 (≥3) / 450:12 ∩=3 (=3 hit, DR-6 ad-hoc 후보).

**DR-6 ad-hoc trigger** (450:5 + 450:12 모두 ∩=3, 둘 다 zone {2,3}):

```yaml
dr6_adhoc_review:
  - candidate_chunk_id: "450:04211:5"
    current_intersection: 3
    zone: "{2,3}_strict"
    proposed_enhancement: "감사인은 명백하게 사소한 것을 제외한 감사 중 식별된 왜곡표시를 어떻게 집계하고, 경영진이 수정을 거절한 경우 사유를 어떻게 평가하며, 미수정왜곡표시를 지배기구와 어떻게 커뮤니케이션하여야 하는가"
    enhancement_added_tokens: ["명백하게", "사소한", "감사", "중"]
    expected_intersection_post: 7   # +명백하게, +사소한, +감사, +중
    da_2test_status: "pending"
  - candidate_chunk_id: "450:04226:12"
    current_intersection: 3
    zone: "{2,3}_strict"
    proposed_enhancement: "감사인은 법규상 금지되지 않는 한 미수정왜곡표시 및 그것이 감사의견에 미칠 영향을 지배기구와 커뮤니케이션하여야 하는가; 식별된 왜곡표시 집계와 경영진 수정 거절 시 사유 평가도 함께 어떻게 수행하는가"
    enhancement_added_tokens: ["법규상", "금지되지", "않는", "감사의견에", "영향을"]
    expected_intersection_post: 6
    da_2test_status: "pending"
```

**Cross-oracle primary-vs-related overlap 경계** (DA Clarification 1 schema 적용):

```yaml
primary_vs_related_overlap:
  - source_oracle: "Q37"
    source_role: "related"
    target_oracle: "N4"
    target_role: "primary"
    chunk_id: "450:04222:11"
    diagnostic_target: "P5 S4 cross-oracle primary-vs-related overlap (within-section 동일 ISA 450 within-requirements)"
```

### S4 prescreen 측정 보류 (P5 일괄)

P2 N1~N9 와 동일 — P5 audit 시점 v3 신규 24 primary 일괄 측정.

### Q38 — ISA 580 경영진 책임 서면진술·시기·기타 진술 요구사항 (requirements)

```yaml
query_id: "Q38"
category: "requirements"
isa_focus: "580"
question: "감사인은 경영진에게 재무제표 작성 책임에 관한 서면진술을 어떤 형태로 요청하여야 하며, 서면진술일은 감사보고서일에 어떻게 근접하게 결정하여야 하는가, 또한 다른 감사기준서가 요구하는 추가 서면진술은 어떻게 요청하는가"
oracle_primary:
  - chunk_id: "580:06734:10"    # ¶10 재무제표 작성 책임 서면진술 (lifecycle 1단계)
  - chunk_id: "580:06744:14"    # ¶14 서면진술일 / 대상기간 (lifecycle 2단계)
  - chunk_id: "580:06742:13"    # ¶13 기타 서면진술 (lifecycle 3단계, β-prime swap from 580:15)
oracle_related:
  expected_related_chunks:
    - "580:06731:9"   # ¶9 경영진 식별 / 책임 서두
    - "580:06736:11"  # ¶11 정보 완전성 진술 (entry)
    - "580:06746:15"  # ¶15 서면진술 형태 (β-prime swap source — related 강등)
    - "580:06749:16"  # ¶16 신뢰성 의문 (entry)
    - "580:06750:17"  # ¶17 일관성 부재 시 절차
    - "580:06751:18"  # ¶18 신뢰 불가 시 705 연계
```

**chunk 본문 인용 (DR-1 stub 검증)**

- `580:06734:10` (cc=200, refs=["A7","A8","A9"]) heading_trail = ["감사기준서 580  서면진술", "요구사항", "경영진책임에 관한 서면진술", "재무제표의 작성"]
  > "10. 감사인은 감사업무 조건에서 정한 바와 같이 경영진이 해당 재무보고체계에 따라 재무제표를 작성할 책임 (관련성이 있는 경우 재무제표의 공정표시책임을 포함)을 완수하였다는 서면진술을 제공하도록 경영진에게 요청하여야 한다. (문단 A7-A9, A14, A22 참조)"
- `580:06744:14` (cc=169, refs=["A15","A16","A17","A18"]) heading_trail = ["감사기준서 580  서면진술", "요구사항", "서면진술일과 대상기간"]
  > "14. 서면진술일은 가능한 재무제표에 대한 감사보고서일에 실행가능한 가장 근접한 날로 하되, 감사보고서일보다 늦지 않아야 한다. 서면진술은 감사보고서에서 언급된 모든 재무제표와 기간을 대상으로 하여야 한다. (문단 A15-A18 참조)"
- `580:06742:13` (cc=272, refs=["A10","A11","A12","A13"]) heading_trail = ["감사기준서 580  서면진술", "요구사항", "기타 서면진술"]
  > "13. 이 감사기준서 외에 다른 감사기준서에서도 감사인에게 서면진술을 요청하도록 요구한다. 다른 감사기준서가 요구하는 그러한 진술 외에, 재무제표 또는 재무제표 내 (하나 또는 그 이상의) 특정 경영진주장과 관련된 다른 감사증거를 뒷받침할 수 있는 (하나 또는 그 이상의) 서면진술을 입수하는 것이 필요하다고 결정하는 경우에는, 감사인은 그러한 서면진술을 추가로 요청하여야 한다. (문단 A10-A13, A14, A22 참조)"

**β-prime swap 결정 근거** (580:15 → 580:13):

```yaml
swap_decision:
  original: "580:06746:15"   # 서면진술 형태 (¶15 cc=236)
  swapped_to: "580:06742:13"  # 기타 서면진술 (¶13 cc=272)
  reason:
    - "DR-4 ∩ token 분석: 580:15 ∩=0~1 (감사인을 vs 감사인은 surface 분리, 형태이어야 vs 형태로 분리). 본문 'surface form drift' 가 strict tokenization 에서 매칭 실패"
    - "swap target 580:13 ∩=4 (감사인은, 서면진술을, 재무제표, 요청하여야 직접 매칭)"
    - "lifecycle 의미 측면: ¶10 (책임) → ¶14 (시기) → ¶13 (기타 서면진술 요청 expansion) 으로 더 wide coverage. ¶15 (형태) 는 cohesive but narrow"
    - "DR-1: ¶15 cc=236 도 substantive (stub 아님), 단 query-primary token 매칭 실패가 DR-4 결정적"
  reference: "P2 N3 (315:11→23 swap), N4 (705:6→8, 700:17→18 swap) precedent"
```

**DR check**

```
[✓] DR-1 (req, NIT-Q38) — stub 패턴 부재
    근거: 3 primary 모두 substantive (cc 200/169/272 > 115)
[✓] DR-2 (req, NIT-Q38) — heading_trail 정합
    근거: 580:10 = 요구사항/경영진책임/재무제표의 작성; 580:14 = 요구사항/서면진술일과 대상기간; 580:13 = 요구사항/기타 서면진술. resolver 매핑 path-suffix `580:?:10/14/13` 직접 hit
[✓] DR-3 (req, NIT-Q38) — paragraph_id numeric
    근거: ["10"]/["14"]/["13"] 모두 numeric
[✓] DR-4 (req, NIT-Q38) — strict tokenization ∩ ≥ 2 (β-prime swap 후)
    근거 (whitespace + lowercase + stopword 제거):
    query top-20: [감사인은, 경영진에게, 재무제표(2), 작성, 책임에, 관한, 서면진술을(2), 어떤, 형태로, 요청하여야(2), 하며, 서면진술일은, 감사보고서일에, 어떻게(2), 근접하게, 결정하여야, 또한, 다른, 감사기준서가, 요구하는, 추가, 요청하는가]
    primary 580:10 ∩ {감사인은, 경영진에게, 서면진술을, 요청하여야} = 4
    primary 580:14 ∩ {서면진술일은, 감사보고서일에} = 2 (hit, =2 — DR-6 ad-hoc 후보)
    primary 580:13 ∩ {감사인은, 서면진술을, 재무제표, 요청하여야, 다른, 감사기준서가, 요구하는, 추가} = 8
[✓] DR-5(a) — req 카테고리, single-ISA 자연 default
    근거: 모두 ISA 580 (intra-standard)
[✓] DR-5(b) (req, NIT-Q38) — 다른 oracle primary disjoint
    근거: P2 N1~N9 ∪ P3 Q36/Q37 primary 와 ISA 580 chunk 0건 → ∅ ✓
[✓] DR-5(c) (req, Option D) — primary section ∈ {requirements, application, definitions}
    근거: 3 primary 모두 section=requirements (Option D 누적 P3 9/9 = 100% 유지)
```

→ 7 항목 (DR-5 3 sub-rule) 전수 ✓.

**∩ margin 분류**: 580:10 ∩=4 (≥3) / 580:14 ∩=2 (=2 hit, DR-6 ad-hoc 후보) / 580:13 ∩=8 (≥3).

**DR-6 ad-hoc trigger** (580:14 ∩=2):

```yaml
dr6_adhoc_review:
  candidate_chunk_id: "580:06744:14"
  current_intersection: 2
  zone: "{2,3}_strict"
  proposed_enhancement: "감사인은 경영진에게 재무제표 작성 책임 서면진술을 어떤 형태로 요청하여야 하며, 서면진술일은 감사보고서일에 가능한 근접한 날로 결정하고 서면진술은 감사보고서에서 언급된 모든 재무제표와 기간을 대상으로 하여야 하는가; 다른 감사기준서가 요구하는 추가 서면진술은 어떻게 요청하는가"
  enhancement_added_tokens: ["가능한", "근접한", "날로", "감사보고서에서", "언급된", "모든", "기간을", "대상으로"]
  expected_intersection_post: 8
  da_2test_status: "pending"
```

### S4 prescreen 측정 보류 (P5 일괄)

P2 N1~N9 와 동일 — P5 audit 시점 v3 신규 24 primary 일괄 측정.

### Q39 — ISA 700 의견 형성·수신인·공정 표시 평가 요구사항 (requirements)

```yaml
query_id: "Q39"
category: "requirements"
isa_focus: "700"
question: "감사인은 재무제표가 해당 재무보고체계에 따라 작성되었는지 의견을 어떻게 형성하여야 하며, 감사보고서는 해당 감사의 상황에 기초하여 적합한 수신인을 어떻게 기재하여야 하고, 재무제표가 공정한 표시를 달성하고 있는지 여부를 어떻게 평가하여야 하는가"
oracle_primary:
  - chunk_id: "700:08000:10"    # ¶10 의견 형성 핵심 entry
  - chunk_id: "700:08032:22"    # ¶22 수신인 기재
  - chunk_id: "700:08025:19"    # ¶19 공정 표시 평가 (준수체계 시)
oracle_related:
  expected_related_chunks:
    - "700:08001:11"  # ¶11 의견 형성 결론 사항 lead-in
    - "700:08005:12"  # ¶12 결론 도출
    - "700:08015:14"  # ¶14 정성적 평가
    - "700:08018:15"  # ¶15 재무보고체계 언급/기술 평가
    - "700:08027:20"  # ¶20 감사보고서 서면방식 (cc=88, related 만)
    - "700:08030:21"  # ¶21 감사보고서 제목
    - "700:08034:23"  # ¶23 감사의견 단락
```

**chunk 본문 인용 (DR-1 stub 검증)**

- `700:08000:10` (cc=122, refs=[]) heading_trail = ["감사기준서 700  재무제표에 대한 의견형성과 보고", "요구사항", "재무제표에 대한 의견형성"]
  > "10. 감사인은 재무제표가 중요성의 관점에서 해당 재무보고체계에 따라 작성되었는지 여부에 대하여 의견을 형성하여야 한다."
- `700:08032:22` (cc=136, refs=["A21"]) heading_trail = ["감사기준서 700  재무제표에 대한 의견형성과 보고", "요구사항", "감사보고서", "감사기준에 따라 수행된 감사에 대한 감사보고서", "수신인"]
  > "22. 감사보고서는 해당 감사의 상황에 기초하여 적합한 수신인을 기재하여야 한다. (문단 A21 참조)"
- `700:08025:19` (cc=296, refs=["A17"]) heading_trail = ["감사기준서 700  재무제표에 대한 의견형성과 보고", "요구사항", "의견의 형태"]
  > "19. 재무제표가 준수체계에 따라 작성되는 경우, 감사인은 재무제표가 공정한 표시를 달성하고 있는지 여부를 평가하도록 요구되지 않는다. 그러나 감사인이 그러한 재무제표가 오도한다는 결론을 내리는 극히 드문 상황이라면, 감사인은 이 사항을 경영진과 논의하여야 한다. 또한 감사인은 이 사항이 어떻게 해결되었는지에 따라 감사보고서에 그러한 사항을 커뮤니케이션을 할 것인지 여부 및 어떻게 커뮤니케이션을 할 것인지 결정하여야 한다. (문단 A17 참조)"

**stub 회피 결정**: 700:08027:20 (¶20 "감사인의 보고는 서면방식에 의하여야 한다." cc=88 < 115) 는 DR-1 stub 의심으로 primary 채택 하지 않고 related 만 등록. 본 ¶20 는 substantive single-sentence 이지만 char_count 임계 보수 적용.

**DR check**

```
[✓] DR-1 (req, NIT-Q39) — stub 패턴 부재
    근거: 3 primary 모두 substantive 본문 (cc 122/136/296). 700:10 cc=122 marginal (115 + 7) 정당화: ¶10 = 의견형성 root requirement, semantic substantive 강함, cc 단일 임계 marginal pass. ¶20 (cc=88) 회피로 stub-bias 차단
[✓] DR-2 (req, NIT-Q39) — heading_trail 정합
    근거: 700:10 = 요구사항/재무제표에 대한 의견형성; 700:22 = 요구사항/감사보고서/.../수신인; 700:19 = 요구사항/의견의 형태. resolver 매핑 path-suffix `700:?:10/22/19` 직접 hit
[✓] DR-3 (req, NIT-Q39) — paragraph_id numeric
    근거: ["10"]/["22"]/["19"] 모두 numeric
[✓] DR-4 (req, NIT-Q39) — strict tokenization ∩ ≥ 2
    근거 (whitespace + lowercase + stopword 제거):
    query top-20: [감사인은(2), 재무제표가(2), 해당(2), 재무보고체계에, 따라, 작성되었는지, 의견을, 어떻게(3), 형성하여야, 하며,, 감사보고서는, 감사의, 상황에, 기초하여, 적합한, 수신인을, 기재하여야, 하고,, 공정한, 표시를, 달성하고, 있는지, 여부를, 평가하여야, 하는가]
    primary 700:10 ∩ {감사인은, 재무제표가, 해당, 재무보고체계에, 따라, 작성되었는지, 의견을, 형성하여야} = 8
    primary 700:22 ∩ {감사보고서는, 해당, 감사의, 상황에, 기초하여, 적합한, 수신인을, 기재하여야} = 8
    primary 700:19 ∩ {재무제표가, 감사인은, 공정한, 표시를, 달성하고, 있는지, 여부를} = 7
[✓] DR-5(a) — req 카테고리, single-ISA 자연 default
    근거: 모두 ISA 700 (intra-standard)
[✓] DR-5(b) (req, NIT-Q39) — 다른 oracle primary disjoint
    근거: P2 N4 primary {700:18}, N5 primary {700:29} ∪ Q36/Q37/Q38 primary 와 700:10/22/19 disjoint ✓ (within-ISA cross-oracle within-requirements)
[✓] DR-5(c) (req, Option D) — primary section ∈ {requirements, application, definitions}
    근거: 3 primary 모두 section=requirements (Option D 누적 P3 12/12 = 100% 유지)
```

→ 7 항목 (DR-5 3 sub-rule) 전수 ✓.

**∩ margin 분류**: 700:10 ∩=8 (≥3) / 700:22 ∩=8 (≥3) / 700:19 ∩=7 (≥3). DR-6 ad-hoc trigger 없음.

**Cross-oracle within-ISA proximity 경계 사항**:

```yaml
monitored_pair:
  - pair_id: "P-7"
    pair_type: "cross_oracle_distant_same_isa"
    oracles: ["N4", "Q39"]
    isa: "700"
    chunks: ["700:08024:18", "700:08000:10"]
    distance_paragraphs: 8
    diagnostic_target: "P5 S4 within-ISA cross-section adjacent (N4 700:18 ↔ Q39 700:10 의견형성 root)"
  - pair_id: "P-8"
    pair_type: "cross_oracle_distant_same_isa"
    oracles: ["N5", "Q39"]
    isa: "700"
    chunks: ["700:08053:29", "700:08025:19"]
    distance_paragraphs: 10
    diagnostic_target: "P5 S4 within-ISA cross-section distant (N5 700:29 ↔ Q39 700:19 공정표시)"
```

ISA 700 cluster 가 N4/N5/Q39 3-oracle 분포 — ISA 315 cluster (N2/N3/N6) 와 동일 패턴. P5 within-ISA cluster diagnostic 누적.

### S4 prescreen 측정 보류 (P5 일괄)

P2 N1~N9 와 동일 — P5 audit 시점 v3 신규 24 primary 일괄 측정.

### Q40 — ISA 610 내부감사기능 이용 결정·평가·커뮤니케이션 요구사항 (requirements)

```yaml
query_id: "Q40"
category: "requirements"
isa_focus: "610"
question: "외부감사인은 내부감사기능이 수행한 업무를 활용할 영역과 범위를 어떻게 결정하며, 표명된 감사의견에 대한 책임을 고려하여 집합적으로 어떻게 평가하고, 지배기구와 어떻게 커뮤니케이션하여야 하는가"
oracle_primary:
  - chunk_id: "610:07502:17"    # ¶17 활용 영역·범위 결정 근거
  - chunk_id: "610:07510:19"    # ¶19 집합적 평가 (전적 책임 고려)
  - chunk_id: "610:07511:20"    # ¶20 지배기구 커뮤니케이션
oracle_related:
  expected_related_chunks:
    - "610:07493:15"  # ¶15 객관성 평가 entry
    - "610:07497:16"  # ¶16 적격성 평가 entry
    - "610:07502:17"  # ¶17 자체 (primary)
    - "610:07503:18"  # ¶18 작업 평가 절차 (sub-item lead-in)
    - "610:07513:21"  # ¶21 활용 결정 검토
    - "610:07514:22"  # ¶22 작업 적정성 평가
    - "610:07515:23"  # ¶23 활용 시 작업 평가
```

**chunk 본문 인용 (DR-1 stub 검증)**

- `610:07502:17` (cc=269, refs=["A15","A16","A17"]) heading_trail = ["감사기준서 610  내부감사인이 수행한 업무의 활용", "요구사항", "내부감사기능이 수행한 업무가 활용될 수 있는지 여부, 활용 영역 및 활용 범위의 결정", "활용 가능한 내부감사기능 수행 업무의 성격 및 범위의 결정"]
  > "17. 내부감사기능이 수행한 업무가 활용될 수 있는 영역과 범위를 결정하는 근거로서, 외부감사인은 내부감사기능이 수행하였거나 수행예정인 업무의 성격 및 범위 그리고 외부감사인의 전반감사전략 및 감사계획에 대한 관련성을 고려하여야 한다. (문단 A15-A17 참조)"
- `610:07510:19` (cc=265, refs=["A15","A16","A17","A18","A19","A20","A21","A22"]) heading_trail = ["감사기준서 610  내부감사인이 수행한 업무의 활용", "요구사항", "내부감사기능이 수행한 업무가 활용될 수 있는지 여부, 활용 영역 및 활용 범위의 결정", "활용 가능한 내부감사기능 수행 업무의 성격 및 범위의 결정"]
  > "19. 외부감사인은 표명된 감사의견에 대한 외부감사인의 전적인 책임을 고려하여, 외부감사인은 내부감사기능이 수행한 업무를 계획된 범위까지 활용하여 외부감사인이 여전히 감사에 충분히 참여하도록 하는지를 집합적으로 평가하여야 한다. (문단 A15-A22 참조)"
- `610:07511:20` (cc=240, refs=["A23"]) heading_trail = ["감사기준서 610  내부감사인이 수행한 업무의 활용", "요구사항", "내부감사기능이 수행한 업무가 활용될 수 있는지 여부, 활용 영역 및 활용 범위의 결정", "활용 가능한 내부감사기능 수행 업무의 성격 및 범위의 결정"]
  > "20. 감사기준서 260에 따라 계획된 감사범위와 시기에 대한 개요를 지배기구와 커뮤니케이션할 때, 외부감사인은 내부감사기능이 수행한 업무를 어떻게 활용할 계획인지를 커뮤니케이션하여야 한다. (문단 A23 참고)"

**DR check**

```
[✓] DR-1 (req, NIT-Q40) — stub 패턴 부재
    근거: 3 primary 모두 substantive 본문 (cc 269/265/240 모두 ≥ 240, robust). lead-in "다음과 같다" 패턴 없음
[✓] DR-2 (req, NIT-Q40) — heading_trail 정합
    근거: 3 primary 모두 동일 sub-section "활용 가능한 내부감사기능 수행 업무의 성격 및 범위의 결정" 하위 (cohesive). resolver 매핑 path-suffix `610:?:17/19/20` 직접 hit
[✓] DR-3 (req, NIT-Q40) — paragraph_id numeric
    근거: ["17"]/["19"]/["20"] 모두 numeric
[✓] DR-4 (req, NIT-Q40) — strict tokenization ∩ ≥ 2
    근거 (whitespace + lowercase + stopword 제거):
    query top-20: [외부감사인은, 내부감사기능이, 수행한, 업무를, 활용할, 영역과, 범위를, 어떻게(3), 결정하며,, 표명된, 감사의견에, 대한, 책임을, 고려하여, 집합적으로, 평가하고,, 지배기구와, 커뮤니케이션하여야, 하는가]
    primary 610:17 ∩ {내부감사기능이, 수행한, 영역과, 범위를} = 4
    primary 610:19 ∩ {외부감사인은, 내부감사기능이, 수행한, 업무를, 표명된, 감사의견에, 대한, 책임을, 집합적으로} = 9
    primary 610:20 ∩ {외부감사인은, 내부감사기능이, 수행한, 업무를, 지배기구와, 커뮤니케이션하여야} = 6
[✓] DR-5(a) — req 카테고리, single-ISA 자연 default
    근거: 모두 ISA 610 (intra-standard)
[✓] DR-5(b) (req, NIT-Q40) — 다른 oracle primary disjoint
    근거: P2 N1~N9 ∪ P3 Q36~Q39 primary 와 ISA 610 chunk 0건 → ∅ ✓
[✓] DR-5(c) (req, Option D) — primary section ∈ {requirements, application, definitions}
    근거: 3 primary 모두 section=requirements (Option D 누적 P3 15/15 = 100% 유지, 종합 누적 27/27)
```

→ 7 항목 (DR-5 3 sub-rule) 전수 ✓.

**∩ margin 분류**: 610:17 ∩=4 (≥3) / 610:19 ∩=9 (≥3) / 610:20 ∩=6 (≥3). DR-6 ad-hoc trigger 없음.

### S4 prescreen 측정 보류 (P5 일괄)

P2 N1~N9 와 동일 — P5 audit 시점 v3 신규 24 primary 일괄 측정.

---

## P3 Phase 1 (Requirements Q36~Q40) — DA spot-check 대기

**Status**: 5/15 oracle 작성 완료 (Q36~Q40), Application + Definitions 미진입.

| oracle | ISA | primary count | DR 7/7 | swap | DR-6 ad-hoc | ∩ 분포 |
|---|---|---:|---|---|---|---|
| Q36 | 230 | 3 | ✓ | 0 | 1 (230:14 ∩=2) | 3/2/4 |
| Q37 | 450 | 3 | ✓ | 0 | 2 (450:5 ∩=3, 450:12 ∩=3) | 3/5/3 |
| Q38 | 580 | 3 | ✓ | 1 (580:15→13 β-prime) | 1 (580:14 ∩=2) | 4/2/8 |
| Q39 | 700 | 3 | ✓ | 0 | 0 | 8/8/7 |
| Q40 | 610 | 3 | ✓ | 0 | 0 | 4/9/6 |

**P3 Requirements 누적**: primary 15 / DR 35/35 ✓ / swap 1건 / DR-6 ad-hoc 4 cases / ∩ 분포 ≥3:11, =3:2, =2:2.

**Cross-oracle 추가 proximity (P-7, P-8)**: ISA 700 cluster (N4/N5/Q39 3-oracle 분포) — P5 within-ISA cluster diagnostic 누적.

**Cross-oracle primary-vs-related overlap (Q37 ↔ N4, 1건 추가)**: 450:11 N4 primary ↔ Q37 related (within-ISA within-requirements). P5 retrofit 추적.

DA Phase 1 Requirements 묶음 spot-check 대기. PASS 시 → Phase 2 (Application Q41~Q45) 진입. DR-6 ad-hoc 4 cases 묶어 DA 2-test 회부.
