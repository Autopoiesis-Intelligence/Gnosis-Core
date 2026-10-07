"""Verification of owner authorization against deployment trust."""

from __future__ import annotations

from gnosis.reflection.owner_authorization import OwnerAuthorizationV1
from gnosis.reflection.owner_trust import OwnerTrustAnchor


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
