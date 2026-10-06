"""Minimal public-key signature verification boundary."""

from __future__ import annotations

from typing import Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class SignatureVerifier(Protocol):
    """Port for verifying a signature over exact canonical message bytes."""

    def verify(
        self,
        *,
        public_key: bytes,
        message: bytes,
        signature: bytes,
    ) -> bool:
        """Return True only when the signature verifies."""


class Ed25519SignatureVerifier:
    """Ed25519 verification adapter backed by cryptography."""

    def verify(
        self,
        *,
        public_key: bytes,
        message: bytes,
        signature: bytes,
    ) -> bool:
        """Verify raw Ed25519 public-key/signature bytes.

        Malformed inputs and invalid signatures fail closed. The adapter never
        accepts text encodings implicitly and never handles private keys.
        """
        if not isinstance(public_key, bytes):
            return False
        if not isinstance(message, bytes):
            return False
        if not isinstance(signature, bytes):
            return False

        try:
            key = Ed25519PublicKey.from_public_bytes(public_key)
            key.verify(signature, message)
        except (InvalidSignature, ValueError, TypeError):
            return False

        return True
