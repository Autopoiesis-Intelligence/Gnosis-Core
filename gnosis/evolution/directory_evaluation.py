"""Unified, read-only shadow evaluation for directory optimization."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping
from .directory_candidate import DirectoryUsage, OptimizationCandidate
from .directory_resources import DirectoryResourceDelta, DirectoryResourceSnapshot, calculate_resource_delta
from .directory_semantics import DirectorySemanticResult, verify_shadow_semantics
from .directory_shadow import DirectoryShadowResult, shadow_directory_optimization

@dataclass(frozen=True)
class DirectoryShadowEvaluation:
    accepted: bool
    structural: DirectoryShadowResult
    semantic: DirectorySemanticResult
    resource_delta: DirectoryResourceDelta
    reasons: tuple[str, ...]

def evaluate_directory_shadow(candidate: OptimizationCandidate, usage: Mapping[str, DirectoryUsage], *, observed_file_count: int, before: DirectoryResourceSnapshot, after: DirectoryResourceSnapshot, required_paths: Iterable[str] = ()) -> DirectoryShadowEvaluation:
    structural = shadow_directory_optimization(candidate, usage, observed_file_count=observed_file_count)
    semantic = verify_shadow_semantics(candidate, usage, required_paths=required_paths)
    resource_delta = calculate_resource_delta(before, after)
    reasons = tuple(dict.fromkeys((*structural.reasons, *semantic.reasons, *(["resource regression"] if not resource_delta.non_worsening else []))))
    return DirectoryShadowEvaluation(accepted=not reasons, structural=structural, semantic=semantic, resource_delta=resource_delta, reasons=reasons)
