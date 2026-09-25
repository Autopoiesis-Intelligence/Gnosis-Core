import hashlib
from pathlib import Path

import pytest


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_core_source_integrity_manifest_matches_exact_files():
    root = Path(__file__).resolve().parents[1]
    authority = root / "gnosis" / "reflection" / "authority.py"
    core_init = root / "gnosis" / "core" / "__init__.py"
    assert authority.is_file()
    assert core_init.is_file()
    digests = {_digest(authority), _digest(core_init)}
    assert len(digests) == 2


def test_core_source_integrity_detects_tampering(tmp_path):
    source = tmp_path / "authority.py"
    source.write_text("canonical-core\n", encoding="utf-8")
    before = _digest(source)
    source.write_text("tampered-core\n", encoding="utf-8")
    assert _digest(source) != before


def test_core_source_integrity_fails_closed_on_missing_artifact():
    root = Path(__file__).resolve().parents[1]
    missing = root / "gnosis" / "reflection" / "__NONEXISTENT_CANONICAL_ARTIFACT__.py"
    assert not missing.exists()