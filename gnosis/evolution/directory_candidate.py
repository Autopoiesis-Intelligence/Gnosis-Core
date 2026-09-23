"""Conservative usage/provenance gate for directory optimization candidates.

A duplicate is not considered removable merely because its bytes match.
This module only produces a candidate/evidence record; it performs no mutation.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


@dataclass(frozen=True)
class DirectoryUsage:
    path: str
    referenced: bool = False
    protected: bool = False
    provenance_id: str = ""


@dataclass(frozen=True)
class OptimizationCandidate:
    content_digest: str
    files: tuple[str, ...]
    removable: tuple[str, ...]
    blocked: tuple[str, ...]
    reason: str


def build_duplicate_candidate(
    files: Iterable[str],
    content_digest: str,
    usage: Mapping[str, DirectoryUsage],
) -> OptimizationCandidate:
    normalized = tuple(sorted(set(str(Path(p)) for p in files)))
    if len(normalized) < 2:
        raise ValueError("duplicate candidate requires at least two files")

    removable: list[str] = []
    blocked: list[str] = []
    for path in normalized[1:]:
        info = usage.get(path, DirectoryUsage(path))
        if info.referenced or info.protected or not info.provenance_id:
            blocked.append(path)
        else:
            removable.append(path)

    if blocked:
        reason = "blocked: usage, protection, or provenance evidence incomplete"
    elif not removable:
        reason = "no removable duplicate established"
    else:
        reason = "candidate only: redundant content with sufficient local evidence"

    return OptimizationCandidate(
        content_digest=content_digest,
        files=normalized,
        removable=tuple(removable),
        blocked=tuple(blocked),
        reason=reason,
    )
