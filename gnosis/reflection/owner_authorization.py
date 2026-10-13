"""Production owner-authorization verification boundary.

This module verifies externally issued owner authorization. It does not issue
authority, store private keys, manage policy, or execute commits.

E8.160 contract:
- Ed25519 signatures
- canonical deterministic JSON, serialization version 1
- raw 32-byte public keys and raw 64-byte signatures, base64 encoded on wire
- exact issuer_id + key_version lookup
- fail-closed verification
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import binascii
import json
from typing import Protocol

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey


ALGORITHM = "Ed25519"
SERIALIZATION_VERSION = 1
ACTIVE = "active"
REVOKED = "revoked"
ROTATED = "rotated"


@dataclass(frozen=True)
class TrustedIssuerKey:
    """Trusted public verification material provisioned outside this module."""

    issuer_id: str
    key_version: str
    public_key: bytes
    status: str = ACTIVE
    valid_from: int | None = None
    expires_at: int | None = None

    def __post_init__(self) -> None:
        if not self.issuer_id or not self.key_version:
            raise ValueError("trusted issuer key requires issuer_id and key_version")
        if len(self.public_key) != 32:
            raise ValueError("Ed25519 public key must be exactly 32 bytes")
        if self.status not in {ACTIVE, REVOKED, ROTATED}:
            raise ValueError("unknown trusted issuer key status")


class TrustedIssuerKeyResolver(Protocol):
    """Resolve exactly the issuer/key version named by an authorization."""

    def resolve(self, issuer_id: str, key_version: str) -> TrustedIssuerKey | None:
        ...


@dataclass(frozen=True)
class ProductionAuthorization:
    """Externally signed owner authorization; never an execution capability."""

    authorization_id: str
    issuer_id: str
    key_version: str
    authority_scope: tuple[str, ...]
    policy_version: str
    evolution_identity: str
    parent_state_digest: str
    request_provenance: str
    valid_from: int
    expires_at: int
    nonce: str
    signature: str

    def payload(self) -> dict[str, object]:
        return {
            "algorithm": ALGORITHM,
            "serialization_version": SERIALIZATION_VERSION,
            "authorization_id": self.authorization_id,
            "issuer_id": self.issuer_id,
            "key_version": self.key_version,
            "authority_scope": list(self.authority_scope),
            "policy_version": self.policy_version,
            "evolution_identity": self.evolution_identity,
            "parent_state_digest": self.parent_state_digest,
            "request_provenance": self.request_provenance,
            "valid_from": self.valid_from,
            "expires_at": self.expires_at,
            "nonce": self.nonce,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_authorization_bytes(self.payload())


def canonical_authorization_bytes(payload: dict[str, object]) -> bytes:
    """Serialize the version-1 authorization payload deterministically."""
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _decode_b64(value: str, *, label: str) -> bytes:
    if not value:
        raise PermissionError(f"{label} is missing")
    try:
        decoded = base64.b64decode(value.encode("ascii"), validate=True)
    except (ValueError, UnicodeEncodeError, binascii.Error) as exc:
        raise PermissionError(f"{label} encoding is invalid") from exc
    return decoded


def verify_production_authorization(
    authorization: ProductionAuthorization,
    resolver: TrustedIssuerKeyResolver,
    *,
    now: int,
    expected_scope: set[str] | None = None,
    expected_policy_version: str | None = None,
    expected_evolution_identity: str | None = None,
    expected_parent_state_digest: str | None = None,
    expected_request_provenance: str | None = None,
) -> TrustedIssuerKey:
    """Verify an external owner authorization and return its trusted key.

    This function establishes cryptographic/binding validity only. It does not
    create ExecutionAuthorization and does not consume a nonce.
    """
    if not authorization.authorization_id:
        raise PermissionError("authorization identity is missing")
    if not authorization.issuer_id or not authorization.key_version:
        raise PermissionError("issuer identity is missing")
    if not authorization.policy_version:
        raise PermissionError("policy version is missing")
    if not authorization.evolution_identity:
        raise PermissionError("evolution identity is missing")
    if not authorization.parent_state_digest:
        raise PermissionError("parent state digest is missing")
    if not authorization.request_provenance:
        raise PermissionError("request provenance is missing")
    if not authorization.nonce:
        raise PermissionError("authorization nonce is missing")
    if authorization.valid_from >= authorization.expires_at:
        raise PermissionError("authorization validity interval is invalid")
    if now < authorization.valid_from or now >= authorization.expires_at:
        raise PermissionError("authorization is outside its validity interval")

    if expected_scope is not None and set(authorization.authority_scope) != expected_scope:
        raise PermissionError("authorization scope mismatch")
    if expected_policy_version is not None and authorization.policy_version != expected_policy_version:
        raise PermissionError("authorization policy mismatch")
    if expected_evolution_identity is not None and authorization.evolution_identity != expected_evolution_identity:
        raise PermissionError("authorization evolution mismatch")
    if expected_parent_state_digest is not None and authorization.parent_state_digest != expected_parent_state_digest:
        raise PermissionError("authorization parent-state mismatch")
    if expected_request_provenance is not None and authorization.request_provenance != expected_request_provenance:
        raise PermissionError("authorization request-provenance mismatch")

    key = resolver.resolve(authorization.issuer_id, authorization.key_version)
    if key is None:
        raise PermissionError("trusted issuer key not found")
    if key.issuer_id != authorization.issuer_id or key.key_version != authorization.key_version:
        raise PermissionError("trusted issuer key identity mismatch")
    if key.status != ACTIVE:
        raise PermissionError("trusted issuer key is not active")
    if key.valid_from is not None and now < key.valid_from:
        raise PermissionError("trusted issuer key is not yet valid")
    if key.expires_at is not None and now >= key.expires_at:
        raise PermissionError("trusted issuer key is expired")

    signature = _decode_b64(authorization.signature, label="authorization signature")
    if len(signature) != 64:
        raise PermissionError("Ed25519 signature must be exactly 64 bytes")

    try:
        VerifyKey(key.public_key).verify(authorization.canonical_bytes(), signature)
    except (BadSignatureError, ValueError) as exc:
        raise PermissionError("authorization signature verification failed") from exc

    return key
