"""Explicit production trust dependencies for signed owner authorization.

Instances must be built by the production composition root from trusted
configuration. Never construct this context from request-controlled values.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from gnosis.reflection.authority import ExecutionCommitRequest
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.owner_authorization import (
    ProductionAuthorization,
    TrustedIssuerKey,
    TrustedIssuerKeyResolver,
    verify_production_authorization,
)


@dataclass(frozen=True)
class ProductionTrustContext:
    """Immutable references to externally provisioned trust dependencies."""

    issuer_key_resolver: TrustedIssuerKeyResolver
    authority_scope: frozenset[str]
    policy_version: str
    trusted_clock: Callable[[], int]

    def __post_init__(self) -> None:
        if not self.authority_scope or any(not item for item in self.authority_scope):
            raise ValueError("trusted authority scope must be non-empty")
        if not self.policy_version:
            raise ValueError("trusted policy version must be non-empty")
        if not callable(self.trusted_clock):
            raise ValueError("trusted clock is required")

    def verify_commit(
        self,
        authorization: ProductionAuthorization,
        request: ExecutionCommitRequest,
    ) -> TrustedIssuerKey:
        """Verify the signed grant against actual commit-request bindings."""
        now = self.trusted_clock()
        if not isinstance(now, int) or isinstance(now, bool):
            raise PermissionError("trusted clock did not return an integer timestamp")

        validity = request.authorization_validity
        if not isinstance(validity, AuthorizationValidity):
            raise PermissionError("authorization validity is required")
        if authorization.authorization_id != request.authorization.approval_id:
            raise PermissionError("signed authorization ID does not match commit request")
        if authorization.authorization_id != validity.authorization_id:
            raise PermissionError("signed authorization ID does not match validity record")
        if validity.policy_version != self.policy_version:
            raise PermissionError("authorization validity policy does not match trusted policy")

        return verify_production_authorization(
            authorization,
            self.issuer_key_resolver,
            now=now,
            expected_scope=set(self.authority_scope),
            expected_policy_version=self.policy_version,
            expected_evolution_identity=request.evolution_identity,
            expected_parent_state_digest=str(request.provenance.parent_state_digest),
            expected_request_provenance=request.request_provenance,
        )
