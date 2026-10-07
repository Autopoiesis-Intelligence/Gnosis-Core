"""Cryptographic verification for externally issued owner authorization.

This module is deliberately verifier-only. It does not create authority,
store private keys, choose a trust root, or issue execution authorization.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from hashlib import sha256

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


DOMAIN = "GNOZIS-OWNER-AUTHORIZATION-V1"


def canonical_payload(fields: dict[str, str]) -> bytes:
    """Produce deterministic, domain-separated signed bytes."""
    if set(fields) != {
        "issuer_id",
        "key_version",
        "authority_root",
        "scope",
        "policy_version",
        "request_provenance",
        "evolution_identity",
        "parent_state_digest",
        "evidence_digest",
        "authorization_id",
        "nonce",
        "valid_from",
        "valid_until",
    }:
        raise ValueError("owner authorization field set is incomplete or contains unknown fields")
    if any(not isinstance(value, str) or not value for value in fields.values()):
        raise ValueError("owner authorization fields must be non-empty strings")
    document = {"domain": DOMAIN, "version": "1", **fields}
    return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
            "issuer_id": self.issuer_id,
            "key_version": self.key_version,
            "authority_root": self.authority_root,
            "scope": self.scope,
            "policy_version": self.policy_version,
            "request_provenance": self.request_provenance,
            "evolution_identity": self.evolution_identity,
            "parent_state_digest": self.parent_state_digest,
            "evidence_digest": self.evidence_digest,
            "authorization_id": self.authorization_id,
            "nonce": self.nonce,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
        })

    @property
    def computed_authorization_id(self) -> str:
        return "sha256:" + sha256(self.canonical_payload).hexdigest()

    def verify_signature(self, public_key: bytes) -> bool:
        if not isinstance(public_key, bytes) or len(public_key) != 32:
            return False
        if self.authorization_id != self.computed_authorization_id:
            return False
        try:
            Ed25519PublicKey.from_public_bytes(public_key).verify(
                self.signature,
                self.canonical_payload,
            )
        except (InvalidSignature, ValueError, TypeError):
            return False
        return True
