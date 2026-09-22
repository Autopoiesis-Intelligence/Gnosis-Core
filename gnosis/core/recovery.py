"""Core recovery contract, independent of SQLite."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence
from .chain_verifier import ChainVerification

@dataclass(frozen=True)
class RecoveryEvidence:
    provenance: Mapping[str, Any]
    audit_rows: Sequence[Mapping[str, Any]]
    observations: Mapping[str, Any]
    proposed_state_content_id: str

@dataclass(frozen=True)
class RecoveryReport:
    recovered_records: int
    chain_valid: bool
    replay_valid: bool
    expected_digest: str | None
    actual_digest: str | None
    reasons: tuple[str, ...]

class RecoveryPort(Protocol):
    def load_recovery_evidence(self, provenance_id: str) -> RecoveryEvidence: ...

def verify_recovery(evidence: RecoveryEvidence, verifier) -> RecoveryReport:
    result: ChainVerification = verifier(
        evidence.provenance, evidence.audit_rows, observations=evidence.observations
    )
    expected=evidence.provenance.get("evidence_digest")
    actual=evidence.provenance.get("replayed_evidence_digest")
    reasons=list(result.reasons)
    if expected is not None and actual is not None and expected != actual:
        reasons.append("recovery replay digest mismatch")
    if evidence.proposed_state_content_id != evidence.provenance.get("proposed_state_content_id",""):
        reasons.append("proposed state content identity mismatch")
    return RecoveryReport(
        len(evidence.audit_rows), result.valid, result.valid and not reasons,
        expected, actual, tuple(dict.fromkeys(reasons)),
    )
