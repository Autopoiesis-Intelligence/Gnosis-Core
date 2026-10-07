"""Cryptographic verification for externally issued owner authorization.

This module is deliberately verifier-only. It does not create authority,
store private keys, choose a trust root, or issue execution authorization.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


DOMAIN = "GNOZIS-OWNER-AUTHORIZATION-V1"

_FIELDS = {
    "issuer_id", "key_version", "authority_root", "scope", "policy_version",
    "request_provenance", "evolution_identity", "parent_state_digest",
    "evidence_digest", "authorization_id", "nonce", "valid_from", "valid_until",
}


def canonical_payload(fields: dict[str, str]) -> bytes:
    """Produce deterministic, domain-separated signed bytes."""
    if set(fields) != _FIELDS:
        raise ValueError("owner authorization field set is incomplete or contains unknown fields")
    if any(not isinstance(value, str) or not value for value in fields.values()):
        raise ValueError("owner authorization fields must be non-empty strings")
    document = {"domain": DOMAIN, "version": "1", **fields}
    return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def authorization_id_for(fields: dict[str, str]) -> str:
    """Derive identity from all authorization fields except the identity itself."""
    unsigned = {key: value for key, value in fields.items() if key != "authorization_id"}
    return "sha256:" + sha256(canonical_payload({**unsigned, "authorization_id": "identity-excluded"})).hexdigest()


@dataclass(frozen=True)
class OwnerAuthorizationV1:
    issuer_id: str
    key_version: str
    authority_root: str
    scope: str
    policy_version: str
    request_provenance: str
    evolution_identity: str
    parent_state_digest: str
    evidence_digest: str
    authorization_id: str
    nonce: str
    valid_from: str
    valid_until: str
    signature: bytes

    @property
    def canonical_payload(self) -> bytes:
        return canonical_payload({
            "issuer_id": self.issuer_id, "key_version": self.key_version,
            "authority_root": self.authority_root, "scope": self.scope,
            "policy_version": self.policy_version, "request_provenance": self.request_provenance,
            "evolution_identity": self.evolution_identity, "parent_state_digest": self.parent_state_digest,
            "evidence_digest": self.evidence_digest, "authorization_id": self.authorization_id,
            "nonce": self.nonce, "valid_from": self.valid_from, "valid_until": self.valid_until,
        })

    @property
    def computed_authorization_id(self) -> str:
        return authorization_id_for({
            "issuer_id": self.issuer_id, "key_version": self.key_version,
            "authority_root": self.authority_root, "scope": self.scope,
            "policy_version": self.policy_version, "request_provenance": self.request_provenance,
            "evolution_identity": self.evolution_identity, "parent_state_digest": self.parent_state_digest,
            "evidence_digest": self.evidence_digest, "authorization_id": "",
            "nonce": self.nonce, "valid_from": self.valid_from, "valid_until": self.valid_until,
        })

    def is_valid_at(self, now: datetime) -> bool:
        """Check the signed validity window using a timezone-aware instant."""
        if now.tzinfo is None:
            raise ValueError("validity checks require a timezone-aware datetime")
        try:
            start = datetime.fromisoformat(self.valid_from.replace("Z", "+00:00"))
            end = datetime.fromisoformat(self.valid_until.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("authorization validity timestamps are invalid") from exc
        if start.tzinfo is None or end.tzinfo is None or end <= start:
            raise ValueError("authorization validity window is invalid")
        current = now.astimezone(timezone.utc)
        return start.astimezone(timezone.utc) <= current < end.astimezone(timezone.utc)

    def verify_signature(self, public_key: bytes) -> bool:
        if not isinstance(public_key, bytes) or len(public_key) != 32:
            return False
        if self.authorization_id != self.computed_authorization_id:
            return False
        try:
            Ed25519PublicKey.from_public_bytes(public_key).verify(self.signature, self.canonical_payload)
        except (InvalidSignature, ValueError, TypeError):
            return False
        return True
