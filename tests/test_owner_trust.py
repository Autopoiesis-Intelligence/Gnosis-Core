from __future__ import annotations

import pytest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from gnosis.reflection.owner_trust import OwnerTrustAnchor


@pytest.fixture()
def anchor() -> tuple[Ed25519PrivateKey, OwnerTrustAnchor]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    return private_key, OwnerTrustAnchor(
        issuer_id="owner-1",
        key_id="key-v1",
        public_key=public_key,
    )


def test_valid_signature_is_accepted(anchor) -> None:
    private_key, trust_anchor = anchor
    payload = b"canonical-owner-authorization-payload"
    signature = private_key.sign(payload)

    assert trust_anchor.verify(
        payload,
        signature,
        issuer_id="owner-1",
        key_id="key-v1",
    )


def test_wrong_key_is_rejected(anchor) -> None:
    _, trust_anchor = anchor
    wrong_key = Ed25519PrivateKey.generate()
    payload = b"payload"
    signature = wrong_key.sign(payload)

    assert not trust_anchor.verify(
        payload,
        signature,
        issuer_id="owner-1",
        key_id="key-v1",
    )


def test_modified_payload_is_rejected(anchor) -> None:
    private_key, trust_anchor = anchor
    signature = private_key.sign(b"original")

    assert not trust_anchor.verify(
        b"modified",
        signature,
        issuer_id="owner-1",
        key_id="key-v1",
    )


def test_unknown_issuer_is_rejected(anchor) -> None:
    private_key, trust_anchor = anchor
    payload = b"payload"
    signature = private_key.sign(payload)

    assert not trust_anchor.verify(
        payload,
        signature,
        issuer_id="unknown-owner",
        key_id="key-v1",
    )


def test_unknown_key_version_is_rejected(anchor) -> None:
    private_key, trust_anchor = anchor
    payload = b"payload"
    signature = private_key.sign(payload)

    assert not trust_anchor.verify(
        payload,
        signature,
        issuer_id="owner-1",
        key_id="key-v2",
    )


@pytest.mark.parametrize(
    ("payload", "signature"),
    [
        (b"payload", b""),
        (b"payload", b"malformed"),
        (b"not-bytes", b"signature"),
    ],
)
def test_malformed_input_is_rejected(anchor, payload, signature) -> None:
    _, trust_anchor = anchor

    assert not trust_anchor.verify(
        payload,
        signature,
        issuer_id="owner-1",
        key_id="key-v1",
    )


def test_invalid_anchor_configuration_fails_closed() -> None:
    with pytest.raises(ValueError):
        OwnerTrustAnchor(
            issuer_id="owner-1",
            key_id="key-v1",
            public_key=b"short",
        )
