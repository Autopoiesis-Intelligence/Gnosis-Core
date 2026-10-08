from __future__ import annotations

import base64

import pytest
from nacl.signing import SigningKey

from gnosis.reflection.owner_authorization import (
    ACTIVE,
    ROTATED,
    ProductionAuthorization,
    TrustedIssuerKey,
    verify_production_authorization,
)


class Resolver:
    def __init__(self, key: TrustedIssuerKey | None) -> None:
        self.key = key

    def resolve(self, issuer_id: str, key_version: str):
        if self.key and self.key.issuer_id == issuer_id and self.key.key_version == key_version:
            return self.key
        return None


def make_authorization(signing_key: SigningKey) -> ProductionAuthorization:
    unsigned = ProductionAuthorization(
        authorization_id="auth-1",
        issuer_id="owner-1",
        key_version="v1",
        authority_scope=("execute",),
        policy_version="policy-1",
        evolution_identity="evolution:1",
        parent_state_digest="parent:1",
        request_provenance="request:1",
        valid_from=100,
        expires_at=200,
        nonce="nonce-1",
        signature="",
    )
    signature = signing_key.sign(unsigned.canonical_bytes()).signature
    return ProductionAuthorization(
        **{**unsigned.__dict__, "signature": base64.b64encode(signature).decode("ascii")}
    )


def test_production_authorization_verifies_with_exact_issuer_and_key_version() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)

    result = verify_production_authorization(
        authorization,
        Resolver(trusted),
        now=150,
        expected_scope={"execute"},
        expected_policy_version="policy-1",
        expected_evolution_identity="evolution:1",
        expected_parent_state_digest="parent:1",
        expected_request_provenance="request:1",
    )

    assert result == trusted


def test_tampered_payload_fails_signature_verification() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)
    tampered = ProductionAuthorization(**{**authorization.__dict__, "policy_version": "policy-2"})

    with pytest.raises(PermissionError, match="signature verification failed"):
        verify_production_authorization(tampered, Resolver(trusted), now=150)


def test_unknown_key_version_fails_closed() -> None:
    signing_key = SigningKey.generate()
    authorization = make_authorization(signing_key)

    with pytest.raises(PermissionError, match="trusted issuer key not found"):
        verify_production_authorization(authorization, Resolver(None), now=150)


def test_rotated_key_is_not_accepted_for_new_authorization() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode(), status=ROTATED)
    authorization = make_authorization(signing_key)

    with pytest.raises(PermissionError, match="not active"):
        verify_production_authorization(authorization, Resolver(trusted), now=150)


@pytest.mark.parametrize("now", [99, 200])
def test_authorization_validity_interval_is_fail_closed(now: int) -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)

    with pytest.raises(PermissionError, match="validity interval"):
        verify_production_authorization(authorization, Resolver(trusted), now=now)
