# 검색 평가 하네스 설계 (KICPA 감사기준 pgvector)

> 담당: `audit-domain-expert` (Task #3, Phase 2d)
> 산출물: 이 디렉터리(`docs/eval/`) — 쿼리 세트 + 메트릭 설계. 코드 구현은 리더 소유.

---

## 1. 목적

`parsed/chunks.jsonl` (4526 chunks) → pgvector 임베딩 인덱스가 실제 감사 실무자의
질의에 얼마나 잘 답하는지를 정량 측정하기 위한 **소규모·라벨 기반 평가 세트**
를 설계한다. 대용량 자동생성(LLM-as-judge) 대신, 실무 패턴을 직접 큐레이션한
**26건**의 golden query 로 A/B 판단 신호를 확보한다.

---

## 2. 쿼리 구조 (`queries.yaml`)

| 필드 | 의미 |
|---|---|
| `id` | `Q01`~`Q26` 고유 식별자 |
| `category` | `requirements` / `application` / `cross-standard` / `definitions` |
| `query` | 실제 감사인이 입력할 법한 자연어 질문(한국어) |
| `expected_primary_chunks` | top-1/top-3 에 반드시 포함되어야 하는 정답 chunk_id 리스트 |
| `expected_related_chunks` | top-10 포함 시 보조 점수. 누락해도 recall 감점 없음 |
| `notes` | 라벨링 근거, 엣지케이스, A/B 테스트 민감도 메모 |

### 카테고리별 건수

| 카테고리 | 건수 | 대표 질의 |
|---|---:|---|
| requirements | 7 | "RMM 식별·평가 절차?", "계약서 포함사항?" |
| application | 6 | "계약서 작성 시 고려사항(적용지침)?" |
| cross-standard | 6 | "RMM: 정의(200) → 평가(315) → 대응(330)" |
| definitions | 7 | "감사위험이란?", "유의적 위험의 정의?" |
| **합계** | **26** | |

---

## 3. `chunk_id` 해석 규약 ★ 중요

### 3.1 문제 (Phase 2d self-audit 실측 반영 — 2026-04-19)

`src/audit_parser/chunk.py::_chunk_id` 의 포맷은 `{isa_no}:{paragraph_id}` 이다.
최상위 숫자 문단(예: `200:13`)은 ISA 안에서 유일하지만, 서브아이템
(`(a)`, `(b)`, `(i)` …)은 **같은 ISA 내에서 반복 등장**한다.

**실측 중복 규모 (parsed/chunks.jsonl 4526 rows)**:
- Unique chunk_ids: **3170**
- Duplicate chunk_ids: **344** (중복 발생 ID 수)
- Row-level loss risk: **1356 rows** (DB PK 가 chunk_id 단일이라면 upsert last-write-wins 로 사라짐)
- 최악: `?:(a)` x96, `?:(b)` x95, `700:(b)` x20, `540:(a)` x17, `610:(a)` x15 …

**정의 영역의 실제 오염 사례 (ISA 200 ¶13)**:
- `200:(c)` 는 chunks.jsonl 에 **2회** 저장되어 있음:
  1. heading_trail=`용어의 정의` → `(c) 감사위험 – 재무제표가 중요하게 왜곡표시되어…` ← **정답**
  2. heading_trail=`적용지침 > 재무제표감사 > 재무제표의 작성` → `(c) 감사인에게 다음 사항들을 제공할 책임…`
- `200:(e)` 도 동일 구조. `(e) 적발위험 – 감사위험을 수용가능한…` (정답) vs `(e) 발생할 경우 중요하다(즉, 규모)` (중요왜곡표시위험 설명의 서브아이템)
- 정의 ¶13 의 (a)~(j) 는 거의 모두 heading_trail 이 **다른 섹션** 으로 오염됨. (k)~(o) 만 `용어의 정의` 아래 올바로 배치됨.

예: `parsed/chunks.jsonl` 에서 `200:` 접두어로 grep 해 보면

```
200:11
200:(a)        ← ¶11의 (a)
200:(b)        ← ¶11의 (b)
200:12
200:13
200:(a)        ← ¶13의 (a)  ← 중복!
200:(b)        ← ¶13의 (b)  ← 중복!
...
200:13.(l)   ← 존재하지 않음. 논리적 경로일 뿐.
```

따라서 `"200:(l)"` 혹은 `"200:13.(l)"` 어느 쪽도 **chunks.jsonl 의 실제
chunk_id 와 직접 매칭되지 않는다.**

### 3.2 해결 규약 (평가 하네스 측 해석 로직)

`queries.yaml` 에서 `"{isa}:{N}.(x)"` 형태(점 + 괄호)가 나타나면:

1. 하네스는 chunks.jsonl 을 ISA·문서 순서대로 로드한 뒤,
2. `chunk_id == "{isa}:{N}"` 인 청크의 `heading_trail` 을 기록(이를 `parent_trail` 이라 함),
3. 그 이후 등장하는 `{isa}:(x)` 청크들 중 **heading_trail 이 `parent_trail` 과 공통 suffix 를 공유** 하는 **첫 매치**를 해당 논리경로의 정답으로 취급한다.
   - 단순 first-match 는 오염된 중복 서브아이템을 잘못 선택함 (§3.1 참조). heading_trail 필터가 **필수**.
   - 예: `"200:13.(c)"` 해석 시 parent=`200:13` 의 trail=`…> 용어의 정의` 이므로, heading_trail 에 `용어의 정의` 가 포함된 `200:(c)` 만 유효.
4. 그 사이에 다음 숫자 문단 `{isa}:{N+1}` 이 나오거나 heading_trail 필터 조건을 만족하는 매치가 없으면 해당 서브아이템은
   **존재하지 않음**으로 판정하고 warning 로그 남김.
5. **DB 실제 저장 상태 확인**: harness 는 실행 전 `SELECT chunk_id, COUNT(*) FROM audit_chunks GROUP BY chunk_id HAVING COUNT(*) > 1` 로 DB 내 잠재적 중복을 exclude 확인. DB 가 단일 PK 라면 `parsed/chunks.jsonl` 의 last 버전만 살아있으므로, 정답 청크 누락을 감지할 수 있도록 logical_path 해석 시 **jsonl 순서의 첫 매치 ≠ DB 저장 청크**인 케이스 warning.

이 규약을 따르면 라벨링 측에서는 자연스러운 논리경로
(`200:13.(c)` = "200 ¶13 의 (c) 서브아이템") 로 표기하고, 하네스는
위치 + heading_trail 필터로 해석한다.

### 3.3 장기 개선 제안 (리더 참고)

`_chunk_id` 를 `{isa}:{parent_para}.{sub}` 포맷(예: `200:13.c`)으로 변경하면
충돌이 근본적으로 해소된다. 다만 Phase 2c 까지 이미 임베딩/DB 가 기존 id 로
생성되었으므로, **Phase 3 마이그레이션에서 한 번에** 바꾸는 것이 안전.
eval 하네스는 그때까지 3.2 의 positional 해석을 사용.

---

## 4. 메트릭 권고

### 4.1 Primary (전체 운영 지표)

**Recall@5 (카테고리별 + 전체)**
- 선정 이유: 실무자가 Cmd-K 검색 결과를 스크롤하는 "현실적 창"이 5건 내외.
- 계산: `|retrieved@5 ∩ expected_primary| / |expected_primary|`
- 목표선(초기): 전체 평균 **≥ 0.70**. 단, cross-standard 는 **≥ 0.55** 로 별도.

### 4.2 Secondary (응답 속도 지표)

**MRR (Mean Reciprocal Rank) — primary chunk 기준**
- 선정 이유: "첫 번째 정답이 몇 번째로 나왔는가" = 실무자의 peek 비용.
- 계산: 각 쿼리에 대해 `1 / rank(첫 primary chunk)` 의 평균.
- 정답이 top-10 안에 전혀 없으면 0.

### 4.3 Tertiary (노이즈 지표)

**Precision@5**
- 선정 이유: 잘못된 chunk 가 상위에 섞이는 정도. recall 과 같이 올라가지
  않는 경우, "정답이 보이지만 오답도 같이 보인다" 는 신호.

### 4.4 보조: nDCG@10

expected_primary 를 relevance=2, expected_related 를 relevance=1 로 놓고
nDCG@10 계산. 튜닝 민감도가 가장 높은 지표이지만 해석이 복잡하므로
모니터링용.

---

## 5. A/B 판정 기준 — `heading_trail` prefix on/off

`embed_text = heading_trail_prefix + "\n\n" + content` 의 prefix 유무를 토글.

### 5.1 가장 민감한 신호

| 지표 | 카테고리 | 기대 효과 | 판정 |
|---|---|---|---|
| **MRR** | `definitions` | 용어 정의는 단일 chunk 에 정답 집중 → heading_trail 이 제목 맥락("용어의 정의")을 주입해 rank 상승 | prefix ON 이 MRR 를 **≥ 0.05** 상회하면 승 |
| **Recall@10** | `cross-standard` | 정답이 여러 ISA 에 분산 → heading_trail 이 ISA 번호/제목을 주입해 장거리 매칭 개선 | prefix ON 이 Recall@10 을 **≥ 0.05** 상회하면 승 |
| Precision@5 | `requirements` | 요구사항 본문은 이미 문맥이 풍부 → heading_trail 과장 시 노이즈 ↑ | prefix ON 이 precision 을 **≥ 0.05** 낮추면 패 |

### 5.2 결론 판정 트리

1. `definitions.MRR`(ON) − `definitions.MRR`(OFF) ≥ +0.05 → **ON 채택 후보**
2. `cross-standard.Recall@10`(ON) − (OFF) ≥ +0.05 → **ON 강력 지지**
3. 단, `requirements.Precision@5` 가 −0.05 이상 하락하면 **조건부 채택**
   (application/definitions 에만 prefix 주입하는 partial ON 도 고려).
4. 모든 카테고리에서 |Δ| < 0.02 → **차이 없음, 기본값(OFF) 유지**.

### 5.3 효과 크기 해석

26건은 절대치 해석에는 작지만, **카테고리 내부 6~7건의 rank-변화 방향성**은
신뢰할 만함. bootstrap(n=1000, 샘플 with replacement) 으로
95% 신뢰구간 찍어 Δ 가 0 을 포함하는지로 유의성 판단.

---

## 6. 향후 확장

- **v2 확장 후보**: 부정확한 의견유형(변형의견), 기타정보(ISA 720), 회계추정(ISA 540),
  그룹감사(ISA 600) 카테고리 추가 — 파싱 대상이 확대되면 각 5건씩 편입.
- **LLM-assisted grading**: expected_related 가 놓친 맥락 chunk 에 대해
  "이 chunk 가 해당 질의의 답으로 적절한가?" 를 LLM 에게 yes/no 로 묻고 간접 보강.
  단, primary 라벨은 반드시 사람이 유지.
- **역질의 (hard negative) 세트**: "이 chunk 가 top-1 로 올라오면 안 되는 질의"
  를 20건 정도 추가하여 false positive 를 점수화.

---

## 7. 실행 체크리스트 (리더 용)

- [ ] `queries.yaml` 로더: `schema_version == 1` 검증, 각 primary/related chunk_id 존재성 검증
- [ ] 서브아이템 positional 해석기(§3.2) 구현 + 미해석 경로 warning
- [ ] pgvector 검색 래퍼: `SELECT ... ORDER BY embedding <=> $1 LIMIT 10`
- [ ] 메트릭 계산: recall@5 / MRR / precision@5 / nDCG@10 (per-category)
- [ ] A/B 실행 스크립트: `--prefix on|off` 플래그 + bootstrap CI
- [ ] 리포트 포맷: JSON + markdown 표 (`docs/eval/reports/{run_id}.md`)
