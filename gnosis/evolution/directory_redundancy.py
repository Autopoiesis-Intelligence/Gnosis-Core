"""Deterministic, read-only redundancy detection for directory optimization.

Detection produces evidence only. It never deletes, moves, or rewrites files.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DuplicateGroup:
    content_digest: str
    files: tuple[str, ...]
    bytes: int


@dataclass(frozen=True)
class RedundancyObservation:
    root: str
    duplicate_groups: tuple[DuplicateGroup, ...]
    scanned_files: int
    budget_exhausted: bool


def _file_digest(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def detect_duplicate_files(
    root: str | Path, *, max_files: int = 10_000
) -> RedundancyObservation:
    path = Path(root)
    if not path.is_dir():
        raise ValueError("directory root must exist and be a directory")
    if max_files < 1:
        raise ValueError("max_files must be positive")

    by_digest: dict[tuple[int, str], list[str]] = {}
    scanned = 0
    exhausted = False

    for item in path.rglob("*"):
        if not item.is_file():
            continue
        scanned += 1
        if scanned > max_files:
            exhausted = True
            break
        size = item.stat().st_size
        key = (size, _file_digest(item))
        by_digest.setdefault(key, []).append(str(item))

    groups = tuple(
        DuplicateGroup(digest, tuple(sorted(files)), size)
        for (size, digest), files in sorted(by_digest.items(), key=lambda x: x[0])
        if len(files) > 1
    )
    return RedundancyObservation(str(path), groups, scanned, exhausted)
