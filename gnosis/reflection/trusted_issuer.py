"""Fail-closed trusted owner-authority issuance contract.

The issuer is deliberately a pure boundary: it accepts an explicit root,
scope, policy and exact evolution binding, and emits an immutable
ExecutionAuthorization only when all bindings are exact. No clock, global
state, external selector or automatic approval is introduced here.
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
    policy_identity: object | None = None
    evidence_digest: str
    policy_identity: object | None = None


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
        if request.policy_identity is None or self.policy_identity != request.policy_identity:
            raise PermissionError("trusted issuer policy identity mismatch")
        if not request.evidence_digest:
            raise PermissionError("authorization evidence is missing")
        approval = request.approval
        if not approval.approval_id:
            raise PermissionError("approval identity is missing")
        if approval.request_provenance != request_provenance:
            raise PermissionError("owner approval does not match provenance")
        if approval.evolution_identity != evolution_identity:
            raise PermissionError("owner approval does not match evolution")
        return ExecutionAuthorization(
            request_provenance=request_provenance,
            owner_approved=True,
            evolution_identity=evolution_identity,
            approval_id=approval.approval_id,
            policy_identity=request.policy_identity,
        )
