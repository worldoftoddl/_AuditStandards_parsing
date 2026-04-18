# Style map — 회계감사기준 전문(2025 개정)

**상태:** 확정 (Phase 1.5). `docs/style_samples.md` 실측 + `word/styles.xml` 직접 덤프 + 본문 위치 통계로 검증됨.
**대상 파일:** `raw/감사인증기준/감사기준 전문/0. 회계감사기준 전문(2025 개정).docx`

## Phase 1.5 검증 결과 (실측 근거)

### `word/styles.xml`에서 추출한 각 styleId의 공식 속성

| styleId | w:name | basedOn | outlineLvl | numId | ilvl |
|---|---|---|---:|---:|---:|
| `10`   | heading 1       | a3   | **0** |     |   |
| `2`    | heading 2       | a3   | **1** |     |   |
| `3`    | heading 3       | 2    | **2** |     |   |
| `4`    | heading 4       | 3    | **3** |     |   |
| `5`    | heading 5       | 4    | **4** |     |   |
| `6`    | heading 6       | 5    | **5** |     |   |
| `aff3` | 보론 제목        | 3    | —     |     |   |
| `a1`   | **문단**         | a9   | —     | 119 |   |
| `A`    | **문단A**        | a9   | —     | 105 |   |
| `A0`   | 불릿목록A         | a9   | —     | 105 | 1 |
| `A2`   | 목록A           | a9   | —     | 119 | 1 |
| `B`    | 불릿목록B         | A0   | —     |     | 2 |
| `B0`   | 목록B           | A2   | —     |     | 2 |
| `C`    | 목록C           | B0   | —     |     | 3 |
| `a9`   | List Paragraph | a3   | —     |     |   |
| `ad`   | 목차            | a3   | —     |     |   |

### 확정된 해석 (draft 대비 수정 사항)

1. **`outlineLvl`이 모든 heading 스타일에 설정되어 있음.** Phase 1 draft의 "거의 미사용" 판단은 **틀렸음**. `10`=0, `2`=1, `3~6`=2~5 — **스타일 이름과 outlineLvl이 완전히 일치**. 파싱에서 `outlineLvl`을 1차 신호로, styleId를 2차 검증으로 사용 가능.

2. **`a1` = "문단" (numId=119, 요구사항 본문), `A` = "문단A" (numId=105, 적용지침 본문).** 스타일 이름과 numId 분리가 결정적 증거. **`is_application_guidance`는 스타일로 판정** — 정규식 판정 불필요.

3. **`aff3` basedOn=`3`** → level **3** (heading_subsection과 동격). ultraplan 리뷰가 제안한 "level 2"는 틀렸고, draft의 level 3이 맞음.

4. **리스트 계열이 numId로 깔끔하게 분리됨:**
   - **numId=119 (요구사항)**: `a1`(root) → `A2`(ilvl=1) → `B0`(ilvl=2)
   - **numId=105 (적용지침)**: `A`(root) → `A0`(ilvl=1) → `B`(ilvl=2) → `C`(ilvl=3)
   - `a9` ("List Paragraph")는 표준 Word 스타일로, 개별 `w:pPr/w:numPr` override로 쓰임.

5. **`<NO_STYLE>` 실측 결과 — 페이지 반복 헤더 거의 없음.** 상위 반복 항목(`[감사인의 주소]`, `독립된 감사인의 감사보고서` 등)은 감사보고서 **사례 문서의 예시 텍스트**(pos 4960~11440 범위 밀집)이며, 가치 있는 콘텐츠이므로 필터링 대상 아님. draft의 "빈도≥10 & 길이≤20" 임계치는 **적용하지 않음**.

## 최종 매핑 테이블

| styleId | 빈도 | kind | level | section 기본값 | is_application | 비고 |
|---|---:|---|---:|---|---|---|
| `10`   | 36    | `heading_standard`       | 1 | —          | — | 기준서 경계. ISA 번호 개수 일치. |
| `2`    | 182   | `heading_section`        | 2 | (§2 규칙)  | — | 서론/목적/정의/요구사항/적용 등 |
| `3`    | 545   | `heading_subsection`     | 3 | inherit    | — |  |
| `4`    | 575   | `heading_subsubsection`  | 4 | inherit    | — |  |
| `5`    | 350   | `heading_level5`         | 5 | inherit    | — |  |
| `6`    | 116   | `heading_level6`         | 6 | inherit    | — |  |
| `aff3` | 41    | `heading_appendix`       | 3 | `appendix` | — | `APPENDIX` 상태로 전이 |
| `a1`   | 1339  | `paragraph_body`         | — | inherit    | **False** | 요구사항 본문 |
| `A`    | 1917  | `paragraph_body`         | — | `application` | **True** | 적용지침 본문 |
| `A0`   | 2534  | `paragraph_list_item`    | — | `application` | **True**  | 적용지침 리스트 (numId=105 ilvl=1) |
| `A2`   | 1361  | `paragraph_list_item`    | — | inherit    | False | 요구사항/정의 리스트 (numId=119 ilvl=1) |
| `B`    | 203   | `paragraph_list_item`    | — | inherit (A0 기반) | True | 적용지침 중첩 |
| `B0`   | 298   | `paragraph_list_item`    | — | inherit (A2 기반) | False | 요구사항 중첩 |
| `C`    | 31    | `paragraph_list_item`    | — | inherit    | inherit | 3-depth 중첩, 부모 따라감 |
| `a9`   | 207   | `paragraph_list_item`    | — | inherit    | inherit | 표준 List Paragraph. 개별 numPr로 판단 |
| `ad`   | 761   | `toc_entry` (`is_toc=True`) | — | — | — | 목차, 본문/임베딩 제외 |
| `<NO_STYLE>` | 1089 | `paragraph_body` (기본) | — | inherit | inherit | §NO_STYLE 규칙 참조 |

## Heading stack 로직

- level 기반 push/pop: 새 heading의 level ≤ 스택 top이면 pop 후 push.
- `heading_standard` (level 1) 진입 시 스택 전체 clear → push (기준서 전환).
- `heading_appendix` (level 3) 진입 시 `APPENDIX` 상태로 전이. section="appendix"로 오버라이드.
- 본문 블록은 push/pop 없이 현재 스택을 `heading_trail`에 스냅샷.

## Section 규칙 (`2` 스타일 텍스트로 분류)

| 텍스트 | section |
|---|---|
| "서론" | `intro` |
| "감사인의 전반적인 목적" / "목적" | `objective` |
| "용어의 정의" | `definitions` |
| "요구사항" | `requirements` |
| "적용 및 기타 설명자료" | `application` |
| (그 외) | `other` |

> draft의 "도입" 매핑은 실제 표본에 없으므로 제거.
> `aff3`(APPENDIX) 진입 후 본문은 모두 `section="appendix"`로 오버라이드.
> `A`/`A0`/`B` 스타일 블록은 `is_application=True` → section 강제 `application`.

## 상태머신

```
        ┌─────────┐   style='10' 최초 등장   ┌──────────────┐
        │ PRE_TOC │ ─────────────────────▶ │ STANDARD_BODY │ ◀─┐
        └────┬────┘                         └──────┬───────┘   │
             │                                     │           │
   text in                                style='ad' or           style='aff3'
   {"목 차","목차","문단번호",           TOC 신호 문자열             │
    "페이지"} 진입                          │                     │
             ▼                                     ▼           │
        ┌─────────┐   style='10' 등장       ┌─────────────┐    │
        │   TOC   │ ─────────────────────▶ │   APPENDIX  │ ───┘
        └─────────┘                         └─────────────┘
```

- `PRE_TOC`: 문서 시작. 제목/발행일 등 `<NO_STYLE>` 블록은 `heading_document` (level 0) 또는 `paragraph_body`.
- `TOC`: `ad` 전부 `is_toc=True`. `<NO_STYLE>` 중 TOC 헤더 문자열(`목 차`/`목차`/`문단번호`/`페이지`)도 `is_toc=True`.
- `STANDARD_BODY`: 일반 본문. `ad` 등장시에도 `is_toc=True` 유지 (기준서 내부 로컬 목차).
- `APPENDIX`: `aff3` 이후. `heading_standard` 등장으로 벗어남.

## paragraph_id 정규식 (확장판)

ultraplan 리뷰 반영. 괄호 하위(`13(f)`), 범위/하이픈(`A24-A26`, `1-2`), 문자 suffix(`14A`) 포함.

```python
# NFKC 정규화 후 적용
REQ_ID = re.compile(
    r'^(?P<id>\d+(?:-\d+)?(?:[A-Za-z])?(?:\([a-z]\))?)(?:\.\s+|\s+)',
    re.UNICODE,
)
APP_ID = re.compile(
    r'^A(?P<id>\d+(?:-\d+)?(?:[A-Za-z])?(?:\([a-z]\))?)(?:\.\s+|\s+)',
    re.UNICODE,
)
CROSS_REF = re.compile(
    r'문단\s+(?P<target>A?\d+(?:-\d+)?(?:[A-Za-z])?(?:\([a-z]\))?)',
    re.UNICODE,
)
```

**적용 순서 (우선순위):**
1. 스타일 `A`/`A0` → `APP_ID` 우선 시도, 실패 시 prefix 없음으로 처리 (본문 그대로).
2. 스타일 `a1`/`A2` → `REQ_ID` 시도.
3. 매칭된 prefix는 `text`에서 제거, `paragraph_id`에만 저장. `raw_text`는 원본 유지.

## Definition 분해 (`A2` 스타일)

```python
DASH_SPLIT = re.compile(r'\s[\u2010-\u2015]\s', re.UNICODE)  # -, ‐, ‑, –, —, ―

def split_definition(text: str) -> tuple[str, str] | None:
    text = unicodedata.normalize('NFKC', text)
    parts = DASH_SPLIT.split(text, maxsplit=1)
    if len(parts) != 2:
        return None
    term, defn = parts[0].strip(), parts[1].strip()
    # 가드: 용어가 너무 길면 정의 아닌 본문으로 폴백
    if len(term) > 40 or not term:
        return None
    return term, defn
```

폴백 시 해당 블록은 `paragraph_body`로 처리.

## NO_STYLE 처리

상태별:
- `PRE_TOC`: 문서 제목류(`회계감사기준 전문(全文)`, `2025년 11월 개정`) → `heading_document` (level 0).
- `TOC`/진입 직후: `목 차`/`목차`/`문단번호`/`페이지` 고정 집합만 `is_toc=True`.
- `STANDARD_BODY`/`APPENDIX`: 기본 `paragraph_body`. **반복 헤더 휴리스틱은 적용하지 않음** (실측 결과 해당 텍스트는 감사보고서 사례 콘텐츠).

## 테이블 (`w:tbl`) & 각주 (`w:footnoteReference`)

Phase 2a 구현 범위에 포함:
- **테이블**: docx_reader에서 `w:tbl` 감지 시 row/cell 순회 → GFM 파이프 테이블 문자열로 변환한 블록 (`kind="table"`) 생성. heading_trail 상속.
- **각주**: 본문 블록 내 `w:footnoteReference` id를 `[^n]` 마커로 치환. `word/footnotes.xml`에서 해당 id 문단 추출하여 Document의 `footnotes: dict[str, str]` 유지.

## Chunk 전략 (Phase 2b 미리보기)

- **단위:** 1 Block = 1 Chunk (문단 단위). 장문 분할하지 않음.
- **제외:** `is_toc`, `kind="header_footer"` (없음), 빈 텍스트.
- **embed 대상 text:** `heading_trail` 을 prefix로 연결 후 본문.
  ```
  감사기준서 200 … > 요구사항 > 감사범위
  문단 3. 본문…
  ```
- 리스트 아이템은 직전 `paragraph_body`의 id를 parent로 기록 (구현 시 확정).

## Open questions (구현 중 실측 후 확정)

- `a9` (207개) 내부의 실제 numPr 분포 — numId=105/119 비율에 따라 `is_application` 상속 방향 재검토.
- `C` 깊은 중첩의 parent 경로 — `A0→B→C` vs `A2→B0→C` 혼재 여부.
- 각주 인라인 치환 시 `[^n]` 충돌 회피 (본문에 `[^`가 우연히 있을 경우 드물지만 escape).
