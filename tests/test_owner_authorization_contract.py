"""Contract tests for the signed owner-authorization primitive.

These tests cover the pure verifier only. They do not prove production commit
integration, replay consumption, or trusted runtime composition.
"""
from __future__ import annotations

import base64
from dataclasses import replace

import pytest
from nacl.signing import SigningKey

from gnosis.reflection.owner_authorization import (
    ACTIVE,
    REVOKED,
    ProductionAuthorization,
    TrustedIssuerKey,
    verify_production_authorization,
)


ISSUER = "owner-root"
KEY_VERSION = "key-1"
SCOPE = {"core:commit"}
POLICY = "policy-1"
EVOLUTION = "evolution:abc"
PARENT = "state:parent"
PROVENANCE = "request:abc"
NOW = 1_800_000_000


class Resolver:
    def __init__(self, key: TrustedIssuerKey | None):
        self.key = key

    def resolve(self, issuer_id: str, key_version: str) -> TrustedIssuerKey | None:
        if self.key is None:
            return None
        if (issuer_id, key_version) != (self.key.issuer_id, self.key.key_version):
            return None
        return self.key


def signed_authorization(signing_key: SigningKey, *, nonce: str = "nonce-1") -> ProductionAuthorization:
    unsigned = ProductionAuthorization(
        authorization_id="pending",
        issuer_id=ISSUER,
        key_version=KEY_VERSION,
        authority_scope=("core:commit",),
        policy_version=POLICY,
        evolution_identity=EVOLUTION,
        parent_state_digest=PARENT,
        request_provenance=PROVENANCE,
        valid_from=NOW - 60,
        expires_at=NOW + 60,
        nonce=nonce,
        signature="pending",
    )
    authorization_id = unsigned.expected_authorization_id()
    unsigned = replace(unsigned, authorization_id=authorization_id)
    signature = signing_key.sign(unsigned.canonical_bytes()).signature
    return replace(unsigned, signature=base64.b64encode(signature).decode("ascii"))


def trusted_key(signing_key: SigningKey, *, status: str = ACTIVE) -> TrustedIssuerKey:
    return TrustedIssuerKey(
        issuer_id=ISSUER,
        key_version=KEY_VERSION,
        public_key=bytes(signing_key.verify_key),
        status=status,
        valid_from=NOW - 100,
        expires_at=NOW + 100,
    )


def verify(authorization: ProductionAuthorization, resolver: Resolver, **overrides: object) -> TrustedIssuerKey:
    arguments: dict[str, object] = {
        "now": NOW,
        "expected_scope": SCOPE,
        "expected_policy_version": POLICY,
        "expected_evolution_identity": EVOLUTION,
        "expected_parent_state_digest": PARENT,
        "expected_request_provenance": PROVENANCE,
    }
    arguments.update(overrides)
    return verify_production_authorization(authorization, resolver, **arguments)  # type: ignore[arg-type]


def test_valid_signature_and_request_bindings_are_accepted() -> None:
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)
    key = trusted_key(signing_key)

    assert verify(authorization, Resolver(key)) == key


def test_invalid_signature_is_rejected() -> None:
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)
    tampered = replace(authorization, signature=base64.b64encode(b"x" * 64).decode("ascii"))

    with pytest.raises(PermissionError, match="signature verification failed"):
        verify(tampered, Resolver(trusted_key(signing_key)))


@pytest.mark.parametrize(
    ("field", "expected", "message"),
    [
        ("expected_scope", {"core:rollback"}, "scope mismatch"),
        ("expected_policy_version", "policy-2", "policy mismatch"),
        ("expected_evolution_identity", "evolution:other", "evolution mismatch"),
        ("expected_parent_state_digest", "state:other", "parent-state mismatch"),
        ("expected_request_provenance", "request:other", "request-provenance mismatch"),
    ],
)
def test_request_binding_mismatches_are_rejected(field: str, expected: object, message: str) -> None:
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)

    with pytest.raises(PermissionError, match=message):
        verify(authorization, Resolver(trusted_key(signing_key)), **{field: expected})


def test_expired_authorization_is_rejected() -> None:
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)
    expired = replace(authorization, valid_from=NOW - 200, expires_at=NOW - 1)
    # Re-sign because validity fields are part of the signed payload and identity.
    expired = replace(expired, authorization_id=expired.expected_authorization_id())
    expired = replace(
        expired,
        signature=base64.b64encode(signing_key.sign(expired.canonical_bytes()).signature).decode("ascii"),
    )

    with pytest.raises(PermissionError, match="outside its validity interval"):
        verify(expired, Resolver(trusted_key(signing_key)))


def test_revoked_trusted_key_is_rejected() -> None:
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)

    with pytest.raises(PermissionError, match="key is not active"):
        verify(authorization, Resolver(trusted_key(signing_key, status=REVOKED)))


def test_missing_trusted_key_is_rejected() -> None:
    signing_key = SigningKey.generate()
    authorization = signed_authorization(signing_key)

    with pytest.raises(PermissionError, match="trusted issuer key not found"):
        verify(authorization, Resolver(None))
