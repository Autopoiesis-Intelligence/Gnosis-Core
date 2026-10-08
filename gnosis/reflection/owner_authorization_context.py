"""Mandatory execution-context binding for production owner authorization.

E8.163 keeps the existing E8.160 cryptographic verifier intact while adding
one safe entry point for production callers: every security-relevant binding
must be supplied as one immutable context object.
"""
from __future__ import annotations

from dataclasses import dataclass

from gnosis.reflection.owner_authorization import (
    ProductionAuthorization,
    TrustedIssuerKey,
    TrustedIssuerKeyResolver,
    verify_production_authorization,
)


@dataclass(frozen=True)
class OwnerAuthorizationExecutionContext:
    """Canonical expected execution bindings for an authorization."""

    now: int
    authority_scope: frozenset[str]
    policy_version: str
    evolution_identity: str
    parent_state_digest: str
    request_provenance: str


def verify_for_execution_context(
    authorization: ProductionAuthorization,
    resolver: TrustedIssuerKeyResolver,
    context: OwnerAuthorizationExecutionContext,
) -> TrustedIssuerKey:
    """Fail closed unless every execution binding matches the authorization."""
    return verify_production_authorization(
        authorization,
        resolver,
        now=context.now,
        expected_scope=set(context.authority_scope),
        expected_policy_version=context.policy_version,
        expected_evolution_identity=context.evolution_identity,
        expected_parent_state_digest=context.parent_state_digest,
        expected_request_provenance=context.request_provenance,
    )
