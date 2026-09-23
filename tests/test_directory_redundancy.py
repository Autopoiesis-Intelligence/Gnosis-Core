from pathlib import Path

from gnosis.evolution.directory_redundancy import detect_duplicate_files


def test_detect_duplicate_files_is_deterministic_and_read_only(tmp_path: Path) -> None:
    a = tmp_path / "a.txt"
    b = tmp_path / "nested" / "b.txt"
    b.parent.mkdir()
    a.write_bytes(b"same")
    b.write_bytes(b"same")

    before = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*"))
    result = detect_duplicate_files(tmp_path)
    after = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*"))

    assert before == after
    assert result.scanned_files == 2
    assert len(result.duplicate_groups) == 1
    assert result.duplicate_groups[0].files == (str(a), str(b))


def test_different_content_is_not_redundant(tmp_path: Path) -> None:
    (tmp_path / "a").write_bytes(b"one")
    (tmp_path / "b").write_bytes(b"two")
    assert detect_duplicate_files(tmp_path).duplicate_groups == ()


def test_duplicate_scan_is_bounded(tmp_path: Path) -> None:
    for name in ("a", "b", "c"):
        (tmp_path / name).write_bytes(name.encode())
    result = detect_duplicate_files(tmp_path, max_files=2)
    assert result.scanned_files == 3
    assert result.budget_exhausted


def test_invalid_duplicate_scan_budget_is_rejected(tmp_path: Path) -> None:
    try:
        detect_duplicate_files(tmp_path, max_files=0)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid scan budget was accepted")
