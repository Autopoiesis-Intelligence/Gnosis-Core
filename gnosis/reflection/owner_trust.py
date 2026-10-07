"""Production-facing cryptographic trust-anchor primitive.

This module establishes only cryptographic trust in a configured owner issuer.
It does not establish scope, policy authority, evolution authorization, or
execution authority. Those remain separate boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


@dataclass(frozen=True)
class OwnerTrustAnchor:
    """Immutable trust anchor for one explicitly configured Ed25519 issuer."""

    issuer_id: str
    key_id: str
    public_key: bytes

    def __post_init__(self) -> None:
        if not self.issuer_id:
            raise ValueError("issuer_id is required")
        if not self.key_id:
            raise ValueError("key_id is required")
        if len(self.public_key) != 32:
            raise ValueError("Ed25519 public key must be 32 bytes")

    def verify(
        self,
        canonical_payload: bytes,
        signature: bytes,
        *,
        issuer_id: str,
        key_id: str,
    ) -> bool:
        """Return True only for a valid signature from this configured issuer/key."""
        if issuer_id != self.issuer_id or key_id != self.key_id:
            return False
        if not isinstance(canonical_payload, bytes) or not isinstance(signature, bytes):
            return False
        try:
            Ed25519PublicKey.from_public_bytes(self.public_key).verify(
                signature,
                canonical_payload,
            )
        except (InvalidSignature, ValueError, TypeError):
            return False
        return True
