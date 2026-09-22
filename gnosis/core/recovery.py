"""Immutable evidence bundle required for trusted recovery."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

@dataclass(frozen=True)
class RecoveryEvidence:
    provenance: Mapping[str, Any]
    audit_rows: tuple[Mapping[str, Any], ...]
    observations: Mapping[str, Any]
    proposed_state_content_id: str
    transition_id: str
    evidence_digest: str
    replayed_evidence_digest: str

    def validate(self) -> None:
        if not self.provenance: raise ValueError("provenance evidence required")
        if not self.audit_rows: raise ValueError("audit evidence required")
        required=(self.proposed_state_content_id,self.transition_id,self.evidence_digest,self.replayed_evidence_digest)
        if any(not value for value in required): raise ValueError("recovery evidence contains empty identity")
        persisted=self.provenance.get("evidence_digest")
        if persisted != self.evidence_digest: raise ValueError("recovery evidence digest mismatch")
        if self.provenance.get("proposed_state_content_id","") != self.proposed_state_content_id:
            raise ValueError("proposed state content identity mismatch")

@dataclass(frozen=True)
class RecoveryReport:
    recovered_records: int
    chain_valid: bool
    replay_valid: bool
    expected_digest: str | None
    actual_digest: str | None
    reasons: tuple[str, ...]

class RecoveryPort:
    def load_recovery_evidence(self, provenance_id: str) -> RecoveryEvidence:
        raise NotImplementedError

def verify_recovery(evidence: RecoveryEvidence, verifier) -> RecoveryReport:
    try: evidence.validate()
    except ValueError as exc:
        return RecoveryReport(len(evidence.audit_rows),False,False,None,None,(str(exc),))
    result=verifier(evidence.provenance,evidence.audit_rows,observations=evidence.observations)
    reasons=list(result.reasons)
    if evidence.evidence_digest != evidence.replayed_evidence_digest:
        reasons.append("recovery replay digest mismatch")
    return RecoveryReport(len(evidence.audit_rows),result.valid,result.valid and not reasons,
                          evidence.evidence_digest,evidence.replayed_evidence_digest,
                          tuple(dict.fromkeys(reasons)))
