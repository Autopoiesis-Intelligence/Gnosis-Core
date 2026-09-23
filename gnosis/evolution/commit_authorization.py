"""Immutable, evidence-bound commit authorization value object."""
from __future__ import annotations
from dataclasses import dataclass
from .directory_provenance import canonical_digest

@dataclass(frozen=True)
class DirectoryCommitAuthorization:
    candidate_id: str
    candidate_binding_digest: str
    provenance_id: str
    evidence_digest: str
    decision_digest: str
    governance_decision: str
    shadow_accepted: bool
    authorization_digest: str

    @classmethod
    def issue(cls, *, candidate_id: str, candidate_binding_digest: str, provenance_id: str,
              evidence_digest: str, decision_digest: str, governance_decision: str,
              shadow_accepted: bool) -> "DirectoryCommitAuthorization":
        payload = {
            "candidate_id": candidate_id,
            "candidate_binding_digest": candidate_binding_digest,
            "provenance_id": provenance_id,
            "evidence_digest": evidence_digest,
            "decision_digest": decision_digest,
            "governance_decision": governance_decision,
            "shadow_accepted": shadow_accepted,
        }
        return cls(**payload, authorization_digest=canonical_digest(payload))

    def verify(self) -> bool:
        payload = {
            "candidate_id": self.candidate_id,
            "candidate_binding_digest": self.candidate_binding_digest,
            "provenance_id": self.provenance_id,
            "evidence_digest": self.evidence_digest,
            "decision_digest": self.decision_digest,
            "governance_decision": self.governance_decision,
            "shadow_accepted": self.shadow_accepted,
        }
        return self.authorization_digest == canonical_digest(payload)
