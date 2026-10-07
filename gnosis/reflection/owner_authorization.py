"""Canonical owner authorization envelope."""

from __future__ import annotations

from dataclasses import dataclass
import json

from gnosis.crypto import Ed25519SignatureVerifier


@dataclass(frozen=True)
class OwnerAuthorizationV1:
    owner_id: str
    key_id: str
    audience: str
    scope: str
    authorization_id: str
    request_provenance: str
    evolution_identity: str
    signature: bytes

    def canonical_signed_bytes(self) -> bytes:
        payload = {
            "audience": self.audience,
            "authorization_id": self.authorization_id,
            "evolution_identity": self.evolution_identity,
            "key_id": self.key_id,
            "owner_id": self.owner_id,
            "request_provenance": self.request_provenance,
            "scope": self.scope,
        }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")

    def verify_signature(self, public_key: bytes) -> bool:
        return Ed25519SignatureVerifier().verify(
            public_key=public_key,
            message=self.canonical_signed_bytes(),
            signature=self.signature,
        )
