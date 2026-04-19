# Phase 3 queries.yaml Self-Audit — 2026-04-19

> 담당: `audit-domain-expert`
> 실행 시점: Phase 3 kickoff. harness (Task #1) 가 `queries.yaml` 을
> 읽어들이기 전에 gold label 정합성을 재검토함.
> 대상: `docs/eval/queries.yaml` v1 (26 queries)

---

## 1. Primary / Related 존재성 검증

전체 26 queries × (primary ∪ related) chunk_ids 를 `parsed/chunks.jsonl`
(4526 rows, 3170 unique chunk_ids) 와 대조.

| 결과 | 건수 |
|---|---:|
| Primary (27건) 모두 파일 내 존재 | **27 / 27** ✓ |
| Related (78건) 모두 파일 내 존재 | **78 / 78** ✓ |
| Positional 해석(`.(x)` 표기) 모두 해석 가능 | **4 / 4** ✓ |

→ 파일 존재성 수준에서 missing label 없음. **단, 해석된 청크가 실제 의도한
   내용인지는 별도 검증 필요 (아래 §2).**

---

## 2. Critical Finding — chunk_id 중복 오염

### 2.1 실측 census

```
unique chunk_ids  : 3170
duplicate chunk_ids : 344 (중복 발생 ID 수)
row-level loss risk: 1356 rows (DB upsert last-write-wins 시)
```

### 2.2 가장 오염된 ID

| chunk_id | 중복 횟수 | 영향 |
|---|---:|---|
| `?:(a)` | 96 | ISA 번호 불명 (preamble/appendix) |
| `?:(b)` | 95 | 동일 |
| `?:(c)` | 59 | 동일 |
| `700:(b)` | 20 | ISA 700 서브아이템 |
| `540:(a)` | 17 | ISA 540 서브아이템 |
| `610:(a)` | 15 | ISA 610 |

### 2.3 정의 영역의 실제 오염 사례

**ISA 200 ¶13 용어의 정의**:
- `200:(c)` 는 chunks.jsonl 에 **2회** 저장:
  1. `용어의 정의 > (c) 감사위험 – 재무제표가 중요하게 왜곡표시…` ← **의도한 정답**
  2. `적용지침 > 재무제표감사 > 재무제표의 작성 > (c) 감사인에게 다음 사항 제공할 책임…`
- `200:(e)`: `용어의 정의 > (e) 적발위험 – 감사위험을 수용가능한…` (정답) vs `(e) 발생할 경우 중요하다(즉, 규모)` (RMM 설명의 sub)
- 정의 ¶13 의 서브아이템 (a)~(j) 중 **(k)~(o) 만 heading_trail 이 `용어의 정의`** 로 올바로 배치됨.

### 2.4 영향도 평가

| 쿼리 ID | 영향 | 조치 |
|---|---|---|
| Q20 (감사위험 정의) | **HIGH**: primary `200:13.(c)` 의 positional first-match 가 오염된 적용지침 (c) 를 잡음 | Q20 strengthen: `200:17`, `200:A35` 를 related 로 추가 (감사위험 본문 fallback). harness 에 heading_trail 필터 요구 |
| Q20 related `200:13.(e)` | MED: 적발위험 정의도 오염된 (e) 가능성 | related 라 비필수. Q20 strengthen 으로 커버 |
| Q14/Q15/Q16/Q22 related `200:13.(n)` | LOW: `200:(n)` 은 heading_trail 검사에서 용어의 정의 아래 유일 | 현상 유지 |
| Q21 (전문가적 의구심 `200:13.(l)`) | LOW: `200:(l)` 용어의 정의 아래 유일 | 현상 유지 |
| Q22 (RMM `200:13.(n)`) | LOW: 동일 | 현상 유지 |
| Q26 (유의적 위험 `315:12.(l)`) | LOW: `315:(l)` 용어의 정의 아래 유일 (확인됨) | 현상 유지 |

---

## 3. ISA 540 파싱 확인 — Q19 primary 확장

Phase 2d queries.yaml v1 작성 시 "ISA 540 이 파싱 대상이면 …" 조건부로 남겨둠.
self-audit 결과 **540 은 311 chunks 로 파싱되어 있음**.

- `540:32` = "경영진이 내린 판단이 경영진의 편의가능성을 나타내는 징후인지 평가" **요구사항 본문**
- `540:A134` = 편의가능성 징후 예시 목록
- `540:A133` = 편의는 계정수준 적발 어려움 (왜곡표시 집합으로 판정)
- `540:(d)` = **경영진의 편의 정의** (240 에는 정의 없음, 540 에만 존재)

→ Q19 primary 를 `240:32` 단일 → **`540:32` + `240:32`** 로 확장.
Cross-standard 성격 더 강화됨 (회계추정 540 ↔ 부정 240).

---

## 4. Harness 구현 시 필수 조치 (리더 전달용)

### 4.1 Positional resolver 업그레이드

README §3.2 업데이트 반영:
1. parent `200:13` 의 heading_trail 을 기록 (`parent_trail`)
2. 이후 등장하는 `200:(x)` 청크들 중 **heading_trail 이 parent_trail 과 공통 suffix 를 공유하는 첫 매치** 만 정답
3. 단순 first-match 금지. 그대로 쓰면 Q20 은 의도와 다른 청크로 채점됨.

### 4.2 DB-jsonl divergence warning

```sql
SELECT chunk_id, COUNT(*) FROM audit_chunks GROUP BY chunk_id HAVING COUNT(*) > 1;
```
DB 가 PK=chunk_id 단일이면 이 쿼리가 0 rows 반환 = **last-write-wins 로 데이터 loss 확정**.
harness 는 실행 전에 "jsonl 의 logical_path 해석 결과 chunk 가 DB 의 실제 chunk 와 다른가?" 를
content_hash 대조로 확인하고, 다르면 rows 기준으로 warning 집계.

### 4.3 ? ISA 번호 청크 처리 방침

`parsed/chunks.jsonl` 의 `?:` 접두 chunk 737건 (ISA 번호 비식별) 은
retrieval 시 noise. eval 시에 DB 필터링(`isa_no != '?'`) 혹은
아예 upsert 제외를 리더가 결정 필요. 현재 queries.yaml 의 정답은
모두 번호 식별된 ISA 이므로 eval 결과에 직접 영향은 없으나,
retrieval 의 top-N 에 ?: 청크가 섞이면 precision 에 악영향.

---

## 5. 이중 게이트 판정 시 해석 가이드 (결과 도착 후 사용)

A/B-1 (BGE vs Upstage) 실측이 어느 시나리오에 속하든 다음 교차표로 해석:

### 5.1 실패가 몰린 카테고리 × 해석

| 실패 집중 카테고리 | 우선 원인 | 판정 함의 |
|---|---|---|
| **definitions (특히 Q20, Q21, Q26)** | 서브아이템 heading_trail 오염 + chunk_id 충돌 | **retrieval 품질이 아닌 chunking 문제**. 모델 선택 결정에서 제외 판단. Phase 3+ chunk_id 스킴 마이그레이션 선결 |
| **cross-standard (Q14, Q17, Q19)** | heading_trail prefix 의 ISA 번호/제목 주입 효과 | prefix ON 이 +0.05 이상 개선 시 ON 채택 강력. 실패 집중 시 A/B-2 의 A (ON) 로 확정 |
| **application (Q08–Q13)** | A-문단 chunk context 부족 가능 | chunk continuation 로직 재검토 신호. Phase 4 candidate |
| **requirements (Q01–Q07)** | 이미 문맥 풍부 — 여기서 실패 시 embedding coverage 부족 | BGE 단독 실패 + Upstage 통과면 한국어 커버리지 부족 신호. BGE 확정 결정 재고려 |

### 5.2 DA 의 시나리오별 도메인 해석 초안

- **시나리오 1 (BGE 0.68 / Upstage 0.72)**: 절대 실패. definitions 에 실패 몰리면 chunking 책임 분리 후 재측정 요구. requirements 에 몰리면 BGE 한국어 코퍼스 한계 → Upstage 유지 권고.
- **시나리오 2 (BGE 0.75 / Upstage 0.82)**: 상대 실패(BGE < 95% of Upstage). application 실패면 chunk context 개선 후 재시도. 전 카테고리 고루 하락이면 Upstage 유지.
- **시나리오 3 (BGE 0.73 / Upstage 0.73)**: 둘 다 통과 + BGE ≥95% of Upstage → **BGE 확정**. 단 정의 카테고리 실패 절대 수가 Upstage 도 통과 못 하는 수준이면 그 실패는 모델 이슈 아닌 chunking 이슈임을 보고.

### 5.3 A/B-2 (heading_trail prefix) 도메인 관점

- ON 이 definitions MRR 을 +0.05 상회 → 정의 청크의 맥락(용어의 정의) 주입 효과. 단, §2.3 중복 오염 상태에서는 prefix 가 **잘못된 heading 을 주입할 수도** 있음 (예: `적용지침 > 재무제표의 작성 > (c) 감사위험` 식으로 잘못 prefix). 카테고리 정답률만 보지 말고 top-1 의 heading_trail 을 샘플링 검사.
- cross-standard Recall@10 이 ON 에서 +0.05 상회면 **강력한 ON 지지**. 이때 도메인 관점 승인 가능.

---

## 6. 대기 중 이후 작업 (harness 결과 도착 대기)

리더가 Task #2 (BGE bulk), #3 (Upstage subset), #4 (A/B-2) 완료 후 eval
실행 결과를 DM 으로 전달하면:

1. 쿼리별 누락 원인 3 분류 (heading_trail dep / chunk boundary / embedding coverage)
2. cross-standard 쿼리 top-10 의 ISA 분포 편향 검사 (Q14/Q17 중심)
3. 서브아이템 positional 해석 warning 건수 집계 (10건 이상이면 Phase 3+ chunk_id 마이그레이션 우선순위 격상)
4. 이중 게이트 판정 + 도메인 권고 첨부 → `phase3_failure_analysis.md` 로 최종 기록

---
