"""Semantic-preservation checks for read-only directory optimization shadow."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .directory_candidate import DirectoryUsage, OptimizationCandidate, verify_candidate_binding


@dataclass(frozen=True)
class DirectorySemanticResult:
    preserved: bool
    required_paths: tuple[str, ...]
    removed_paths: tuple[str, ...]
    reasons: tuple[str, ...]


def verify_shadow_semantics(
    candidate: OptimizationCandidate,
    usage: Mapping[str, DirectoryUsage],
    *,
    required_paths: Iterable[str] = (),
) -> DirectorySemanticResult:
    """Fail closed if the proposed removal intersects declared required paths."""
    reasons: list[str] = []
    required = tuple(sorted(set(str(path) for path in required_paths)))
    removable = set(candidate.removable)

    if not verify_candidate_binding(candidate, usage):
        reasons.append("candidate evidence binding mismatch")

    overlap = tuple(sorted(removable.intersection(required)))
    if overlap:
        reasons.append("shadow removal intersects required paths")

    for path in candidate.removable:
        info = usage.get(path, DirectoryUsage(path))
        if info.referenced or info.protected or not info.provenance_id:
            reasons.append(f"removal lacks sufficient safety evidence: {path}")

    return DirectorySemanticResult(
        preserved=not reasons,
        required_paths=required,
        removed_paths=tuple(candidate.removable) if not reasons else (),
        reasons=tuple(dict.fromkeys(reasons)),
    )
