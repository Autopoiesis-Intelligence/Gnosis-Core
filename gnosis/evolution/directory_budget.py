"""Resource-aware directory inventory for evolution experiments.

This module observes directory cost without mutating or deleting filesystem
content. It is intentionally outside Ψ-Core and produces evidence suitable for
a later optimization proposal.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DirectoryBudget:
    max_entries: int = 10_000
    max_bytes: int = 100_000_000

    def __post_init__(self) -> None:
        if self.max_entries < 1:
            raise ValueError("max_entries must be positive")
        if self.max_bytes < 1:
            raise ValueError("max_bytes must be positive")


@dataclass(frozen=True)
class DirectoryObservation:
    root: str
    entries: int
    bytes: int
    directories: int
    files: int
    budget_exhausted: bool


def observe_directory(root: str | Path, *, budget: DirectoryBudget = DirectoryBudget()) -> DirectoryObservation:
    path = Path(root)
    entries = files = directories = total_bytes = 0

    if not path.is_dir():
        raise ValueError("directory root must exist and be a directory")

    for item in path.rglob("*"):
        entries += 1
        if item.is_dir():
            directories += 1
        elif item.is_file():
            files += 1
            total_bytes += item.stat().st_size

        if entries >= budget.max_entries or total_bytes >= budget.max_bytes:
            return DirectoryObservation(
                str(path), entries, total_bytes, directories, files, True
            )

    return DirectoryObservation(
        str(path), entries, total_bytes, directories, files, False
    )
