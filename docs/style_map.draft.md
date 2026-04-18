# Style map (draft) — 회계감사기준 전문(2025 개정)

Phase 1 산출물. `docs/style_samples.md` 실측 근거 + 회계감사기준 문서 구조 관찰로 도출한 스타일 → 의미 매핑 초안. **Phase 2 전에 승인 필요.**

## 전제

- **`outlineLvl` / numPr 거의 미사용** — Word 기본 heading 레벨을 쓰지 않음. 스타일 이름(`10`, `2`, `3`, `4`, `5`, `6`, `A`, `A0`, `A2`, `a1`, `ad`, `aff3`, `B`, `B0`, `C`, `a9`, `<NO_STYLE>`)만 유일한 구조 신호.
- **숫자 스타일이 heading hierarchy** — `10` > `2` > `3` > `4` > `5` > `6` 으로 내려감. `10`은 감사기준서 이름, `2`는 기준서 내 대섹션(서론/용어의 정의/요구사항/적용 및 기타 설명자료 등).
- **알파벳 스타일이 본문** — `a1`, `A`, `A0`, `A2`, `B0`, `B`, `C`, `a9`는 본문·리스트. 세부 구분은 IR 포스트-처리(번호 파싱)에서 추론.

## 매핑

| 스타일 | 빈도 | 제안 kind | level | 비고 |
|---|---:|---|---:|---|
| `10` | 36 | `heading_standard` | 1 | "감사기준서 200 …" — 기준서 경계. 정확히 ISA 번호 개수와 일치 |
| `2` | 182 | `heading_section` | 2 | 서론 / 감사인의 전반적 목적 / 용어의 정의 / 요구사항 / 적용 및 기타 설명자료 — 본문 섹션 헤더 |
| `3` | 545 | `heading_subsection` | 3 | 예: "이 감사기준서의 범위", "시행일", "전문가적 의구심" |
| `4` | 575 | `heading_subsubsection` | 4 | 예: "관련 요구사항의 준수", "감사범위(문단 3 참조)" |
| `5` | 350 | `heading_level5` | 5 | 예: "중요왜곡표시위험", "적발위험" |
| `6` | 116 | `heading_level6` | 6 | 예: "통제환경", "통제활동" |
| `aff3` | 41 | `heading_appendix` | 3 | "보론 N (문단 Am 참조) …" — 부록 제목. level은 섹션과 동격 |
| `a1` | 1339 | `paragraph_body` | — | 기준서 본문 단락 |
| `A` | 1917 | `paragraph_body` | — | 기준서 본문 단락(서브타입 없음) |
| `A0` | 2534 | `paragraph_list_item` | — | 리스트 하위 항목. 부모 paragraph의 마지막 문장이 ":" 또는 "다음과 같다"로 끝나는 패턴 기대 |
| `A2` | 1361 | `paragraph_definition` | — | 용어 정의 섹션의 항목. "용어 – 뜻" 패턴 |
| `B0` | 298 | `paragraph_list_item` | — | 본문 내 enumerate. `A0`와 유사하지만 다른 뿌리 |
| `B` | 203 | `paragraph_list_item` | — | 짧은 나열(예: "재무상태표", "손익계산서") |
| `C` | 31 | `paragraph_list_item` | — | 깊은 중첩 리스트 |
| `a9` | 207 | `paragraph_list_item` | — | numPr 有(numId=8 등). 정식 번호 리스트 |
| `ad` | 761 | **TOC entry** (`is_toc=True`) | — | 목차 본문. 페이지 번호(탭 포함) 동반. Phase 2에서 `is_toc=True`로 표시, 본문/임베딩 대상에서 제외 |
| `<NO_STYLE>` | 1589 | **mixed** | — | 세부 분기(§ "NO_STYLE 처리" 참고) |

## NO_STYLE 처리

`<NO_STYLE>` 1589개는 단일 규칙으로 처리 불가. 텍스트 내용으로 분기:

1. **문서 제목**: "회계감사기준 전문(全文)", "2025년 11월 개정" — `heading_document` (level 0). 최초 수 블록만.
2. **목차 헤더**: "목 차", "페이지", "목차", "문단번호" — `is_toc=True`.
3. **페이지 반복 헤더 의심**: "재무제표감사" 등 짧고 반복되는 텍스트 — **정확한 반복 빈도 집계**로 임계치(예: ≥ 10회 반복 & ≤ 20자) 초과 시 `is_header_footer=True` 플래그 후 본문 제외.
4. **나머지**: `paragraph_body`로 폴백.

실제로는 Phase 2 `structure.py`에서 **문서 상태 머신**을 돌려야 안전:
- 상태: `PRE_TOC` → `TOC` → `STANDARD_BODY`
- 첫 `10` 스타일 등장 시 `STANDARD_BODY`로 전이, 이후 `ad`는 `STANDARD_BODY` 내부 로컬 목차이므로 is_toc=True 유지.

## Heading trail 구축 규칙 (Phase 2 stack 로직)

- heading 스택은 level 기반 push/pop: 새 heading의 level ≤ 스택 top의 level이면 pop, 이후 push.
- 본문 블록은 push/pop 하지 않고 현재 스택을 `heading_trail`에 복사.
- `heading_standard`(level 1) 블록이 들어오면 스택 전체 clear → push (기준서 전환).
- `aff3`(heading_appendix) 진입 시 `section`을 `"appendix"`로 전환.

## Section 매핑 규칙 (`section` 필드)

`heading_section` (`2` 스타일) 텍스트로 분류:

| heading_section 텍스트 | section |
|---|---|
| "서론" / "도입" | `intro` |
| "감사인의 전반적인 목적" / "목적" | `objective` |
| "용어의 정의" | `definitions` |
| "요구사항" | `requirements` |
| "적용 및 기타 설명자료" | `application` |
| (그 외) | `other` |

`heading_appendix` 구간 내 본문은 모두 `section="appendix"` 로 오버라이드.

## paragraph_id 추출 규칙 (Phase 2 `numbering.py`)

- ISA 문단 번호는 텍스트에 **인라인**으로 박혀 있음. 예: `"1. 이 감사기준서는 …"`, `"A15. 적용지침은 …"`.
- 정규식:
  - 요구사항: `^(?P<id>\d+[A-Za-z]?)(\.|\s)`
  - 적용지침: `^A(?P<id>\d+(?:[-.]?\d+)?)(\.|\s)`
- 매칭 시 `paragraph_id` 세팅 및 본문에서 prefix 제거.
- 적용지침 블록은 `is_application_guidance=True`.

## 미결 / Phase 2에서 실측 확인

1. `A0`/`B0`/`B`/`C` 리스트 항목의 **부모 연결**. 현재 계획은 "직전 본문 블록 = 부모" 로컬 규칙. 중첩 리스트가 있을지 기준서 315 표본으로 확인 필요.
2. `A2` 정의 블록의 "용어 – 뜻" 파싱. `–` / `-` / `—` 다 허용해야 함.
3. `ad` (TOC) 이후 `10` (새 기준서) 전환 시 페이지 번호 주변 공백 정리.
4. 반복 페이지 헤더("재무제표감사" 등) 탐지 임계치 — 실측 통계 뽑은 후 결정.

---

**CHECKPOINT 1 승인 요청**: 이 매핑으로 Phase 2 진행 가능합니까? 특히:
- `10 → heading_standard (level 1)`, `2 → heading_section (level 2)`, `3~6 → 하위 레벨` 순서가 맞는지
- `ad`를 항상 `is_toc=True`로 두는 정책 (기준서 안쪽의 로컬 목차도 포함)
- `<NO_STYLE>` 페이지 반복 헤더 탐지 임계치 "≥ 10회 & ≤ 20자"
