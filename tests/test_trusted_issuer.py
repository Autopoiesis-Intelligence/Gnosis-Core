import hashlib

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from gnosis.reflection.authority import OwnerApproval
from gnosis.reflection.owner_authorization import (
    OwnerAuthorizationV1,
    authorization_id_for,
    canonical_payload,
)
from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer


PRIVATE_KEY = Ed25519PrivateKey.generate()


def authorization():
    fields = {
        "issuer_id": "owner-issuer",
        "key_version": "key-v1",
        "authority_root": "root-1",
        "scope": "evolution.commit",
        "policy_version": "policy-1",
        "request_provenance": "p1",
        "evolution_identity": "e1",
        "parent_state_digest": "sha256:parent",
        "evidence_digest": "evd",
        "authorization_id": "",
        "nonce": "nonce-1",
        "valid_from": "2026-10-07T00:00:00Z",
        "valid_until": "2026-10-08T00:00:00Z",
    }
    fields["authorization_id"] = authorization_id_for(fields)
    payload = canonical_payload(fields)
    return OwnerAuthorizationV1(**fields, signature=PRIVATE_KEY.sign(payload))


def req():
    auth = authorization()
    approval = OwnerApproval(auth.authorization_id, "p1", "e1")
    return TrustedIssuerInput(approval, auth, "root-1", "evolution.commit", "policy-1", "evd")


def issuer():
    return TrustedOwnerIssuer(
        "root-1",
        "evolution.commit",
        "policy-1",
        "owner-issuer",
        "key-v1",
        PRIVATE_KEY.public_key().public_bytes_raw(),
    )


def test_exact_signed_authorization_is_issued():
    auth = issuer().issue(req(), request_provenance="p1", evolution_identity="e1")
    assert auth.can_execute is True
    assert auth.approval_id == req().approval.approval_id


@pytest.mark.parametrize("field,value", [
    ("authority_root", "root-x"),
    ("scope", "other.scope"),
    ("policy_version", "policy-x"),
])
def test_request_binding_mismatch_fails_closed(field, value):
    base = req().__dict__.copy()
    base[field] = value
    with pytest.raises(PermissionError):
        issuer().issue(TrustedIssuerInput(**base), request_provenance="p1", evolution_identity="e1")


def test_invalid_signature_fails_closed():
    request = req()
    bad = OwnerAuthorizationV1(**{**request.authorization.__dict__, "signature": b"bad"})
    request = TrustedIssuerInput(
        request.approval, bad, request.authority_root, request.scope,
        request.policy_version, request.evidence_digest,
    )
    with pytest.raises(PermissionError):
        issuer().issue(request, request_provenance="p1", evolution_identity="e1")


def test_wrong_issuer_key_version_fails_closed():
    request = req()
    bad = OwnerAuthorizationV1(**{**request.authorization.__dict__, "key_version": "key-v2"})
    request = TrustedIssuerInput(
        request.approval, bad, request.authority_root, request.scope,
        request.policy_version, request.evidence_digest,
    )
    with pytest.raises(PermissionError):
        issuer().issue(request, request_provenance="p1", evolution_identity="e1")


def test_cross_evolution_fails_closed():
    with pytest.raises(PermissionError):
        issuer().issue(req(), request_provenance="p1", evolution_identity="forged")


def test_missing_evidence_fails_closed():
    base = req().__dict__.copy()
    base["evidence_digest"] = ""
    with pytest.raises(PermissionError):
        issuer().issue(TrustedIssuerInput(**base), request_provenance="p1", evolution_identity="e1")
