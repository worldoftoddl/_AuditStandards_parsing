# Parsing Plan — KICPA 감사인증기준 → pgvector

**상태:** Phase 1.5 + Phase 2a PR1 완료 (2026-04-18). 계획 구성은 이후 "ultraplan"에 따라 재조정되었으므로 §5 Phase Breakdown 도입부를 먼저 참조.
**전제:** `docs/style_map.md` (Phase 1.5 확정본) 이 기준점.

---

## 1. Requirements Restatement

- **입력:** `raw/` 하위 17개 자료 (DOCX 주 타겟, PDF/DOC 후순위).
- **출력:** (a) 구조화 IR → (b) Markdown 중간표현 → (c) pgvector 임베딩 저장.
- **메커니즘:** 스타일 이름 기반 블록 분류 + 상태머신 walker + **정규식 기반 paragraph_id/cross-ref 추출** + 청크 전략.
- **운영:** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 하에서 도메인/인프라 분권 지점마다 teammate 호출.
- **제약 (CLAUDE.md):** PHASED EXECUTION (파일 ≤5/phase), FORCED VERIFICATION, 승인 게이트.

---

## 2. Architecture

```
raw/*.docx  ┐
raw/*.pdf   │──► loader ──► IR (Block[])
raw/*.doc   ┘                    │
                                 ▼
                         classifier (style → kind)
                                 │
                                 ▼
                    stateful_walker (heading stack,
                     section, TOC/h-f detector)
                                 │
                                 ▼
                    numbering.py      crossref.py
                    (para_id regex)   (문단 N 참조)
                                 │
                                 ▼
                           chunker (요구사항 + 대응 적용지침 묶음)
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           markdown_emitter            embedder (upstage/bge)
           parsed/**.md                       │
                                              ▼
                                     pg_writer (pgvector)
```

**모듈 책임 경계:**

| 모듈 | 입력 | 출력 | 순수성 |
|---|---|---|---|
| `loader/docx.py` | `Path` | `Block[]` (raw) | 순수 (I/O 제외) |
| `classifier.py` | `Block[]` | `Block[]` (kind 채움) | 순수 |
| `walker.py` | `Block[]` | `Block[]` (heading_trail, section, flags) | 순수 (상태머신) |
| `numbering.py` | `Block[]` | `Block[]` (paragraph_id) | 순수 (regex) |
| `crossref.py` | `Block[]` | `Block[]` (refs[]) | 순수 (regex) |
| `chunker.py` | `Block[]` | `Chunk[]` | 순수 |
| `emitter/markdown.py` | `Block[]` | `str` | 순수 |
| `embed/*.py` | `Chunk[]` | `Chunk[]` + vector | I/O + 캐시 |
| `db/writer.py` | `Chunk[]+vec` | — | I/O |

---

## 3. IR & PG Schema

### 3.1 `Block` (IR dataclass)

```python
@dataclass
class Block:
    # identity
    block_id: str                # f"{source_stem}#{ordinal:05d}"
    source_path: Path
    ordinal: int

    # raw
    style_name: str              # '10', 'A0', '<NO_STYLE>' …
    text: str                    # 정규식으로 prefix 제거된 본문
    raw_text: str                # 원본 (디버깅/복원용)
    num_pr: str | None           # 'numId=8,ilvl=0' 형태

    # classified
    kind: Literal[
        'heading_document','heading_standard','heading_section',
        'heading_subsection','heading_subsubsection','heading_level5',
        'heading_level6','heading_appendix',
        'paragraph_body','paragraph_list_item','paragraph_definition',
        'toc_entry','header_footer','unknown'
    ]
    level: int | None            # 0..6, appendix는 3 (section 동격)

    # derived
    heading_trail: tuple[str, ...]   # 현재까지의 heading 스택 텍스트
    section: Literal['intro','objective','definitions','requirements',
                     'application','appendix','other'] | None
    paragraph_id: str | None         # '1', '14A', 'A15', 'A1-2'
    is_application_guidance: bool    # paragraph_id가 A*로 시작
    is_toc: bool
    is_header_footer: bool
    refs: list[str]                  # ['A15','14(a)', …]  (crossref 추출)
```

### 3.2 Postgres (`pgvector`)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE audit_chunks (
    id              BIGSERIAL PRIMARY KEY,
    source_path     TEXT NOT NULL,
    standard_no     TEXT,                      -- '200','315' …
    section         TEXT,                      -- intro/requirements/…
    heading_trail   TEXT[],
    paragraph_ids   TEXT[],                    -- 묶음 청크면 복수
    is_application  BOOL NOT NULL DEFAULT false,
    text            TEXT NOT NULL,             -- markdown 청크 본문
    token_estimate  INT,
    embedding       vector(EMBED_DIM),         -- 1024 or 4096 (Phase 6 확정)
    content_hash    CHAR(64) NOT NULL,         -- SHA-256, dedupe/캐시 키
    created_at      TIMESTAMPTZ DEFAULT now(),

    UNIQUE (source_path, content_hash)
);

CREATE INDEX ON audit_chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
CREATE INDEX ON audit_chunks (standard_no, section);
CREATE INDEX ON audit_chunks USING GIN (heading_trail);
CREATE INDEX ON audit_chunks USING GIN (paragraph_ids);
```

> `EMBED_DIM`은 Phase 6에서 provider 확정 시 ALTER. HNSW 선택 근거는 `vector-db-expert` teammate 리뷰에서 확정.

---

## 4. Regex Catalog

모든 정규식은 `numbering.py` / `crossref.py` / `detectors/` 내에 **명명 상수로 격리**하고, 테이블-드리븐 pytest로 긍정·부정 케이스 양측 검증.

| 이름 | 패턴 | 대상 스타일 | 목적 | 테스트 ≥ |
|---|---|---|---|---|
| `STANDARD_HEADER` | `^감사기준서\s+(?P<no>\d{3})(?:호)?\s+(?P<title>.+)$` | `10` | 기준서 번호·제목 분리 | 36 (전체) |
| `REQ_PARA_ID` | `^(?P<id>\d+[A-Za-z]?)\.\s+(?P<rest>.+)$` | `a1`/`A`/`A0`/`B0` | 요구사항 문단 ID | 30 |
| `APP_PARA_ID` | `^A(?P<id>\d+(?:[-.]?\d+)?)\.\s+(?P<rest>.+)$` | `A`/`A0` | 적용지침 ID | 30 |
| `APPENDIX_TITLE` | `^보론\s*(?P<n>\d+)?\s*\(문단\s+A?\d+(?:-\d+)?\s*참조\)\s*(?P<title>.+)$` | `aff3` | 부록 제목 파싱 | 20 |
| `TOC_LINE` | `^(?P<title>.+?)(?:\t+|\s{3,})(?P<pages>\d+(?:-\d+)?)\s*$` | `ad` | 목차 라인 (탭 or 공백 3+) | 15 |
| `CROSS_REF` | `문단\s+(?P<target>A?\d+(?:\s*\([a-z]\))?(?:-\d+)?)` | 모든 본문 | 교차참조 수집 | 20 |
| `DEFINITION_SPLIT` | `^(?P<term>[^–\-—]+?)\s*[–\-—]\s+(?P<def>.+)$` | `A2` | 용어–정의 분리 (dash variants) | 20 |
| `ENUM_PAREN` | `^\((?P<n>[가-힣a-zA-Z0-9]+)\)\s*` | `a9`/`B0`/`C` | 하위 enumerate 번호 | 15 |
| `PAGE_HEADER_CANDIDATE` | N/A (길이≤20 && 반복≥10) | `<NO_STYLE>` | 페이지 반복 헤더 탐지 | 빈도 통계 기반 |

**규칙:**
- 매칭된 prefix(예: `"1. "`, `"A15. "`)는 `text`에서 제거, `paragraph_id`에만 보존.
- `raw_text`는 항상 원본 유지 (디버깅/복원용).
- dash variants(`–`/`-`/`—`)는 모두 허용, `\u2010-\u2015` 포함 정밀화.
- `CROSS_REF`는 `re.findall` 방식으로 `refs[]`에 축적.
- 모든 regex는 `re.compile(..., re.UNICODE)` 명시.

---

## 5. Phase Breakdown

> **2026-04-18 개정 (ultraplan 승인본 반영).** 본 섹션의 원래 Phase 2 / 3 / 4는
> ultraplan이 승인한 **PR1 단일 묶음** (5 files: `ir`, `styles`, `docx_reader`,
> `numbering`, `structure`)로 병합되었습니다. 개별 승인 게이트(✅2, ✅3, ✅4)
> 대신 **PR1 종료 시점에 도메인 전문가 시뮬레이터와의 교차검증** 하나로
> 대체합니다. PR2 이하 phase는 원래대로 유지.
>
> 이 병합의 근거: (a) ir + classifier + walker + regex/numbering은 모두
> 같은 IR 자료구조를 공유하므로 분리 구현시 API 인터페이스 공중부양이
> 발생, (b) 도메인 전문가 교차검증이 "분류 정확도 >99%" / "상태머신 로그
> 리뷰" / "정규식 커버리지" 3 게이트를 동시에 만족시킴.

### Phase 2a PR1 · 파싱 코어 _(5 files — 완료 2026-04-18)_

- `src/audit_parser/ir.py` — `Block`, `RawBlock`, `NumPr`, `NumLevel`, `AbstractNum`, `NumberingSpec`, `Standard`, `Document` dataclasses
- `src/audit_parser/styles.py` — `STYLE_MAP` 단일 진리 원천 (style_map.md 반영)
- `src/audit_parser/docx_reader.py` — lxml 기반 DOCX → `RawBlock[]` + footnotes + NumberingSpec
- `src/audit_parser/numbering.py` — 정규식 fallback + numbering.xml 파서 + `NumberingCounter` (abstractNumId 키 공유)
- `src/audit_parser/structure.py` — 상태머신 + heading stack + section 분류 + paragraph_id walker

**검증 결과:**
- 36 ISAs 인식, 851 footnotes, 74 tables
- paragraph_id 커버리지: a1 (요구사항 본문) 97.1%, A (적용지침 본문) 94.0%
- 25 ISA × golden first-requirement-id 테이블 교차검증 PASS
- pytest 95 / ruff 0 에러

### Phase 2 (원안) · Loader + IR + Classifier _(파일 ≤5) — ultraplan에 의해 PR1로 병합_

- `src/audit_parser/ir.py` — `Block` dataclass
- `src/audit_parser/loader/docx.py` — python-docx + lxml 기반 로더
- `src/audit_parser/classifier.py` — 스타일→kind 매핑 (style_map.draft.md 반영)
- `tests/test_classifier.py` — 테이블 드리븐
- `tests/fixtures/mini.docx` — 주 DOCX에서 150블록 표본

**검증:** `ruff check src tests && pytest -q`
**Checkpoint ✅ 2**: 분류 정확도 > 99% (style_map 매핑과 교차검증).

---

### Phase 3 · Stateful Walker + 탐지기 _(≤5)_

- `src/audit_parser/walker.py` — heading stack + `PRE_TOC → TOC → STANDARD_BODY` 상태머신
- `src/audit_parser/detectors/toc.py` — `ad` + `<NO_STYLE>` 목차 헤더 탐지
- `src/audit_parser/detectors/page_header.py` — 반복 빈도 기반 header/footer 탐지
- `tests/test_walker.py`
- `tests/test_detectors.py`

**검증:** 36개 `10` 블록 모두 `heading_standard`로 승격되고 스택이 clear되는지. 목차 761블록이 `is_toc=True`로 처리되는지.
**Checkpoint ✅ 3**: 상태머신 전이 로그 리뷰.

---

### Phase 4 · Numbering + Cross-ref _(≤4)_

- `src/audit_parser/numbering.py`
- `src/audit_parser/crossref.py`
- `tests/test_numbering.py`
- `tests/test_crossref.py`

**검증:** 요구사항 문단 ID 매칭율, 적용지침 A*. 테이블 케이스 각 ≥20개.
**Checkpoint ✅ 4**: `audit-domain-expert` teammate가 실패 케이스 수집 후 regex 보강.

---

### Phase 5 · Markdown Emitter + Chunker _(≤4)_

- `src/audit_parser/emitter/markdown.py`
- `src/audit_parser/chunker.py` — 전략: **요구사항 문단 N + 그 본문에서 참조한 `A*` 적용지침 묶음** 을 기본 청크 단위
- `tests/test_emitter.py`
- `tests/test_chunker.py`

**Checkpoint ✅ 5**: 청크 전략은 `audit-domain-expert` + `vector-db-expert` 공동 리뷰.

---

### Phase 6 · Embedding Provider + Cache _(≤5)_

- `src/audit_parser/embed/base.py` — protocol
- `src/audit_parser/embed/upstage.py` — httpx + tenacity
- `src/audit_parser/embed/bge.py` — 로컬 fallback
- `src/audit_parser/embed/cache.py` — content-hash 기반 SQLite 캐시 (`.embed_cache.sqlite`)
- `tests/test_embed.py` (mock HTTP)

**Checkpoint ✅ 6**: `vector-db-expert` teammate가 차원·passage/query 모델 쌍 승인 후 `EMBED_DIM` 확정.

---

### Phase 7 · pgvector Schema + Writer _(≤4)_

- `src/audit_parser/db/schema.sql`
- `src/audit_parser/db/writer.py` — psycopg3
- `src/audit_parser/db/migrations.py` — 간단 idempotent DDL
- `tests/test_writer.py` — testcontainers-python(postgres:16 + pgvector)

**Checkpoint ✅ 7**: 멱등성·dedupe·index 사용 계획 확인.

---

### Phase 8 · Loader 확장 _(≤5)_

- `src/audit_parser/loader/pdf.py` — pdfplumber/pymupdf 프로토타입 비교 결과 반영
- `src/audit_parser/loader/doc.py` — `libreoffice --headless --convert-to docx` 사전처리 파이프
- `tests/test_pdf_loader.py`
- `tests/test_doc_loader.py`

> PDF/DOC은 구조 신호가 없으므로 **classifier/walker를 재사용하려면 스타일을 합성**해야 함. 대안: 이 둘은 별도 "plain-text 경로"로 분리하고 heading은 폰트 크기/행 간격 휴리스틱 사용.

**Checkpoint ✅ 8**: 경로 선택 (`audit-domain-expert` 승인).

---

### Phase 9 · CLI + E2E _(≤4)_

- `src/audit_parser/cli.py` — `typer` 기반 `audit-parser ingest <glob>` / `audit-parser reembed`
- `tests/test_e2e.py`
- `Makefile` or `justfile`
- README 업데이트

**Checkpoint ✅ 9**: 전체 DOCX → pgvector 1회 성공.

---

## 6. Teammate Dispatch Plan

### 6.1 팀 구성 (Phase 2 착수 직전 1회 생성)

| 이름 | agentType / subagent | 소유 영역 | 예상 task 수 |
|---|---|---|---|
| `audit-domain-expert` | general-purpose (커스텀 프롬프트) | `docs/**`, regex 케이스 파일 | 5-6 |
| `vector-db-expert` | `everything-claude-code:database-reviewer` | `src/audit_parser/db/**`, `src/audit_parser/embed/**` | 5-6 |
| `python-architect` | `everything-claude-code:architect` | `pyproject.toml`, 모듈 경계 리뷰 | 3-4 |

> **리더 = 메인 세션 (나).** 3명 구성이 agent-teams 문서 권장 범위(3-5) 하단. skeptic은 Phase 5 이후 단발 스폰 후 종료.

### 6.2 디스패치 매트릭스

| 시점 (Phase) | 호출 대상 | 방식 | 전달 컨텍스트 | 기대 산출물 | 반영 방법 |
|---|---|---|---|---|---|
| Phase 2 시작 | audit-domain-expert | SendMessage (assign task) | `style_map.draft.md`, `style_samples.md`, `CLAUDE.md` 경로 | 매핑 최종 승인 또는 수정안 | `classifier.py` 구현 전 매핑 확정 |
| Phase 4 완료 | audit-domain-expert | DM | `numbering.py` diff + 실패 후보 목록 | 놓친 패턴 리포트 (regex 추가) | 정규식 테이블 업데이트 + 테스트 추가 |
| Phase 5 kickoff | audit-domain-expert + vector-db-expert | broadcast (예외적 1회) | chunker 전략 초안, 샘플 청크 20개 | 청크 크기·요구-지침 묶기 규칙 승인 | `chunker.py` 파라미터 확정 |
| Phase 6 시작 | vector-db-expert | DM + plan_approval_request | `.env.example`, passage/query 모델 후보, 차원 | `EMBED_DIM` 확정, HNSW vs IVFFlat 결정 | schema.sql 최종화 |
| Phase 7 시작 | vector-db-expert | DM + plan_approval_request | `schema.sql` 초안, dedupe 정책 | 인덱스/GIN 전략 승인 | 마이그레이션 적용 |
| Phase 2·6 사이 | python-architect | DM | 완성된 모듈 트리, pyproject | 타입 힌트·optional-deps 구성 리뷰 | 구조 조정 1회 |
| Phase 5 직후 (단발) | skeptic (spawn 후 shutdown) | general-purpose | 현재까지 diff 요약 | "과잉설계" 판정 또는 단순화 제안 | 필요 시 refactor 단일 커밋 |

### 6.3 운영 원칙 (agent-teams 문서 준수)

- **파일 충돌 차단:** 각 teammate는 위 표의 "소유 영역"만 수정. 교차 수정은 리더 경유.
- **Spawn prompt에 컨텍스트 포함:** 리더 대화기록 비상속 → 참조 파일 경로 명시.
- **Plan approval 요구 지점:** pgvector 스키마 변경, Upstage API 호출 발생 작업 (비용/외부 상태).
- **Broadcast 최소화:** Phase 5 kickoff 1회만. 이후 DM.
- **Cleanup은 리더 전용:** 모든 phase 완료 후 `shutdown_request` 순차 송신 → 최종 팀 제거.
- **Nested teams 금지:** teammate는 스스로 팀을 만들지 않음.

---

## 7. Risks & Open Questions

| # | 리스크 | 영향 | 완화 |
|---|---|---|---|
| R1 | Upstage vs BGE 차원 불일치 → DB 재구축 | HIGH | Phase 6에서 `vector-db-expert` 승인 후 `EMBED_DIM` 고정, 변경 시 table rename 마이그레이션 |
| R2 | PDF/DOC 구조 손실 | MED | Phase 8 진입 전 pdfplumber/pymupdf/docling 3-way 프로토타입 1세션 |
| R3 | `<NO_STYLE>` 페이지 헤더 임계치 오탐 | MED | Phase 3 후 빈도 분포 EDA 결과로 임계치 튜닝 |
| R4 | `a9`(numPr) vs `A0`(패턴) 리스트 부모-자식 혼선 | MED | Phase 3 walker에서 "직전 본문 블록 = 부모" + numPr.ilvl 우선순위 규칙 |
| R5 | `A0`에 요구사항과 적용지침 혼재 | HIGH | Phase 4에서 `REQ_PARA_ID` vs `APP_PARA_ID` 둘 다 시도, A* 우선 |
| R6 | Teammate 파일 충돌 | LOW | 6.3 운영 원칙 준수 |
| R7 | 작성사례 zip/xlsx 저작권·포맷 이질성 | LOW | 범위 외로 명시, Phase 9 이후 선택적 확장 |

---

## 8. Verification Strategy

**Python이므로 FORCED VERIFICATION 번역:**
- Phase 2에서 pyproject에 추가: `pytest`, `pytest-cov`, `mypy`(선택).
- 각 phase 완료 시:
  ```bash
  ruff check src tests
  ruff format --check src tests
  pytest -q --cov=audit_parser --cov-fail-under=80
  ```
- Phase 7 이후: `pytest tests/test_e2e.py` — testcontainers Postgres.
- 정규식 모듈은 커버리지 **100%** 목표 (순수 함수).

**로그/관측:**
- `rich` 기반 진행 바 + walker 상태 전이 `--debug` 모드 출력.
- 파싱 산출물 diff는 `parsed/` 아래에 커밋 제외(`.gitignore`). 대신 스냅샷 테스트용 골든 파일 `tests/golden/` 소량 유지.

---

## 9. Estimated Complexity & Effort

| Phase | 복잡도 | 예상 세션 | 주요 비용 |
|---|---|---|---|
| 2 | M | 1 | DOCX XML 파싱, style 매핑 |
| 3 | M | 1 | 상태머신·통계 튜닝 |
| 4 | M | 1 | regex 정확도 |
| 5 | M | 1 | 청크 전략 도메인 협의 |
| 6 | MH | 1-2 | 외부 API, 캐시 |
| 7 | MH | 1 | testcontainers, DDL |
| 8 | H | 2 | 포맷 다형성 |
| 9 | M | 1 | 통합 + CLI UX |

**합계:** 9-11 세션. 도메인/벡터DB teammate 호출이 병렬화를 가속.

---

## 10. WAITING FOR CONFIRMATION

다음 사항에 대한 명시적 승인을 요청합니다:

1. **Phase 구성과 파일 ≤5 제약 준수 — Phase 2부터 착수해도 됩니까?**
2. **Teammate 3인 구성 (audit-domain-expert / vector-db-expert / python-architect) 을 Phase 2 시작 시점에 스폰합니까?**
3. **정규식 카탈로그(§4) 9개를 Phase 3~4 구현 기준선으로 확정합니까?**
4. **`EMBED_DIM` 결정은 Phase 6로 이연, 그 전까지 스키마에 placeholder 유지합니까?**
5. **작성사례 zip/xlsx는 범위 외로 확정합니까?**

`proceed` / `yes` / `진행` / `수정: …` 로 응답해 주세요.
