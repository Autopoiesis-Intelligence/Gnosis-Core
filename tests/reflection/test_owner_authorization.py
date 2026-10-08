from __future__ import annotations

import base64

import pytest
from nacl.signing import SigningKey

from gnosis.reflection.owner_authorization import (
    ProductionAuthorization,
    ROTATED,
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
        authorization_id="",
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
    authorization_id = unsigned.expected_authorization_id()
    unsigned = ProductionAuthorization(**{**unsigned.__dict__, "authorization_id": authorization_id})
    signature = signing_key.sign(unsigned.canonical_bytes()).signature
    return ProductionAuthorization(
        **{**unsigned.__dict__, "signature": base64.b64encode(signature).decode("ascii")}
    )


def test_valid_authorization_verifies_with_exact_issuer_and_key_version() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)

    assert verify_production_authorization(
        authorization,
        Resolver(trusted),
        now=150,
        expected_scope={"execute"},
        expected_policy_version="policy-1",
        expected_evolution_identity="evolution:1",
        expected_parent_state_digest="parent:1",
        expected_request_provenance="request:1",
    ) == trusted


def test_tampered_payload_fails_signature_verification() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)
    tampered = ProductionAuthorization(**{**authorization.__dict__, "policy_version": "policy-2"})

    with pytest.raises(PermissionError, match="signature verification failed"):
        verify_production_authorization(tampered, Resolver(trusted), now=150)


def test_unknown_issuer_or_key_version_fails_closed() -> None:
    signing_key = SigningKey.generate()
    authorization = make_authorization(signing_key)

    with pytest.raises(PermissionError, match="trusted issuer key not found"):
        verify_production_authorization(authorization, Resolver(None), now=150)


def test_rotated_key_is_not_accepted() -> None:
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

    with pytest.raises(PermissionError, match="authorization is outside"):
        verify_production_authorization(authorization, Resolver(trusted), now=now)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("policy_version", "policy-2"),
        ("evolution_identity", "evolution:2"),
        ("parent_state_digest", "parent:2"),
        ("request_provenance", "request:2"),
    ],
)
def test_expected_binding_mismatch_fails_closed(field: str, expected: str) -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)

    kwargs = {
        "expected_scope": {"execute"},
        "expected_policy_version": "policy-1",
        "expected_evolution_identity": "evolution:1",
        "expected_parent_state_digest": "parent:1",
        "expected_request_provenance": "request:1",
    }
    if field == "policy_version":
        kwargs["expected_policy_version"] = expected
        match = "policy mismatch"
    elif field == "evolution_identity":
        kwargs["expected_evolution_identity"] = expected
        match = "evolution mismatch"
    elif field == "parent_state_digest":
        kwargs["expected_parent_state_digest"] = expected
        match = "parent-state mismatch"
    else:
        kwargs["expected_request_provenance"] = expected
        match = "request-provenance mismatch"

    with pytest.raises(PermissionError, match=match):
        verify_production_authorization(authorization, Resolver(trusted), now=150, **kwargs)


def test_scope_mismatch_fails_closed() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)

    with pytest.raises(PermissionError, match="scope mismatch"):
        verify_production_authorization(
            authorization, Resolver(trusted), now=150, expected_scope={"read"}
        )


def test_invalid_signature_encoding_fails_closed() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = ProductionAuthorization(
        **{**make_authorization(signing_key).__dict__, "signature": "not-base64"}
    )

    with pytest.raises(PermissionError, match="signature encoding is invalid"):
        verify_production_authorization(authorization, Resolver(trusted), now=150)


def test_nonce_is_required() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = ProductionAuthorization(
        **{**make_authorization(signing_key).__dict__, "nonce": ""}
    )

    with pytest.raises(PermissionError, match="authorization nonce is missing"):
        verify_production_authorization(authorization, Resolver(trusted), now=150)


def test_authorization_id_tampering_fails_closed() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)
    tampered = ProductionAuthorization(**{**authorization.__dict__, "authorization_id": "auth:tampered"})

    with pytest.raises(PermissionError, match="authorization identity mismatch"):
        verify_production_authorization(tampered, Resolver(trusted), now=150)


def test_scope_must_be_canonical() -> None:
    signing_key = SigningKey.generate()
    trusted = TrustedIssuerKey("owner-1", "v1", signing_key.verify_key.encode())
    authorization = make_authorization(signing_key)
    tampered = ProductionAuthorization(**{**authorization.__dict__, "authority_scope": ("execute", "execute")})

    with pytest.raises(PermissionError, match="scope is not canonical"):
        verify_production_authorization(tampered, Resolver(trusted), now=150)
