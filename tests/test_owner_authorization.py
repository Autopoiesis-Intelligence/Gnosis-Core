import json

from gnosis.reflection.owner_authorization import OwnerAuthorizationV1


def make_authorization(**overrides: object) -> OwnerAuthorizationV1:
    values = {
        "owner_id": "owner-1",
        "key_id": "key-1",
        "audience": "execution",
        "scope": "candidate-commit",
        "authorization_id": "auth-1",
        "request_provenance": "prov-1",
        "evolution_identity": "evo-1",
        "signature": b"signature",
    }
    values.update(overrides)
    return OwnerAuthorizationV1(**values)


def test_canonical_signed_bytes_are_deterministic() -> None:
    auth = make_authorization()
    assert auth.canonical_signed_bytes() == auth.canonical_signed_bytes()


def test_signature_is_not_part_of_signed_bytes() -> None:
    first = make_authorization(signature=b"one")
    second = make_authorization(signature=b"two")
    assert first.canonical_signed_bytes() == second.canonical_signed_bytes()


def test_field_order_is_canonical() -> None:
    auth = make_authorization()
    assert auth.canonical_signed_bytes() == (
        b'{"audience":"execution","authorization_id":"auth-1",'
        b'"evolution_identity":"evo-1","key_id":"key-1",'
        b'"owner_id":"owner-1","request_provenance":"prov-1",'
        b'"scope":"candidate-commit"}'
    )


def test_signed_bytes_are_utf8_json_without_whitespace() -> None:
    auth = make_authorization(audience="исполнение")
    payload = json.loads(auth.canonical_signed_bytes().decode("utf-8"))
    assert payload["audience"] == "исполнение"
    assert b" " not in auth.canonical_signed_bytes()


def test_frozen_envelope_cannot_be_mutated() -> None:
    auth = make_authorization()
    try:
        auth.owner_id = "changed"
    except Exception:
        pass
    else:
        raise AssertionError("OwnerAuthorizationV1 must be immutable")

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def test_valid_signature_verifies() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    unsigned = make_authorization()
    signed = make_authorization(signature=private_key.sign(unsigned.canonical_signed_bytes()))
    assert signed.verify_signature(public_key)


def test_changed_signed_field_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    unsigned = make_authorization()
    signed = make_authorization(signature=private_key.sign(unsigned.canonical_signed_bytes()), scope="changed")
    assert not signed.verify_signature(public_key)


def test_wrong_public_key_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    wrong_key = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
    unsigned = make_authorization()
    signed = make_authorization(signature=private_key.sign(unsigned.canonical_signed_bytes()))
    assert not signed.verify_signature(wrong_key)


def test_malformed_signature_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    assert not make_authorization(signature=b"bad").verify_signature(public_key)
