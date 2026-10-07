from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from gnosis.reflection.owner_authorization import OwnerAuthorizationV1
from gnosis.reflection.owner_authorization_verifier import verify_owner_authorization
from gnosis.reflection.owner_trust import OwnerTrustAnchor


def make_authorization(private_key: Ed25519PrivateKey, **overrides: object) -> OwnerAuthorizationV1:
    values = {
        "owner_id": "owner-1",
        "key_id": "key-1",
        "audience": "execution",
        "scope": "candidate-commit",
        "authorization_id": "auth-1",
        "request_provenance": "prov-1",
        "evolution_identity": "evo-1",
    }
    values.update(overrides)
    unsigned = OwnerAuthorizationV1(signature=b"", **values)
    return OwnerAuthorizationV1(signature=private_key.sign(unsigned.canonical_signed_bytes()), **values)


def test_trusted_owner_and_key_signature_verifies() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    authorization = make_authorization(private_key)
    anchor = OwnerTrustAnchor("owner-1", "key-1", public_key)

    assert verify_owner_authorization(authorization, trust_anchor=anchor)


def test_owner_mismatch_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    authorization = make_authorization(private_key)
    anchor = OwnerTrustAnchor("other-owner", "key-1", public_key)

    assert not verify_owner_authorization(authorization, trust_anchor=anchor)


def test_key_mismatch_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    authorization = make_authorization(private_key)
    anchor = OwnerTrustAnchor("owner-1", "other-key", public_key)

    assert not verify_owner_authorization(authorization, trust_anchor=anchor)


def test_wrong_trusted_public_key_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
    authorization = make_authorization(private_key)
    anchor = OwnerTrustAnchor("owner-1", "key-1", wrong_key)

    assert not verify_owner_authorization(authorization, trust_anchor=anchor)


def test_missing_trust_anchor_fails_closed(monkeypatch) -> None:
    monkeypatch.delenv("GNOZIS_OWNER_ID", raising=False)
    monkeypatch.delenv("GNOZIS_OWNER_KEY_ID", raising=False)
    monkeypatch.delenv("GNOZIS_OWNER_TRUSTED_ED25519_PUBLIC_KEY_HEX", raising=False)
    private_key = Ed25519PrivateKey.generate()

    assert not verify_owner_authorization(make_authorization(private_key))


def test_caller_supplied_public_key_is_not_an_argument() -> None:
    private_key = Ed25519PrivateKey.generate()
    authorization = make_authorization(private_key)
    anchor = OwnerTrustAnchor("owner-1", "key-1", private_key.public_key().public_bytes_raw())

    assert verify_owner_authorization(authorization, trust_anchor=anchor)
    try:
        verify_owner_authorization(authorization, public_key=anchor.public_key)
    except TypeError:
        pass
    else:
        raise AssertionError("caller public-key substitution must not be supported")
