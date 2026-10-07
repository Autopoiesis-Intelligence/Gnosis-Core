"""Minimal public-key signature verification boundary."""

from __future__ import annotations

from typing import Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class SignatureVerifier(Protocol):
    def verify(self, *, public_key: bytes, message: bytes, signature: bytes) -> bool:
        ...


class Ed25519SignatureVerifier:
    def verify(self, *, public_key: bytes, message: bytes, signature: bytes) -> bool:
        if not isinstance(public_key, bytes) or not isinstance(message, bytes) or not isinstance(signature, bytes):
            return False
        try:
            Ed25519PublicKey.from_public_bytes(public_key).verify(signature, message)
        except (InvalidSignature, ValueError, TypeError):
            return False
        return True
