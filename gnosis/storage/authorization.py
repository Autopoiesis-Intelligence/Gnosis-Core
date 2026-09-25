"""Deterministic recovery-authorization validation.

This module defines the data contract only. It does not grant authority;
callers must supply an authorization decision from the governance boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal


class AuthorizationError(ValueError):
    """Raised when recovery authorization cannot be accepted."""


@dataclass(frozen=True)
class RecoveryAuthorization:
    authorization_id: str
    subject: str
    requested_by: str
    authority: str
    decision: Literal["allow", "deny"]
    reason: str
    issued_at: str
    expires_at: str | None
    evidence_digest: str

    def canonical_bytes(self) -> bytes:
        fields = (
            self.authorization_id,
            self.subject,
            self.requested_by,
            self.authority,
            self.decision,
            self.reason,
            self.issued_at,
            self.expires_at or "",
            self.evidence_digest,
        )
        return "\x1f".join(fields).encode("utf-8")

    @property
    def authorization_digest(self) -> str:
        return sha256(self.canonical_bytes()).hexdigest()


def validate_recovery_authorization(
    authorization: RecoveryAuthorization | None,
    *,
    subject: str,
    evidence_digest: str,
    now: str,
) -> None:
    if authorization is None:
        raise AuthorizationError("recovery authorization required")
    if authorization.decision != "allow":
        raise AuthorizationError("recovery authorization denied")
    if authorization.subject != subject:
        raise AuthorizationError("recovery authorization subject mismatch")
    if authorization.evidence_digest != evidence_digest:
        raise AuthorizationError("recovery authorization evidence mismatch")
    if authorization.expires_at is not None and now >= authorization.expires_at:
        raise AuthorizationError("recovery authorization expired")
    if not authorization.authorization_id or not authorization.requested_by:
        raise AuthorizationError("recovery authorization identity missing")
    if not authorization.authority:
        raise AuthorizationError("recovery authorization authority missing")
