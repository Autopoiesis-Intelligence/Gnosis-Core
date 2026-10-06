"""Explicit, deterministic authorization validity and revocation contract."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.core.policy import PolicyIdentity

@dataclass(frozen=True)
class AuthorizationValidity:
    authorization_id: str
    policy_version: str
    validity_evidence_digest: str
    revoked: bool = False
    policy_identity: PolicyIdentity | None = None

    def require_valid(self, *, expected_policy_version: str, expected_evidence_digest: str, expected_policy_identity: PolicyIdentity | None = None) -> None:
        if not self.authorization_id:
            raise PermissionError("authorization identity is missing")
        if self.revoked:
            raise PermissionError("execution authorization revoked")
        if self.policy_version != expected_policy_version:
            raise PermissionError("authorization policy mismatch")
        if self.validity_evidence_digest != expected_evidence_digest:
            raise PermissionError("authorization validity evidence mismatch")
        if expected_policy_identity is not None and self.policy_identity != expected_policy_identity:
            raise PermissionError("authorization evaluated policy mismatch")
