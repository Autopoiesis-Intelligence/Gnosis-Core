"""Read-only shadow model for directory optimization.

The shadow layer evaluates a proposed duplicate cleanup without mutating the
real filesystem. It reports structural/resource deltas only; governance
decides whether any later mutation is admissible.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .directory_candidate import DirectoryUsage, OptimizationCandidate, verify_candidate_binding


@dataclass(frozen=True)
class DirectoryShadowResult:
    accepted: bool
    before_count: int
    after_count: int
    removed_count: int
    blocked_count: int
    reasons: tuple[str, ...]


def shadow_directory_optimization(
    candidate: OptimizationCandidate,
    usage: Mapping[str, DirectoryUsage],
    *,
    observed_file_count: int,
) -> DirectoryShadowResult:
    reasons: list[str] = []

    if not verify_candidate_binding(candidate, usage):
        reasons.append("candidate evidence binding mismatch")
    if candidate.blocked:
        reasons.append("candidate contains blocked files")
    if observed_file_count < len(candidate.files):
        reasons.append("observed file count is smaller than candidate scope")
    if any(path not in candidate.files for path in candidate.removable):
        reasons.append("candidate removable set escapes candidate scope")

    removed_count = len(candidate.removable)
    after_count = observed_file_count - removed_count

    if after_count < 0:
        reasons.append("shadow result would produce negative file count")

    return DirectoryShadowResult(
        accepted=not reasons,
        before_count=observed_file_count,
        after_count=after_count,
        removed_count=removed_count if not reasons else 0,
        blocked_count=len(candidate.blocked),
        reasons=tuple(dict.fromkeys(reasons)),
    )
