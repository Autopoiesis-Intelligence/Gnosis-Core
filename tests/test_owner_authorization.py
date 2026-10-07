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
