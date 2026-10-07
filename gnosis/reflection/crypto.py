"""Isolated cryptographic primitives for the E8.53 authority audit.

This module does not issue execution authority and is not wired into the
production authorization path.
"""
from __future__ import annotations

import hashlib
import json
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

def generate_keypair() -> tuple[bytes, bytes]:
    private_key = Ed25519PrivateKey.generate()
    return private_key.private_bytes_raw(), private_key.public_key().public_bytes_raw()

def sign(private_key_bytes: bytes, payload: bytes) -> bytes:
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    return Ed25519PrivateKey.from_private_bytes(private_key_bytes).sign(payload)

def canonical_owner_authorization(payload: dict[str, object]) -> bytes:
    required = (
        "authority_root",
        "scope",
        "policy_version",
        "evidence_digest",
        "request_provenance",
        "evolution_identity",
        "approval_id",
    )
    if set(payload) != set(required):
        raise ValueError("OwnerAuthorizationV1 fields mismatch")
    encoded = json.dumps(
        {"version": "OwnerAuthorizationV1", **payload},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return b"GNOZIS-OWNER-AUTHORIZATION-V1\x00" + hashlib.sha256(encoded).digest()


def verify(public_key_bytes: bytes, payload: bytes, signature: bytes) -> bool:
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    try:
        Ed25519PublicKey.from_public_bytes(public_key_bytes).verify(signature, payload)
    except (InvalidSignature, ValueError):
        return False
    return True
