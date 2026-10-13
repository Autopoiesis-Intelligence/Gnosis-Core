"""Fail-closed trusted owner-authority issuance contract.

OwnerApproval is caller-constructible data, not proof of owner identity.
Until a trusted-key signature verifier is wired into this path, this module
must not convert an approval-shaped object into executable authority.
"""
from __future__ import annotations

from dataclasses import dataclass

from gnosis.reflection.authority import ExecutionAuthorization, OwnerApproval


@dataclass(frozen=True)
class TrustedIssuerInput:
    approval: OwnerApproval
    authority_root: str
    scope: str
    policy_version: str
    evidence_digest: str


@dataclass(frozen=True)
class TrustedOwnerIssuer:
    authority_root: str
    scope: str
    policy_version: str

    def issue(
        self,
        request: TrustedIssuerInput,
        *,
        request_provenance: str,
        evolution_identity: str,
    ) -> ExecutionAuthorization:
        """Reject unsigned approvals; never elevate caller-supplied fields.

        This intentionally remains unavailable until signature authenticity,
        trusted-key status/version, signed-field binding, and validity checks
        are implemented and integrated with the existing execution gate.
        """
        # Retain cheap binding checks for clear, deterministic failures. These
        # checks are not authentication and never suffice to issue authority.
        if not self.authority_root or not self.scope or not self.policy_version:
            raise PermissionError("trusted issuer configuration is incomplete")
        if request.authority_root != self.authority_root:
            raise PermissionError("authority root mismatch")
        if request.scope != self.scope:
            raise PermissionError("authorization scope mismatch")
        if request.policy_version != self.policy_version:
            raise PermissionError("authorization policy mismatch")
        if not request.evidence_digest:
            raise PermissionError("authorization evidence is missing")
        approval = request.approval
        if not approval.approval_id:
            raise PermissionError("approval identity is missing")
        if approval.request_provenance != request_provenance:
            raise PermissionError("owner approval does not match provenance")
        if approval.evolution_identity != evolution_identity:
            raise PermissionError("owner approval does not match evolution")

        raise PermissionError(
            "unsigned OwnerApproval is not trusted; cryptographic owner "
            "verification is not implemented"
        )
