# Query Design Rules — DR-1 ~ DR-5

> 담당: `audit-domain-expert`
> 적용 phase: Phase 4 P0 (queries.yaml v2 → v3, 신규 24 쿼리 Q27–Q50)
> 근거 문서:
> - `docs/eval/queries.yaml` v2 (Q10/Q14/Q16/Q24/Q25 evidence block — 포맷 표준)
> - `docs/eval/phase3_failure_analysis.md` §3.2 (17 실패 bucket), §5 (gold 수정 권고),
>   §5.5 (v2 실측 효과), §5.6 (UPS stub-bias), §8 (역검증), §9 P5 ((i) 모호성)
> - `docs/eval/phase3_self_audit_2026_04_19.md` §2 (chunk_id 중복 오염), §4.1 (resolver 업그레이드)
> - `src/audit_parser/eval.py:99-151` (`resolve_logical_path` 2-pass)
>
> 본 문서는 Phase 3 v1 → v2 gold 수정 5건 (Q10/Q14/Q16/Q24/Q25) 과 §5.3 deferred
> 3건 (Q11/Q18/Q19) 의 실패 원인을 추출해 **재발 방지 design rule** 로 고착한다.
> P2/P3 신규 oracle 작성 시 5 DR 체크리스트 모두 ✓ 가 아니면 evidence block
> 채택 금지. DA 서명 후 P2/P3 진입.

---

## 0. Scope & 정합 원칙

- **적용 대상**: P2 cross 9개 (N1~N9 → Q27~Q35), P3 req 5 + app 5 + def 5
  (Q36~Q50). 총 24 쿼리.
- **적용 제외**: v2 Q01–Q26 (append-only 정책, plan §6).
  v2 §5.3 deferred (Q11/Q18/Q19) 도 P0 scope 밖 — Phase 4 P3.
- **DR 충돌 시**: 본 문서 lead 보고 → DR 수정 후 P2/P3 재진입.
  사일런트 회피 금지 (Phase 3 v1 워크숍 부재가 v1 5건 실패의 root cause).

---

## DR-1 — Intro-parent stub 금지

### 규칙

`{isa}:{N}` 형태의 parent paragraph chunk 가 본문 패턴
`"{N}. 감사기준에서 사용하는 용어의 정의는 다음과 같다."` 또는
`"{N}. 이 감사기준서와 관련된 감사인의 목적은 다음과 같다."` 류 **stub**
인 경우, primary 로 지정 금지. 실제 정의/목적은 직후 서브아이템
(`(a)`, `(b)`, …) 에 분산되어 있으므로 primary 는 서브아이템 단위로 지정.

### 판정 기준 (3-step)

1. **본문 패턴 매칭**: chunk 의 `text` 에서 heading_trail prefix 와 paragraph
   번호 (`"13. "`, `"5. "`) 를 제거한 잔여 본문이 다음 정규식 중 하나에
   매칭되면 stub:
   - `^감사기준에서 사용하는 용어의 정의는 다음과 같다\.?$`
   - `^이 감사기준서와 관련된 감사인의 목적은 다음과 같다\.?$`
   - `^.{0,15}는 다음과 같다\.?$` (일반 fallback — 9~15자 인트로 변형)
2. **char_count 보조 신호**: heading_trail prefix 포함 char_count ≤ **115**
   이면 stub 의심군. (Prefix 가 60~80자 차지하므로 본문은 10~50자 내외.)
   임계 115 는 DA NIT-N1 advisory (2026-04-19) 기반 — `220:00726:A4`
   (cc=114, 윤리강령 인트로) / `402:03988:7` (cc=110, 이용자기업 감사인 목적
   인트로) 같은 경계 stub 을 안전하게 커버. FP 위험은 paragraph_ids 단일
   숫자 + section ∈ {definitions, objective, intro} 결합 필터로 0건 확인.
3. **section 검증**: `section in {"definitions", "objective", "intro"}` +
   `paragraph_ids` 에 단일 숫자 (e.g. `["13"]`) 만 포함되면 stub 가능성 ↑.

### Evidence (chunks.jsonl 원문)

```jsonl
# Stub 사례 1 — ISA 200 ¶13 용어의 정의 intro
chunk_id="200:00050:13"  section=definitions  char_count=87
heading_trail=["감사기준서 200  ...", "용어의 정의"]
text="감사기준서 200  독립된 감사인의 전반적인 목적 ... > 용어의 정의\n\n
      13. 감사기준에서 사용하는 용어의 정의는 다음과 같다."
→ heading_trail prefix 제거 후 본문 24자. 임베딩 신호 사실상 0.
```

```jsonl
# Stub 사례 2 — ISA 500 ¶5 용어의 정의 intro
chunk_id="500:04342:5"  section=definitions  char_count=56
text="감사기준서 500  감사증거 > 용어의 정의\n\n
      5. 감사기준에서 사용하는 용어의 정의는 다음과 같다."
```

```jsonl
# Stub 사례 3 — ISA 240 ¶11 목적 intro / ¶12 정의 intro
chunk_id="240:01071:11"  section=objective  char_count=74
text="... > 목적\n\n11. 이 감사기준서와 관련된 감사인의 목적은 다음과 같다."

chunk_id="240:01076:12"  section=definitions  char_count=76
text="... > 용어의 정의\n\n12. 감사기준에서 사용하는 용어의 정의는 다음과 같다."
```

### 실패 사례 (v1 → v2 교체로 입증)

`phase3_failure_analysis.md` §5.5:
- Q14 v1 primary `200:13` (stub) → v2 `200:13.(n)` 추가: BGE 0.0 → 0.0 (별도 §5.7
  쿼리 어휘 문제), UPS 0.33 유지. **gold 라벨로는 stub 회수 불가가 입증**.
- Q16 v1 `200:13` 단독 → v2 `(c)/(e)/(n)` 3개: BGE 0.0 → **0.333**, UPS 0.0 → **0.333**.
- Q24 v1 `240:11`,`240:12` (둘 다 stub) → v2 `240:12.(a)`,`240:2`: BGE 0.0 → **1.0**,
  UPS 0.0 → 0.0 (UPS stub-bias). **stub primary 는 모델 판단력과 무관하게 0 점**.
- Q25 v1 `500:5` (stub) → v2 `500:5.(b)/(c)/(f)`: BGE 0.0 → 0.667, UPS 1.0 → **0.0**.
  v1 UPS 1.0 은 §5.6 stub-bias artefact.

### 운용 결과 (DR-5 제외)

Stub 후보를 primary 가 아닌 **related** 로 강등. heading_trail prefix 가 다른
청크에 prefix 형태로 들어가 있다면 검색 신호로 작동하므로 related 유지는
무해. 단, primary 슬롯은 서브아이템 (a)~(z) 또는 다른 numbered paragraph
(e.g. `240:2` 서론) 로 채운다.

---

## DR-2 — Heading_trail suffix resolver 매핑 로그 검증

### 규칙

`{isa}:{N}.(x)` 형태 logical path 를 primary 로 지정한 모든 쿼리는,
`src/audit_parser/eval.py:99` `resolve_logical_path` 의 **실측 매핑 결과 (Pass 1
또는 Pass 2)** 를 evidence block 에 기록한다. concrete chunk_id 와
`parent_section` 이 의도한 영역 (예: `definitions`) 인지 사람이 검증한다.

### Resolver 동작 요약 (eval.py:99-151)

```python
# Pass 1: parent.section == c.section 인 첫 매치
result = _walk(lambda c: c.section == parent.section)
if result is not None: return result
# Pass 2 (fallback): heading_trail 마지막 element 공유
return _walk(lambda c: _share_heading_suffix(c.heading_trail, parent.heading_trail))
```

`_walk` 는 다음 numeric parent (`\d+[A-Za-z]?`) 또는 ISA 경계까지 forward
스캔. `paragraph_ids` 에 `(x)` 토큰을 가지면서 predicate 를 만족하는 첫 청크
를 반환.

### Evidence — 200:(c) pollution case

`phase3_self_audit_2026_04_19.md` §2.3 에서 ISA 200 정의 `(c)` 가 chunks.jsonl
에 2회 등장한다고 보고:

```jsonl
# Hit 1 (intended) — 용어의 정의 아래
chunk_id="200:00059:(c)"  section=definitions  block_ordinal=59
heading_trail=["...", "용어의 정의"]
text="(c) 감사위험 – 재무제표가 중요하게 왜곡표시되어 있을 경우에 ..."

# Hit 2 (pollution) — 적용지침 아래
chunk_id="200:00115:(c)"  section=application  block_ordinal=115
heading_trail=["...", "적용 및 기타 설명자료", "재무제표감사",
               "재무제표의 작성(문단 4 참조)"]
text="(c) 감사인에게 다음 사항들을 제공할 책임 ..."
```

`200:13.(c)` resolve 시:
- parent = `200:00050:13` (block_ordinal=50, section=definitions)
- Pass 1 first match: section==definitions 인 첫 `(c)` → `200:00059:(c)` ✅
  (intended)
- Pass 2 fallback 미발동.

→ Resolver 가 정확히 작동. **단, evidence block 에 `parent_section=definitions`
명시로 사후 검증 가능 상태 유지**.

`phase3_failure_analysis.md` §2 표 (Q20/Q21/Q22/Q26) 에서 6개 logical path 모두
`parent_section=definitions` 매핑 확인됨 → DR-2 의 검증 절차가 작동했음을
입증.

### 적용 절차 (P2/P3 신규 쿼리)

신규 evidence block 에 다음 미니 표 포함:

```text
| logical_path | concrete_chunk_id | parent_section | block_ordinal | 판정 |
| 315:12.(l)   | 315:02428:(l)     | definitions    | 2428          | ✓ intended |
```

`판정` 컬럼이 ✗ 이면 primary 후보 배제, 또는 logical path 가 아닌 직접
chunk_id 지정으로 우회.

---

## DR-3 — Alphabetical (i) vs Roman (i) 모호성 회피

### 규칙

`{isa}:{N}.(i)` logical path 사용 **금지**. ISA 한글 번역본의 서브아이템은
alphabetical 순서 `(a),(b),...,(h),(i),(j),...` 와 sub-sub 의 Roman 순서
`(i),(ii),(iii)` 가 동일 토큰 `(i)` 로 표기되어 resolver 가 두 의미를
구분하지 못한다. `(i)` 정의 인용이 필요하면 직접 concrete chunk_id (`200:00065:(i)`
형식) 로 지정한다.

### Evidence — ISA 200 ¶13 아래 `(i)` 토큰 3개 공존

```jsonl
# (1) Roman (i) — sub-sub of (h) 재무보고체계 항목
chunk_id="200:00053:(i)"  section=definitions  block_ordinal=53
heading_trail=["...", "용어의 정의"]
paragraph_ids=["(i)"]
text="(i) 재무제표의 공정한 표시를 달성하기 위하여 경영진이 해당 체계가
      특정하여 요구하는 범위 이상으로 공시하는 것이 필요할 수 있다고
      명시적이거나 묵시적으로 인정함."

# (2) Alphabetical (i) — 왜곡표시 정의 (intended in many queries)
chunk_id="200:00065:(i)"  section=definitions  block_ordinal=65
heading_trail=["...", "용어의 정의"]
paragraph_ids=["(i)"]
text="(i) 왜곡표시 – 재무제표에 보고된 금액, 분류, 공시 또는 표시와
      해당 재무보고체계의 요구에 따른 금액, 분류, 공시 또는 표시와의 차이.
      왜곡표시는 오류 또는 부정으로 발생될 수 있다. ..."

# (3) Alphabetical (i) — 적용지침 윤리적 요구사항 sub-list
chunk_id="200:00168:(i)"  section=application  block_ordinal=168
heading_trail=["...", "적용 및 기타 설명자료", "재무제표감사와 관련된
                윤리적 요구사항(문단 14 참조)"]
paragraph_ids=["(i)"]
text="(i) 비밀유지"
```

### Resolver 실측 (eval.py:30 정규식)

```python
_LOGICAL_PATH = re.compile(r"^(?P<isa>[^:]+):(?P<parent>\d+[A-Za-z]?)\.\((?P<sub>[a-z])\)$")
```

`sub` 그룹이 `[a-z]` single character 만 받아들여 Roman `i` 와 alphabetical `i` 가
동일 토큰. `200:13.(i)` resolve 결과:

- parent = `200:00050:13` (block_ordinal=50, section=definitions)
- Pass 1 first match: section==definitions 인 첫 `(i)` → **`200:00053:(i)`** (Roman, "공정한 표시 인정")
- intended 인 alphabetical `(i)` 왜곡표시 (`200:00065:(i)`) 는 누락.

→ `200:13.(i)` 는 의도와 다른 청크를 회수. Q24 v2 evidence 에서 명시적으로
related 제외 사유로 기록됨 (queries.yaml:452-456).

### 회피 방법

| 잘못된 패턴 | 권고 대체 |
|---|---|
| `expected_primary_chunks: ["200:13.(i)"]` | `expected_primary_chunks: ["200:00065:(i)"]` (concrete) |
| (또는 영향 쿼리 자체 회피) | "왜곡표시 정의" 쿼리는 P3 def 5개 후보에서 제외, 다른 정의 쿼리로 대체 |

### 다른 ISA 의 동일 위험

ISA 240 / 315 / 500 / 700 의 ¶12~¶13 정의 단락에도 `(i)` 토큰 충돌 가능. P3
def 5 oracle 작성 시 해당 ISA 의 `(i)` 사용 전 직접 chunks.jsonl 에서 토큰
중복 횟수 grep 으로 확인.

`docs/eval/phase3_failure_analysis.md` §9 P5 가 resolver 확장으로 alphabetical/
Roman 구분 가능하게 만드는 후속 항목으로 등록됨 (P0 scope 밖).

---

## DR-4 — Query phrasing 과 primary framing 일치

### 규칙

쿼리의 자연어 표현이 primary chunk 의 본문 framing 과 동일 어휘 축에 있어야
한다. 쿼리 의도 ↔ chunk 본문 의도 사이에 framing gap 이 있으면 모델이 더
적합한 다른 청크를 top-5 에 올려 gold 가 인공 실패한다. evidence block
작성 시 쿼리 단어와 primary 본문의 핵심 단어를 ≥ 2개 일치시키고, gap 이
있다면 gap 내용 + 정당화 근거를 notes 에 기록한다.

### Evidence — Phase 3 §5.3 / §8.5 deferred 3건

#### Q11 (gold 와 쿼리 framing 어긋남)

```yaml
query: "고유위험과 통제위험의 범위를 평가할 때 고려할 상황은?"
primary: ["315:A7", "315:A8"]  # 본문은 "고유위험요소" 정의 확장 (개념 분류)
```

phase3_failure_analysis.md §5.3:
> gold = 고유위험요소 정의 확장. 쿼리 = "고유위험·통제위험 범위 상황"
> → "통제위험" 차원 미포함. 모델은 `315:29` (고유위험 평가) / `315:A129`
> 를 top-3 로 더 적합 판단. 실측 BGE/UPS recall@5 = 0.0.

쿼리 framing ("범위 평가 상황") vs primary framing ("고유위험요소 정의 확장")
사이에 통제위험 축 누락 + 평가/분류 동사 차이 = framing gap. 모델 retrieval
은 정직했으나 gold 가 인공 실패.

#### Q18 (cross-link framing 약함)

```yaml
query: "부정 위험을 평가할 때 내부통제 이해는 어떻게 연계되는가?"
primary: ["240:26", "315:14"]  # 식별/평가 요구사항 본문 — "부정 × 내부통제 연계" 명시 약함
```

§5.3:
> 모델은 `240:A13` (경영진질문-부정) + `315:A95` (내부통제 이해 적용지침) 을
> 더 정면 매치로 판단. 실측 recall@5 = 0.0.

primary 본문이 "부정 RMM 식별 절차" / "위험평가 일반" 으로, 쿼리의 "연계"
프레임을 직접 답하지 않음.

### 검증 절차 (NIT-N4 반영, DA 서명 조건)

DR-4 의 "framing 일치" 판정은 평가자 재량 변동을 줄이기 위해 다음 수치
기준으로 정량화한다. evidence block 의 DR-4 mini-table 은 **각 primary
chunk 마다 1행** 으로 작성한다.

#### 토큰화 정책 (Phase 5 S3 와 완전 동일)

1. **분할**: 공백 단위 split (한국어는 형태소 분석 미적용 — 표면형 매칭
   단순화).
2. **lowercase**: 영문 / 숫자만 lowercase 적용 (한국어는 변환 없음).
3. **Stopword 제거** (고정 리스트, P5 `scripts/retrofit_audit.py` 와 공유):

   ```text
   STOPWORDS = {"의", "은", "는", "이", "가", "에", "와", "과", "을", "를",
                "수", "등", "및", "한", "한다", "있다", "하는"}
   ```

4. **빈도 상위 20 토큰** 을 primary 본문에서 추출 (chunk 의 `text` 필드
   기준, heading_trail prefix 포함). 동률 시 출현 순서로 자른다.

#### 판정 기준

각 primary 의 mini-table 1행은 다음 컬럼 (표면형 surface match):

```text
| primary chunk_id | query 토큰 (공백 split, stopword 후) | primary top-20 토큰 | 교집합 (strict surface) | 일치 (≥ 2) |
| 500:04351:6      | ["감사인은","충분하고","적합한","감사증거를","어떻게","입수하는가?"] | ["적합한","감사증거","충분하고","감사인은","감사증거를",...] | {감사인은, 충분하고, 적합한, 감사증거를} = 4 | ✓ |
```

- **교집합 ≥ 2**: ✓ DR-4 통과
- **교집합 < 2**: ✗ 다음 중 하나로 처리:
  - (a) 쿼리 narrowing — primary 본문 토큰을 쿼리에 포함시켜 재작성
  - (b) primary 교체 — 교집합 ≥ 2 가 자연스럽게 형성되는 chunk 로 변경
  - (c) intentional gap (cross-standard 의 DR-5 우선 trade-off 등) — notes
    에 정당화 사유 명시

cross-standard 에서 (c) 가 누적 (총 primary 의 30% 초과) 되면 lead 보고.
정량 임계는 Phase 5 S3 audit 가 retrofit 신호로 재측정.

#### Worked example (N1 candidate)

쿼리 후보: "감사인은 충분하고 적합한 감사증거를 어떻게 입수하는가?"
primary `500:04351:6` 본문 (heading_trail prefix 포함):
"감사기준서 500  감사증거 > 요구사항 > 충분하고 적합한 감사증거\n\n
6. 감사인은 충분하고 적합한 감사증거를 입수하기 위하여 상황에 적합한
감사절차를 설계하고 수행하여야 한다. (문단 A5-A29 참조)"

```text
공백 split → query 토큰 (6개):
  ["감사인은", "충분하고", "적합한", "감사증거를", "어떻게", "입수하는가?"]
stopword 제거 (해당 없음 — 모두 agglutinated surface form): 6 토큰 유지

primary 본문 빈도 top-20 (공백 split, 동률 시 출현순 절단):
  ["적합한"(3), ">"(2), "감사증거"(2), "충분하고"(2), "감사기준서", "500",
   "요구사항", "감사증거를", "6.", "감사인은", "입수하기", "위하여", "상황에",
   "감사절차를", "설계하고", "수행하여야", "한다.", "(문단", "A5-A29", "참조)"]

교집합 (strict surface-form):
  {"감사인은", "충분하고", "적합한", "감사증거를"} = 4
판정: ✓ (≥ 2)
```

**주의 — Korean 표면형 한계**: "감사증거" vs "감사증거를" 처럼 조사 부착으로
표면형이 다르면 별개 토큰 (형태소 분석 미적용). 의미적으로 일치하나 표면형
불일치 가능. ≥ 2 임계가 보수적인 이유 (false match 방지) 이며, 실패 시
(a) 쿼리 phrasing 을 primary 표면형에 맞춰 narrowing 하는 것이 first-line
조정. P5 S3 audit 도 동일 표면형 매칭이므로 사전·사후 정합.

cross-standard 에서 framing gap 동반 stub 은 누적되면 실측 0.0 (Q11/Q18
패턴) — DR-4 위반은 (c) intentional 케이스 외에는 무조건 lead 보고.

### v2 self-evaluation (Q15 vs Q14)

Q15 ("전문가적 의구심의 개념과 부정위험에의 적용") 는 primary `200:15` (요구사항)
+ `240:13` (부정맥락 적용 요구사항) — 쿼리 "개념과 적용" 이 두 ISA 의 동사
("적용한다") 와 정합. UPS 0.5, BGE 0.0 (BGE 는 §3.2 bucket C 임베딩 커버리지
문제).

Q14 ("RMM 의 의미와 감사절차에서의 역할") 는 primary `200:13.(n)` (정의) +
`315:23` (식별) + `330:5` (대응). 쿼리 "역할" 이 절차 어휘로 분산되어 §5.7
에서 BGE 가 절차 청크로 흩어짐. **DR-4 관점에서 Q14 는 잠재적 framing
weakness**. cross-standard 에서는 framing 보다 ISA 분포 확장 우선시 → DR-5 와
trade-off.

---

## DR-5 — Cross-standard 는 최소 2개 ISA primary + 쿼리 간 disjoint

### 규칙

**(a) 다중 ISA 강제**: `category: cross-standard` 쿼리의
`expected_primary_chunks` 는 **서로 다른 ISA 번호** 를 가진 chunk 가 최소
2개 포함되어야 한다. 단일 ISA 만 primary 인 경우 cross-standard 라벨 부적격
(definitions / requirements / application 중 적합한 카테고리로 재분류).

**(b) 쿼리 간 primary disjoint 강제 (NIT-N6, 2026-04-19 추가)**:
Cross-standard 쿼리의 primary chunk_ids 집합은 다른 cross-standard 쿼리의
primary 집합과 **disjoint** 여야 한다. 즉 임의의 쿼리 i, j (i ≠ j, 둘 다
`category=cross-standard`) 에 대해 `primary(i) ∩ primary(j) = ∅`. 동일
`chunk_id` 또는 동일 `logical_path` 모두 공유 금지. 두 쿼리에 모두 적합한
chunk 는 한 쿼리에만 primary 로 남기고 다른 쿼리는 (i) `expected_related_chunks`
로 강등 또는 (ii) 대체 chunk 를 선택한다.

이유:
- 동일 chunk 가 두 쿼리에서 gold 로 등장하면 Phase 5 S4 (oracle 겹침) 측정
  시 이중 계상 → 임계 30% 가 인공적으로 충족되어 retrofit 신호 의미 소실.
- 평가 샘플의 정보량 중복: 쿼리 framing 이 다르더라도 gold 가 같으면 측정
  효율 저하.

예외 — application-guidance vs requirements 처럼 같은 ¶ 의 다른 측면은
chunker 가 별도 chunk_id 로 이미 분리하므로 자연 disjoint. 실무에서 겹칠
때는 framing 설계 실수 또는 plan §4.2 같은 사전 후보표의 우연적 중복.

**v2 Q14~Q19 에는 소급 적용하지 않음** (append-only 정책, plan §6).
DA 가 v2 6건 cross 의 primary 간 chunk_id 중복을 재검토했으며 0건 확인됨
(v1 `200:13` 공유는 v2 의 서브 분해로 해소).

**(c) primary 섹션 제약 (Option D, 2026-04-19 추가)**:
Cross-standard 쿼리의 `expected_primary_chunks` 는 `section ∈ {requirements,
application, definitions}` 에서 선정한다. `section=objective` 는 primary 로
채택하지 않는다. application / definitions 은 DR-1 cc 기준 (> 115) + stub
금지 + axis-specific framing 조건을 모두 충족해야 한다.

<!-- Option D pilot precedent: 315:11 Option C fail (2026-04-19).
     Option C (cc ≥ 180) 시도 후 cc=163 + generic objective framing 이중
     fail → section=objective 제외로 단순화. -->

이유:
- `objective` = ISA 전체 목적의 meta-declaration — 특정 axis 의 primary
  evidence 로서 권위 구조적 약화 (generic framing → axis-specific retrieval
  평가 부적합).
- `requirements` = 강행규정 (primary 표준).
- `application` = 적용지침 (primary 보조, axis framing 구체 시).
- `definitions` = 용어정의 (stub filter 하 primary 가능).

**예외**: axis framing 이 ISA 간 의존·프레임워크 참조 구조 자체를 요구하는
경우 (드문 케이스), objective section 이 structural primary 로 자격 있는지
lead 재심의 (P0 scope 외 — 적용 사례 없음 시 P4 이후 재검토).

적용 범위: v3 신규 Q27~ 부터 적용 (v2 Q01~Q26 소급 미적용, append-only 정책).

**N3 적용 precedent**: N3 (Q29) 초안에서 `315:02409:11` (§11, section=objective,
cc=163) 가 후보로 등장했으나, (1) Option C (cc ≥ 180) 적용 시 cc 기준 fail,
(2) 본문이 ISA 315 전체 objective 의 generic 선언 → axis-specific framing
부재 이중 fail. → `315:02485:23` (§23, section=requirements, cc=165, RMM
식별 framework) 로 swap. Option D 하에 primary 적격성 확보.

검증: P4 merge 시점에 cross-standard 카테고리 전체 primary 집합을 수집하여
UNIQUE 제약 + objective 제외를 확인 (`assert len(set(all_cross_primaries)) ==
sum(len(q.primary) for q in cross_queries)` +
`assert all(c.section != 'objective' for c in all_cross_primaries)`).

### 근거

cross-standard 카테고리의 정의 자체 (queries.yaml:241 코멘트):
> "복수 ISA 에 걸친 개념"

phase3_failure_analysis.md §4.1 / §4.3 에서 단일-ISA 포화 (single-ISA
saturation) 가 cross-standard 의 구조적 실패 모드로 식별됨:

> Q19 의 단일-ISA 포화는 BGE ON 에서만 발생 (540×9). prefix 가 "540" 토큰을
> 각 청크 앞에 삽입해 자기강화. UPS 는 분포 정상.

primary 가 단일 ISA 면 모델 retrieval 이 자연스럽게 같은 ISA 청크로 포화 →
cross-link 신호 측정 불가. 2+ ISA primary 가 강제되어야 prefix 효과 / cross-
link rerank 효과의 분리 측정이 가능.

### Evidence — v2 cross-standard 6건의 ISA 분포 + disjoint 검증

```text
| QID | primary ISAs | 2+ ISA? | primary chunk_ids (요약) | 다른 cross 와 공유? |
| Q14 | 200, 315, 330 | ✓ | 200:13.(n), 315:23, 330:5 | ✗ disjoint |
| Q15 | 200, 240      | ✓ | 200:15, 240:13            | ✗ disjoint |
| Q16 | 200 only (.(c)/(e)/(n) 3 sub) | ✗ — 단일 ISA, **재분류 검토 권고** | 200:13.(c)/(e)/(n) | ✗ disjoint |
| Q17 | 315, 330      | ✓ | 315:27, 330:21            | ✗ disjoint |
| Q18 | 240, 315      | ✓ | 240:26, 315:14            | ✗ disjoint |
| Q19 | 540, 240      | ✓ | 540:32, 240:32            | ✗ disjoint |
```

→ **NIT-N6 disjoint 소급 검증 (DA, 2026-04-19)**: v2 6건의 primary chunk_id
union 카운트 = 13개, 모두 unique. v1 의 `200:13` 단일 공유는 v2 서브 분해
(`.(c)/(e)/(n)`) 로 자연 해소. v2 append-only 정책으로 v2 자체 수정 불필요.

→ Q16 은 **(a) 다중 ISA** 기준으로는 단일 ISA 라 재분류 후보. 단 append-
only 정책 (plan §6) 으로 P0 scope 밖. P3 def 5 작성 시 Q16 류 단일-ISA
정의는 def 카테고리로 신규 oracle 작성하는 방향으로 학습 적용.

### 적용 절차 (P2 N1~N9 신규)

plan §4.2 의 N1~N9 후보 9건은 모두 ≥ 2 ISA 명시되어 있어 본 DR 충족 가능.
oracle 작성 시 각 evidence block 에 다음 mini-table 추가:

```text
| primary chunk_id | isa_no | section       |
| 500:6            | 500    | requirements  |
| 330:7            | 330    | requirements  |
| 450:8            | 450    | application   |
→ unique ISAs = {500, 330, 450} = 3 개 ✓ DR-5(a) 통과
→ objective 제외 ✓ DR-5(c) 통과
```

unique ISAs ≥ 2 가 아닐 경우 oracle 후보 변경 또는 카테고리 재분류.
primary 중 section=objective 가 1건이라도 있으면 DR-5(c) 위반 — 즉시 같은
ISA 의 requirements / application / definitions 중 axis 정합 chunk 로 교체.

### DR-4 와의 trade-off

Q14 케이스에서 보듯 cross-standard 의 다중 ISA 강제 (DR-5) 는 쿼리 어휘를
정의·요구사항·적용지침에 걸쳐 만들어야 하므로 framing 자연스러움 (DR-4) 와
긴장. 권고 우선순위:

1. DR-5 (≥ 2 ISA) 강제 — cross-standard 정의상 양보 불가
2. DR-4 framing — 쿼리 phrasing 을 ISA 별 본문 어휘 OR 합집합으로 구성
3. framing gap 잔존 시 notes 에 명시 + retrofit 신호 모니터링 (Phase 5
   S3/S4 audit 의 입력)

---

## 5 DR 체크리스트 (P2/P3 신규 24 쿼리 evidence block 마지막에 첨부)

신규 oracle 1건 = 1개 체크리스트. ✓ 5 / 5 가 아니면 lead/DA 보고 후 채택
재검토.

```text
[ ] DR-1 — Intro-parent stub 없음
    근거: 모든 primary char_count > 115 (NIT-N1 임계 상향) OR 본문이
          "...는 다음과 같다." 패턴 아님 + paragraph_ids 단일 숫자 아님
[ ] DR-2 — Resolver 매핑 로그 첨부
    근거: logical_path 사용 시 mini-table (concrete_chunk_id, parent_section, block_ordinal)
[ ] DR-3 — `{isa}:{N}.(i)` 패턴 미사용
    근거: 모든 logical path 의 sub 가 `(i)` 가 아님; (i) 인용 시 concrete chunk_id
[ ] DR-4 — Query phrasing 과 primary framing 일치
    근거: 동사·명사 일치 mini-table; gap 있으면 notes 정당화
[ ] DR-5(a) (cross 카테고리만) — primary ISA 수 ≥ 2
    근거: unique ISAs mini-table; req/app/def 카테고리는 N/A 로 표기
[ ] DR-5(b) (cross 카테고리만) — 다른 cross 쿼리와 primary chunk_id disjoint
    근거: NIT-N6 (2026-04-19). evidence block 작성 후 cross 카테고리 전체
          primary 합집합 수동 차집합 확인. P4 merge 시 자동 UNIQUE 검증.
[ ] DR-5(c) (cross 카테고리만) — primary section ∈ {requirements, application, definitions}
    근거: NIT-N7 Option D (2026-04-19). section mini-table 에 objective 0건
          확인. v3 신규 Q27~ 적용, v2 Q01~Q26 소급 미적용.
```

체크리스트 위반 시 처리:

- DR-1 위반: stub primary 를 sub-item 으로 교체, 또는 다른 numbered paragraph 로 교체.
- DR-2 위반: logical path 를 concrete chunk_id 로 교체.
- DR-3 위반: 무조건 회피 — `(i)` 인용 자체를 다른 sub 로 우회.
- DR-4 위반: 쿼리 narrowing 또는 primary 교체. 잔존 시 lead 보고.
- DR-5(a) 위반: cross 카테고리 라벨 부적격 — 다른 카테고리로 재분류 또는
  oracle 교체.
- DR-5(b) 위반: 두 쿼리 중 하나의 공유 chunk 를 related 로 강등 또는 대체
  chunk 선택. P2 plan §4.2 의 사전 후보표에서 우연 중복 발견 시 동일 처리
  (예: N7 ∩ N9 = `240:22` → N9 의 `240:22` 를 `240:24` 로 교체).
- DR-5(c) 위반: primary 중 section=objective 발견 시 같은 ISA 의
  requirements / application / definitions 중 axis 정합 chunk 로 교체
  (DR-1 cc > 115 + stub 금지 + axis-specific framing 재검증 필수).
  예외 조건 (ISA 간 의존·프레임워크 참조 structural framing) 해당 시 lead
  재심의. 예: N3 `315:02409:11` → `315:02485:23` swap (2026-04-19).

---

## 서명

### Audit-Domain-Expert (DE)

- **이름**: audit-domain-expert
- **서명일**: 2026-04-19
- **서명 진술**:
  본 5 DR 은 phase3_failure_analysis.md §5 (gold 수정 5건) 와 §8.5 (deferred
  3건) 의 실패 원인을 chunks.jsonl 원문 evidence 와 함께 추출했음. P2/P3 신규
  24 쿼리에 본 체크리스트가 모두 ✓ 인지 evidence block 자체에서 검증할 수
  있도록 mini-table 포맷을 명시했음. v2 §5.3 deferred 3건 (Q11/Q18/Q19) 은 본
  DR 적용 대상이 아니며 (Phase 4 P3 워크숍 deferred), v2 Q01–Q26 에 대한
  소급 적용도 하지 않음 (append-only 정책).

### Devils-Advocate (DA)

- **이름**: devils-advocate
- **서명일**: 2026-04-19
- **판정**: **조건부 서명 (NIT 5건, blocking 0건; N4 만 DR-4 문단 보강 후 최종 서명 유지)**
- **서명 진술**:
  DE 요청 5 검토 항목 및 plan §4.2 N1~N9 (i) prescreen 완료. 5 DR 은 Phase 5
  S3/S4 retrofit audit 의 **사전 방어선** 으로 기능하며, DR 위반 = 해당 signal
  trip 으로 이중 연동됨을 §Phase 5 관계 항에서 확인. DR-1/2/3/5 는 cleanly
  승인. DR-4 는 객관성 강화 (N4) 를 DR-4 규칙 문단에 반영하는 조건으로 승인.

#### DA 검토 결과 (DE 요청 5항목)

**1) DR-1 false-positive 리스크 — 낮음**. anchor `^…$` 엄격 매칭으로 stub
외 청크 매치 불가. fallback `^.{0,15}는 다음과 같다\.?$` 도 sub-item 이어
지는 정상 청크는 $ anchor 로 회피됨. char_count ≤ 90 보조 신호도 heading
prefix 포함 기준 안전.
- **NIT-N1 (advisory)**: fallback 15자 상한이 긴 변형 intro (예: "부정과
  관련된 위험요소는 다음과 같다" 류, ≈17~19자) 를 놓칠 수 있음. P2/P3
  진행 중 chunks.jsonl 에서 `"는 다음과 같다"` grep 결과 전수 확인 후
  필요 시 20~25자로 확장. 본 NIT 는 착수 차단 아님.

**2) DR-2 mini-table 운용 가능성 — 양호**. resolver 호출 결과 복사로 작성 가능.
- **NIT-N2 (advisory)**: 현 포맷이 Pass 1 vs Pass 2 fallback 을 구분하지
  않음. DR-1 차단으로 stub parent 배제되면 대부분 Pass 1 이지만, Pass 2
  fallback 발동 케이스는 evidence 신뢰도가 한 단계 낮음. Mini-table 에
  `resolver_pass` 컬럼 (`1`/`2`) 추가 권고. 본 NIT 는 착수 차단 아님.

**3) DR-3 회피 절차의 retrofit 리스크 — 낮음**. concrete chunk_id
(`200:00065:(i)`) 지정은 resolver 버그 우회이지 측정 인플레이션 아님. 해당
chunk 가 Phase 3 v2 top-5 에 등장했다면 S4 임계 30% 에 집계되어 retrofit
탐지 — 이중 방어.
- **NIT-N3 (advisory)**: DR-3 본문이 "concrete chunk_id 우회" 와 "쿼리
  자체 회피" 를 병기하는데 우선순위 불분명. 권고 순서: **(a) concrete
  chunk_id 우선, (b) 완전 회피는 (i) 토큰 3+ 공존 ISA (현재 200, 여타
  240/315/500/700 으로 P3 진입 전 grep 확인) 에서만**. DR-3 규칙 문단
  말미에 명시.

**4) DR-4 framing 판정 객관성 — 5 DR 중 가장 약함**. "핵심 동사·명사" 선택과
"일치" 판정이 평가자마다 변동. Q11/Q18 형태의 미세한 framing gap 은 수작업
mini-table 로 재현성 떨어짐.
- **NIT-N4 (서명 조건, 착수 차단 요소)**: P2/P3 evidence block 의 DR-4
  mini-table 에 다음 수치 기준 강제:
  - 쿼리 토큰 ∩ primary 본문 핵심 토큰 (각 primary 당 상위 20 빈도어)
    **≥ 2** (stopword 제거 후 표면형 일치)
  - 토큰화 정책: 공백 split + 공용 stopword 리스트
    `{의, 은, 는, 이, 가, 에, 와, 과, 을, 를, 수, 등, 및, 한, 한다, 있다, 하는}`
    + 영문/숫자 lowercase (DA 의 P5 S3 tokenization 과 **완전 동일**)
  - 교집합 < 2 인 경우 notes 에 framing gap + intentional choice
    (cross-standard 의 DR-5 우선 trade-off 등) 정당화
  이로써 DR-4 판정이 정량화되고 Phase 5 S3 prescreen 과 tokenization 공유.
  DR-4 문단에 이 수치 기준이 반영된 `query_design_rules.md v2` 가
  P2 착수 전 커밋되어야 본 DA 서명 유효.

**5) DR-5 Q16 소급 비적용 — 명확**. §DR-5 Evidence 의 "v2 append-only 정책으로
P0 scope 밖" 문구가 plan §6 과 정렬.
- **NIT-N5 (advisory)**: "학습 적용은 P3 신규에만" 이 P3 def 5 에 Q16 스타일
  (ISA 200 단일 정의) 유사 oracle 을 허용할 여지가 있음. 권고: **P3 def 5
  중 Q16 과 의미론적으로 유사한 oracle 은 최대 1개** (자연어 토큰 기준
  Jaccard ≥ 0.3 은 P5 S3 에서 정량 검증). 본 NIT 는 착수 차단 아님.

#### Plan §4.2 N1~N9 prescreen (DR-3 관점 + 부수 발견)

- **DR-3 pass**: N1~N9 primary 총 25 chunk 모두 `{isa}:{N}` 또는 `{isa}:{N}.(x≠i)`
  형태, `(i)` sub 인용 0건. DE 의 "외관상 안전" 주장 확인.
- **부수 발견 → NIT-N6 조항화 (phantom motivating example, DE 정정 2026-04-19)**:
  DA 초기 읽기에서 N7 (`250:22`, `240:22`) 과 N9 (`550:18`, `240:22`) 가 동일
  chunk `240:22` 를 primary 로 공유한다고 판단하여 lead 권고로 NIT-N6 차단
  요소 등재. 그러나 DE 가 P2 entry 첫 작업으로 plan §4.2 원본 + chunks.jsonl
  실측 재검증한 결과 N9 후보는 **`240:24`** (`240:01102:24`) 이고 N7 의
  `240:22` 는 `240:01098:22` 로 **서로 다른 chunk_id** → overlap **phantom
  확정** (DA misread, 숫자 근접성 혼동). plan §4.2 원본 N7/N9 후보는 그대로
  유효 (교체 작업 불필요).
  **그러나 NIT-N6 규칙 조항화 자체는 유지** — prophylactic design rule 로서
  (i) 미래 cross 쿼리 누적 시 dual-counting 구조적 차단, (ii) v1 Q14·Q16
  `200:13` 공유라는 **real precedent** (phase3 §5.2) 존재가 motivating
  example 의 phantom 여부와 무관하게 조항화 정당성 부여. 즉 "N7/N9" 인용은
  phantom 으로 정정하되, DR-5(b) 자체는 v1 precedent 에 기반해 유효.

#### NIT-N6 (신규, 서명 조건 추가 차단 요소) — DR-5 cross 축 간 primary 중복 금지

- **근거**:
  - **S4 이중 계산 위험 (일반 구조)**: 임의 cross 쿼리 간 공유 chunk 가 Phase 3
    v2 top-5 union (BGE-ON ∪ UPS-ON) 에 포함되면 두 쿼리 모두 trip → 한
    chunk 가 2 건 count, 30% 임계가 인공 팽창하여 DA 측정 편향. (DA 초기
    motivating example 로 `240:22` 공유를 인용했으나 실측 phantom — §Plan
    §4.2 prescreen 주석 참조. 그러나 구조적 risk 는 예시 존부와 무관.)
  - **평가 샘플 정보량 중복**: 쿼리 framing 이 다르면서 gold chunk 가 같은
    경우, n=50 중 유효 독립 샘플 수가 실제로 49 로 감소. CI 폭 개선
    효과 (P0 본 목적) 를 스스로 감소시키는 모순.
  - **v1 real precedent (motivating example)**: v1 Q14·Q16 이 모두 `200:13`
    stub 을 primary 로 공유했다가 v2 에서 각각 서브 `(c)/(e)/(n)` 로 분해
    되어 chunk 공유 해소된 바 있음 (phase3_failure_analysis §5.2). Chunk
    공유 = retrofit risk 의 **실제 기존 전례** (phantom 아님). 본 전례가
    NIT-N6 조항화 정당성의 주 근거.
- **규칙 제안 (DR-5 §규칙 말미에 추가)**:
  > `category: cross-standard` 쿼리 간에 `expected_primary_chunks` 에 동일
  > `chunk_id` 또는 동일 `logical_path` 를 공유할 수 없다. 두 cross 쿼리에
  > 모두 적합한 chunk 는 하나의 쿼리에만 primary 로 남기고 다른 쿼리에는
  > `expected_related_chunks` 로 강등하거나 대체 chunk 를 선택한다. v2
  > Q14~Q19 에는 소급 적용하지 않음 (append-only 정책).
- **P2 구체 조치 (phantom 확정 후 정정, 2026-04-19)**:
  - N7/N9 overlap 은 **phantom 확정** (DE 실측: N7 `240:22` = `240:01098:22`,
    N9 `240:24` = `240:01102:24`, 서로 다른 chunk_id). plan §4.2 원본
    N7=(250:22, 240:22), N9=(550:18, **240:24**) 유지, 교체 작업 불필요.
  - DR-5(b) 조항은 P2/P3 전체 cross oracle 작성 시 primary chunk_id
    수동 차집합 검증으로 운용 (체크리스트 DR-5(b) 항목). P4 merge 시 자동
    UNIQUE 검증으로 이중 방어.
- **v2 Q14~Q19 재검증 (소급 미적용 확인)**: 본 DA 가 append-only 범위 내 v2
  cross 6 건 간 chunk 공유 재검토 — Q14~Q19 각 primary 간 chunk_id 중복
  **없음 확인** (v1 Q14·Q16 `200:13` 공유는 v2 서브 분해로 해소). 따라서
  소급 rework 불필요.

#### 서명 조건 (요약, 업데이트)

- **차단 요소 (2건, P2 착수 전 필수 커밋)**:
  - **NIT-N4**: DR-4 수치 기준 (token intersection ≥ 2, stopword 공유)
  - **NIT-N6**: DR-5 cross 축 primary chunk_id 중복 금지 조항 반영 (motivating
    example 로 인용했던 N7/N9 `240:22` 공유는 DE 실측 결과 phantom —
    정정 주석 상단 참조. 조항 자체는 v1 Q14·Q16 `200:13` real precedent 에
    기반해 유효.)
- **Advisory (P2/P3 진행 중 반영)**:
  - **NIT-N1 업데이트**: DR-1 §판정 기준 2번 char_count 임계 **90 → 115**
    (`parsed/chunks.jsonl` 전수 스캔 근거: `402:03988:7` cc=110,
    `220:00726:A4` cc=114 경계 케이스 안전 커버). regex fallback 은 현상
    유지 — paragraph_ids 단일 숫자 필터가 실질 핵심 방어선, FP 0건 확인.
  - **NIT-N2** (`resolver_pass` 컬럼 추가)
  - **NIT-N3** (DR-3 우선순위: concrete chunk_id 우선)
  - **NIT-N5** (P3 def 5 중 Q16 유사 oracle 최대 1개)
  - **NIT-N7 (2026-04-19 추가, DA 4th Edit 반영 완료)**: DR-5(c) primary
    section 제약 (Option D) — `section=objective` 제외, requirements /
    application / definitions 허용. application / definitions 은 DR-1
    cc > 115 + stub 금지 + axis-specific framing 전제. 예외: ISA 간
    의존·프레임워크 참조 structural framing 시 lead 재심의 (P0 scope 외).
    v3 신규 Q27~ 적용, v2 Q01~Q26 소급 미적용 (append-only). Lead 승인
    2026-04-19, DA 재확인 ✓. N3 (Q29) `315:02409:11` → `315:02485:23`
    swap 이 첫 적용 precedent.
- **Phase 5 연계**:
  - N4 stopword 리스트 = P5 `scripts/retrofit_audit.py` 와 완전 동일.
  - N6 신설 조항 위반 여부는 P5 S4 측정 전에 queries.yaml v3 전수 sanity
    check 로 이중 검증 (DA 소관, 추가 비용 ≤ 10 분).
  - N7 section 제약 위반 여부는 P4 merge 시 automated assert 로 이중
    검증 (`assert all(c.section != 'objective' for c in all_cross_primaries)`).

N4 + N6 + N7 반영 커밋 확인 후 본 서명 유지. 셋 중 하나 미반영 시 재검토.

---

## Phase 5 retrofit audit 와의 관계

본 DR 은 Phase 5 (DA 4-signal audit, plan §7 Phase 5) 의 **사전 검증** 역할.
- DR-1/DR-3 위반 = retrofit 의 S3 (실패 쿼리 bias) 에 직접 영향.
- DR-4 위반 = S2 (one-way movement) 의 잠재 신호.
- DR-5 위반 = cross-standard 카테고리 신뢰성 자체의 문제.

Phase 5 가 본 DR 위반을 정량 측정하지만, P2/P3 단계에서 DR 체크리스트로
사전 차단하는 것이 retrofit 비용 절감에 우선.
