from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from gnosis.reflection.owner_authorization import OwnerAuthorizationV1, canonical_payload


FIELDS = {
    "issuer_id": "owner-issuer",
    "key_version": "key-v1",
    "authority_root": "root-1",
    "scope": "evolution.commit",
    "policy_version": "policy-v1",
    "request_provenance": "request-1",
    "evolution_identity": "evolution:abc",
    "parent_state_digest": "sha256:parent",
    "evidence_digest": "sha256:evidence",
    "authorization_id": "",
    "nonce": "nonce-1",
    "valid_from": "2026-10-07T00:00:00Z",
    "valid_until": "2026-10-08T00:00:00Z",
}


def make_authorization(private_key: Ed25519PrivateKey) -> OwnerAuthorizationV1:
    unsigned_payload = canonical_payload({**FIELDS, "authorization_id": "placeholder"})
    auth_id = "sha256:" + __import__("hashlib").sha256(unsigned_payload).hexdigest()
    fields = {**FIELDS, "authorization_id": auth_id}
    payload = canonical_payload(fields)
    return OwnerAuthorizationV1(**fields, signature=private_key.sign(payload))


def test_valid_signature_is_accepted() -> None:
    private_key = Ed25519PrivateKey.generate()
    authorization = make_authorization(private_key)
    assert authorization.verify_signature(private_key.public_key().public_bytes_raw())


def test_modified_security_field_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    authorization = make_authorization(private_key)
    modified = OwnerAuthorizationV1(
        **{**authorization.__dict__, "scope": "different-scope"},
    )
    assert not modified.verify_signature(private_key.public_key().public_bytes_raw())


def test_wrong_key_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    authorization = make_authorization(private_key)
    wrong_key = Ed25519PrivateKey.generate()
    assert not authorization.verify_signature(wrong_key.public_key().public_bytes_raw())


def test_wrong_authorization_id_is_rejected() -> None:
    private_key = Ed25519PrivateKey.generate()
    authorization = make_authorization(private_key)
    tampered = OwnerAuthorizationV1(
        **{**authorization.__dict__, "authorization_id": "sha256:wrong"},
    )
    assert not tampered.verify_signature(private_key.public_key().public_bytes_raw())


def test_wrong_domain_payload_cannot_verify() -> None:
    private_key = Ed25519PrivateKey.generate()
    authorization = make_authorization(private_key)
    assert authorization.canonical_payload.startswith(b'{"authority_root"') is False
