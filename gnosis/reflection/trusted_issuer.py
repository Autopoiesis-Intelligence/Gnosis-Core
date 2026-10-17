"""Fail-closed trusted owner-authority issuance contract.

This issuer validates request bindings but does not verify cryptographic owner
proof. It therefore never grants executable authorization. Production issuance
must be integrated through a trusted verifier and protected composition root.
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

    def issue(self, request: TrustedIssuerInput, *, request_provenance: str, evolution_identity: str) -> ExecutionAuthorization:
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

        # OwnerApproval is a caller-constructible data object, not proof of
        # authority. Until a trusted cryptographic verifier is composed here,
        # matching strings must never produce owner_approved=True.
        raise PermissionError(
            "cryptographic owner proof is not verified; authorization issuance is disabled"
        )
