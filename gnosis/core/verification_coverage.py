"""Verification adequacy: distinguish passing results from obligation coverage."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.core.types import _stable_hash

@dataclass(frozen=True)
class VerificationCoverage:
    rule_digest: str
    obligations: tuple[str, ...]
    checked_obligations: tuple[str, ...]

def coverage_digest(c: VerificationCoverage) -> str:
    return _stable_hash({
        "rule_digest": c.rule_digest,
        "obligations": c.obligations,
        "checked_obligations": c.checked_obligations,
    })

def verify_adequacy(c: VerificationCoverage, expected_digest: str) -> None:
    if coverage_digest(c) != expected_digest:
        raise ValueError("verification coverage digest mismatch")
    required=set(c.obligations)
    checked=set(c.checked_obligations)
    if not required.issubset(checked):
        missing=sorted(required-checked)
        raise ValueError(f"verification coverage incomplete: {missing}")
