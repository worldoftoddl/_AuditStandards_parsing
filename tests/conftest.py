from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TARGET_DOCX = (
    ROOT / "raw" / "감사인증기준" / "감사기준 전문" / "0. 회계감사기준 전문(2025 개정).docx"
)


@pytest.fixture(scope="session")
def target_docx() -> Path:
    """Primary KICPA audit-standards DOCX.

    Tests that need it skip when it's not present (the `raw/` tree is
    gitignored and only available locally).
    """
    if not TARGET_DOCX.exists():
        pytest.skip(f"target DOCX not available: {TARGET_DOCX}")
    return TARGET_DOCX
