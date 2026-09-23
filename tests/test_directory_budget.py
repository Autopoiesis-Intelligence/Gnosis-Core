"""Tests for bounded directory resource observation."""
from pathlib import Path

from gnosis.evolution.directory_budget import DirectoryBudget, observe_directory


def test_directory_observation_counts_files(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("abc", encoding="utf-8")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "b.txt").write_text("12345", encoding="utf-8")

    result = observe_directory(tmp_path)
    assert result.entries == 3
    assert result.files == 2
    assert result.directories == 1
    assert result.bytes == 8
    assert not result.budget_exhausted


def test_directory_observation_stops_at_entry_budget(tmp_path: Path) -> None:
    for name in ("a", "b", "c"):
        (tmp_path / name).write_text(name, encoding="utf-8")

    result = observe_directory(tmp_path, budget=DirectoryBudget(max_entries=2, max_bytes=100))
    assert result.entries == 2
    assert result.budget_exhausted


def test_directory_budget_rejects_invalid_limits() -> None:
    for kwargs in ({"max_entries": 0}, {"max_bytes": 0}):
        try:
            DirectoryBudget(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid directory budget was accepted")
