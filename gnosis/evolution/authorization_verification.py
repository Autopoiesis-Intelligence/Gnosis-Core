"""Fail-closed staleness verification for commit authorization."""
from __future__ import annotations
from dataclasses import dataclass
from .commit_authorization import DirectoryCommitAuthorization
from .directory_provenance import canonical_digest

@dataclass(frozen=True)
class AuthorizationVerification:
    valid: bool
    reasons: tuple[str, ...]

def verify_authorization_freshness(
    authorization: DirectoryCommitAuthorization,
    *,
    current_candidate_id: str,
    current_candidate_binding_digest: str,
    current_provenance_id: str,
    current_evidence_digest: str,
    current_decision_digest: str,
) -> AuthorizationVerification:
    reasons: list[str] = []
    if not authorization.verify():
        reasons.append("authorization integrity verification failed")
    if authorization.candidate_id != current_candidate_id:
        reasons.append("stale candidate identity")
    if authorization.candidate_binding_digest != current_candidate_binding_digest:
        reasons.append("stale candidate binding")
    if authorization.provenance_id != current_provenance_id:
        reasons.append("stale provenance identity")
    if authorization.evidence_digest != current_evidence_digest:
        reasons.append("stale evidence identity")
    if authorization.decision_digest != current_decision_digest:
        reasons.append("stale decision identity")
    return AuthorizationVerification(not reasons, tuple(dict.fromkeys(reasons)))
