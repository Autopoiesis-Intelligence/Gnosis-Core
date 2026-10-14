"""Production owner-authorization verification boundary.

This module verifies externally issued owner authorization. It does not issue
authority, store private keys, manage policy, or execute commits.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import binascii
import hashlib
import json
from typing import Protocol

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

DOMAIN = "gnosis-core:owner-authorization:v1"
ALGORITHM = "Ed25519"
SERIALIZATION_VERSION = 1
ACTIVE = "active"
REVOKED = "revoked"
ROTATED = "rotated"


@dataclass(frozen=True)
class TrustedIssuerKey:
    """Public verification material provisioned outside Core."""
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
        if self.valid_from is not None and self.expires_at is not None and self.valid_from >= self.expires_at:
            raise ValueError("trusted issuer key validity interval is invalid")


class TrustedIssuerKeyResolver(Protocol):
    """Resolve trusted public keys provisioned by a protected authority boundary."""
    def resolve(self, issuer_id: str, key_version: str) -> TrustedIssuerKey | None: ...


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
    proposal_binding_digest: str
    signature: str

    def payload(self) -> dict[str, object]:
        return {
            "domain": DOMAIN, "algorithm": ALGORITHM,
            "serialization_version": SERIALIZATION_VERSION,
            "authorization_id": self.authorization_id, "issuer_id": self.issuer_id,
            "key_version": self.key_version, "authority_scope": list(self.authority_scope),
            "policy_version": self.policy_version, "evolution_identity": self.evolution_identity,
            "parent_state_digest": self.parent_state_digest,
            "request_provenance": self.request_provenance, "valid_from": self.valid_from,
            "expires_at": self.expires_at, "nonce": self.nonce,
            "proposal_binding_digest": self.proposal_binding_digest,
        }

    def identity_payload(self) -> dict[str, object]:
        payload = self.payload()
        payload.pop("authorization_id")
        return payload

    def expected_authorization_id(self) -> str:
        digest = hashlib.sha256(canonical_authorization_bytes(self.identity_payload())).hexdigest()
        return "auth:" + digest[:32]

    def canonical_bytes(self) -> bytes:
        return canonical_authorization_bytes(self.payload())


def canonical_authorization_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _decode_b64(value: str, *, label: str) -> bytes:
    if not value:
        raise PermissionError(f"{label} is missing")
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (ValueError, UnicodeEncodeError, binascii.Error) as exc:
        raise PermissionError(f"{label} encoding is invalid") from exc


def verify_production_authorization(
    authorization: ProductionAuthorization,
    resolver: TrustedIssuerKeyResolver,
    *,
    now: int,
    expected_scope: set[str],
    expected_policy_version: str,
    expected_evolution_identity: str,
    expected_parent_state_digest: str,
    expected_request_provenance: str,
    expected_proposal_binding_digest: str,
) -> TrustedIssuerKey:
    """Verify signature and request bindings; replay consumption is separate."""
    if not expected_scope or not all((expected_policy_version, expected_evolution_identity, expected_parent_state_digest, expected_request_provenance, expected_proposal_binding_digest)):
        raise PermissionError("trusted execution binding is incomplete")
    if not authorization.authorization_id or not authorization.issuer_id or not authorization.key_version:
        raise PermissionError("authorization identity is missing")
    if not all((authorization.policy_version, authorization.evolution_identity, authorization.parent_state_digest, authorization.request_provenance, authorization.nonce, authorization.authority_scope, authorization.proposal_binding_digest)):
        raise PermissionError("authorization binding is incomplete")
    if tuple(sorted(set(authorization.authority_scope))) != authorization.authority_scope:
        raise PermissionError("authorization scope is not canonical")
    if authorization.authorization_id != authorization.expected_authorization_id():
        raise PermissionError("authorization identity mismatch")
    if authorization.valid_from >= authorization.expires_at or now < authorization.valid_from or now >= authorization.expires_at:
        raise PermissionError("authorization is outside its validity interval")
    if set(authorization.authority_scope) != expected_scope:
        raise PermissionError("authorization scope mismatch")
    if authorization.policy_version != expected_policy_version:
        raise PermissionError("authorization policy mismatch")
    if authorization.evolution_identity != expected_evolution_identity:
        raise PermissionError("authorization evolution mismatch")
    if authorization.parent_state_digest != expected_parent_state_digest:
        raise PermissionError("authorization parent-state mismatch")
    if authorization.request_provenance != expected_request_provenance:
        raise PermissionError("authorization request-provenance mismatch")
    if authorization.proposal_binding_digest != expected_proposal_binding_digest:
        raise PermissionError("authorization proposal-binding mismatch")
    key = resolver.resolve(authorization.issuer_id, authorization.key_version)
    if key is None or key.issuer_id != authorization.issuer_id or key.key_version != authorization.key_version:
        raise PermissionError("trusted issuer key not found or identity mismatch")
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
