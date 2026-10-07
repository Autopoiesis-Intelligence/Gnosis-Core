"""Fail-closed trusted owner-authority issuance contract.

The issuer verifies externally signed OwnerAuthorization V1 evidence before
emitting ExecutionAuthorization. It does not create authority or hold a
private key.
"""
from __future__ import annotations

from dataclasses import dataclass

from gnosis.reflection.authority import ExecutionAuthorization, OwnerApproval
from gnosis.reflection.owner_authorization import OwnerAuthorizationV1


@dataclass(frozen=True)
class TrustedIssuerInput:
    approval: OwnerApproval
    authorization: OwnerAuthorizationV1
    authority_root: str
    scope: str
    policy_version: str
    evidence_digest: str


@dataclass(frozen=True)
class TrustedOwnerIssuer:
    authority_root: str
    scope: str
    policy_version: str
    issuer_id: str
    key_version: str
    public_key: bytes

    def issue(
        self,
        request: TrustedIssuerInput,
        *,
        request_provenance: str,
        evolution_identity: str,
    ) -> ExecutionAuthorization:
        if (
            not self.authority_root
            or not self.scope
            or not self.policy_version
            or not self.issuer_id
            or not self.key_version
            or not self.public_key
        ):
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
        authorization = request.authorization

        if not approval.approval_id:
            raise PermissionError("approval identity is missing")
        if approval.request_provenance != request_provenance:
            raise PermissionError("owner approval does not match provenance")
        if approval.evolution_identity != evolution_identity:
            raise PermissionError("owner approval does not match evolution")

        if authorization.issuer_id != self.issuer_id:
            raise PermissionError("owner authorization issuer mismatch")
        if authorization.key_version != self.key_version:
            raise PermissionError("owner authorization key version mismatch")
        if authorization.authority_root != self.authority_root:
            raise PermissionError("owner authorization authority root mismatch")
        if authorization.scope != self.scope:
            raise PermissionError("owner authorization scope mismatch")
        if authorization.policy_version != self.policy_version:
            raise PermissionError("owner authorization policy mismatch")
        if authorization.request_provenance != request_provenance:
            raise PermissionError("owner authorization provenance mismatch")
        if authorization.evolution_identity != evolution_identity:
            raise PermissionError("owner authorization evolution mismatch")
        if authorization.evidence_digest != request.evidence_digest:
            raise PermissionError("owner authorization evidence mismatch")
        if authorization.authorization_id != approval.approval_id:
            raise PermissionError("owner authorization does not match approval")

        if not authorization.verify_signature(self.public_key):
            raise PermissionError("owner authorization signature invalid")

        return ExecutionAuthorization(
            request_provenance=request_provenance,
            owner_approved=True,
            evolution_identity=evolution_identity,
            approval_id=approval.approval_id,
        )
