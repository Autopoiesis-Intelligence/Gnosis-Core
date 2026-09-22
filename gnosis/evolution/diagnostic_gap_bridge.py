"""Controlled bridge from verified diagnostic patterns to GapHypothesis."""
from __future__ import annotations

from .diagnostic_pattern_verification import DiagnosticPatternVerification
from .diagnostic_patterns import DiagnosticPattern
from .gap import GapHypothesis, _digest


def pattern_to_gap(
    pattern: DiagnosticPattern,
    verification: DiagnosticPatternVerification,
) -> GapHypothesis:
    if pattern.pattern_id != verification.pattern_id:
        raise ValueError("pattern and verification identity mismatch")
    if not verification.eligible_for_gap:
        raise ValueError("diagnostic pattern is not eligible for gap detection")
    if not pattern.evidence_ids:
        raise ValueError("gap requires diagnostic evidence references")
    raw = {
        "pattern_id": pattern.pattern_id,
        "evidence_ids": pattern.evidence_ids,
        "signature": pattern.signature,
    }
    return GapHypothesis(
        gap_id="gap:" + _digest(raw)[:24],
        source_records=pattern.evidence_ids,
        trigger_kind="diagnostic_pattern",
        description=f"Repeated verified diagnostic pattern: {pattern.signature}",
        conditions=(
            "pattern_verified=true",
            f"independent_source_count={verification.independent_source_count}",
        ),
        counterevidence=verification.counterexample_refs,
    )
