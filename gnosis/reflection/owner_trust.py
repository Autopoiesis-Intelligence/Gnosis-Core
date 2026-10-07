"""Deployment-configured owner trust anchor."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class OwnerTrustAnchor:
    owner_id: str
    key_id: str
    public_key: bytes

    @classmethod
    def from_environment(cls) -> "OwnerTrustAnchor | None":
        owner_id = os.environ.get("GNOZIS_OWNER_ID")
        key_id = os.environ.get("GNOZIS_OWNER_KEY_ID")
        public_key_hex = os.environ.get("GNOZIS_OWNER_TRUSTED_ED25519_PUBLIC_KEY_HEX")

        if not owner_id or not key_id or not public_key_hex:
            return None

        try:
            public_key = bytes.fromhex(public_key_hex)
        except ValueError:
            return None

        if len(public_key) != 32:
            return None

        return cls(owner_id=owner_id, key_id=key_id, public_key=public_key)

    def matches(self, *, owner_id: str, key_id: str) -> bool:
        return self.owner_id == owner_id and self.key_id == key_id
