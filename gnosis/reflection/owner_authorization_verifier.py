"""Verification of owner authorization against deployment trust."""

from __future__ import annotations

from gnosis.reflection.owner_authorization import OwnerAuthorizationV1
from gnosis.reflection.owner_trust import OwnerTrustAnchor
from gnosis.reflection.trusted_issuer import TrustedOwnerIssuer


def verify_owner_authorization(
    authorization: OwnerAuthorizationV1,
    *,
    trust_anchor: OwnerTrustAnchor | None = None,
) -> bool:
    """Verify owner identity binding and signature; never authorize execution."""
    if not isinstance(authorization, OwnerAuthorizationV1):
        return False
    anchor = trust_anchor if trust_anchor is not None else OwnerTrustAnchor.from_environment()
    if anchor is None:
        return False
    if not anchor.matches(owner_id=authorization.owner_id, key_id=authorization.key_id):
        return False
    return authorization.verify_signature(anchor.public_key)


def verify_owner_authorization_scope(
    authorization: OwnerAuthorizationV1,
    *,
    expected_scope: str,
    trust_anchor: OwnerTrustAnchor | None = None,
) -> bool:
    """Verify owner authorization and bind it to an independent expected scope."""
    if not expected_scope or authorization.scope != expected_scope:
        return False
    return verify_owner_authorization(authorization, trust_anchor=trust_anchor)


def verify_owner_authorization_request(
    authorization: OwnerAuthorizationV1,
    *,
    expected_request_provenance: str,
    trust_anchor: OwnerTrustAnchor | None = None,
) -> bool:
    """Verify owner authorization and bind it to the current request provenance."""
    if not expected_request_provenance or authorization.request_provenance != expected_request_provenance:
        return False
    return verify_owner_authorization(authorization, trust_anchor=trust_anchor)


def verify_owner_authorization_evolution(
    authorization: OwnerAuthorizationV1,
    *,
    expected_evolution_identity: str,
    trust_anchor: OwnerTrustAnchor | None = None,
) -> bool:
    """Verify owner authorization and bind it to the current evolution identity."""
    if not expected_evolution_identity or authorization.evolution_identity != expected_evolution_identity:
        return False
    return verify_owner_authorization(authorization, trust_anchor=trust_anchor)


def verify_owner_authorization_policy(
    authorization: OwnerAuthorizationV1,
    *,
    expected_policy_version: str,
    expected_policy_binding_digest: str,
    trust_anchor: OwnerTrustAnchor | None = None,
) -> bool:
    """Verify owner authorization against independently expected policy identity."""
    if not expected_policy_version or not expected_policy_binding_digest:
        return False
    if authorization.policy_version != expected_policy_version:
        return False
    if authorization.policy_binding_digest != expected_policy_binding_digest:
        return False
    return verify_owner_authorization(authorization, trust_anchor=trust_anchor)


def verify_owner_authorization_for_issuer(
    authorization: OwnerAuthorizationV1,
    *,
    issuer: TrustedOwnerIssuer,
    trust_anchor: OwnerTrustAnchor | None = None,
) -> bool:
    """Verify owner authorization against the issuer's configured scope."""
    return verify_owner_authorization_scope(
        authorization,
        expected_scope=issuer.scope,
        trust_anchor=trust_anchor,
    )
