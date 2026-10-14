"""Explicit production trust dependencies for signed owner authorization.

Instances must be built by a protected production composition root, never from
request-controlled values. The current repository has not yet proven that root.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from gnosis.reflection.authority import ExecutionCommitRequest
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.owner_authorization import ProductionAuthorization, TrustedIssuerKey, TrustedIssuerKeyResolver, verify_production_authorization


@dataclass(frozen=True)
class ProductionTrustContext:
    issuer_key_resolver: TrustedIssuerKeyResolver
    authority_scope: frozenset[str]
    policy_version: str
    trusted_clock: Callable[[], int]
    validity_evidence_digest_resolver: Callable[[str], str | None]

    def __post_init__(self) -> None:
        if not self.authority_scope or any(not item for item in self.authority_scope):
            raise ValueError("trusted authority scope must be non-empty")
        if not self.policy_version or not callable(self.trusted_clock) or not callable(self.validity_evidence_digest_resolver):
            raise ValueError("trusted policy, clock and evidence resolver are required")

    def resolve_validity_evidence_digest(self, authorization_id: str) -> str:
        if not authorization_id:
            raise PermissionError("authorization identity is missing")
        digest = self.validity_evidence_digest_resolver(authorization_id)
        if not isinstance(digest, str) or not digest:
            raise PermissionError("trusted authorization validity evidence is missing")
        return digest

    def verify_commit(self, authorization: ProductionAuthorization, request: ExecutionCommitRequest, *, expected_evidence_digest: str | None = None) -> TrustedIssuerKey:
        now = self.trusted_clock()
        if not isinstance(now, int) or isinstance(now, bool):
            raise PermissionError("trusted clock did not return an integer timestamp")
        validity = request.authorization_validity
        if not isinstance(validity, AuthorizationValidity):
            raise PermissionError("authorization validity is required")
        if authorization.authorization_id != request.authorization.approval_id or authorization.authorization_id != validity.authorization_id:
            raise PermissionError("signed authorization ID does not match commit request")
        if validity.policy_version != self.policy_version:
            raise PermissionError("authorization validity policy does not match trusted policy")
        if expected_evidence_digest is None:
            expected_evidence_digest = self.resolve_validity_evidence_digest(validity.authorization_id)
        validity.require_valid(expected_policy_version=self.policy_version, expected_evidence_digest=expected_evidence_digest)
        return verify_production_authorization(
            authorization, self.issuer_key_resolver, now=now,
            expected_scope=set(self.authority_scope), expected_policy_version=self.policy_version,
            expected_evolution_identity=request.evolution_identity,
            expected_parent_state_digest=str(request.provenance.parent_state_digest),
            expected_request_provenance=request.request_provenance,
        )
