"""Verification of diagnostic pattern adequacy.

This layer deliberately does not infer causality. It measures whether a
pattern has enough provenance diversity and variation to justify forwarding
it to GapDetector.
"""
from __future__ import annotations

from dataclasses import dataclass

from .diagnostic_patterns import DiagnosticPattern


@dataclass(frozen=True)
class DiagnosticPatternVerification:
    pattern_id: str
    eligible_for_gap: bool
    independent_source_count: int
    adequacy_flags: tuple[str, ...]
    blind_spots: tuple[str, ...]
    counterexample_refs: tuple[str, ...] = ()


def verify_diagnostic_pattern(
    pattern: DiagnosticPattern,
    *,
    minimum_independent_sources: int = 2,
    counterexample_refs: tuple[str, ...] = (),
) -> DiagnosticPatternVerification:
    if minimum_independent_sources < 1:
        raise ValueError("minimum_independent_sources must be >= 1")
    flags: list[str] = []
    blind: list[str] = []

    if "COMMON_SOURCE" in pattern.common_mode_flags:
        flags.append("COMMON_MODE_SOURCE")
    if "SAME_STATE" in pattern.common_mode_flags:
        blind.append("STATE_VARIATION_MISSING")
    if "SAME_CANDIDATE" in pattern.common_mode_flags:
        blind.append("CANDIDATE_VARIATION_MISSING")
    if pattern.independent_sources.__len__() < minimum_independent_sources:
        flags.append("INSUFFICIENT_SOURCE_DIVERSITY")
        blind.append("SOURCE_DIVERSITY_MISSING")
    if counterexample_refs:
        flags.append("COUNTEREXAMPLE_PRESENT")

    eligible = (
        pattern.status == "CANDIDATE"
        and not counterexample_refs
        and not any(flag in flags for flag in ("COMMON_MODE_SOURCE", "INSUFFICIENT_SOURCE_DIVERSITY"))
        and not any(blind)
    )
    return DiagnosticPatternVerification(
        pattern.pattern_id,
        eligible,
        len(pattern.independent_sources),
        tuple(flags),
        tuple(blind),
        counterexample_refs,
    )
