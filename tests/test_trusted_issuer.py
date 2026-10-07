import pytest

from gnosis.reflection.authority import OwnerApproval
from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer
from gnosis.reflection.crypto import generate_keypair, sign_owner_authorization


def req():
    private_key, public_key = generate_keypair()
    authorization = {
        "authority_root": "root-1",
        "scope": "evolution.commit",
        "policy_version": "policy-1",
        "evidence_digest": "evd",
        "request_provenance": "p1",
        "evolution_identity": "e1",
        "approval_id": "a1",
    }
    approval = OwnerApproval.from_signed_authorization(
        authorization,
        signature=sign_owner_authorization(private_key, authorization),
        owner_public_key=public_key,
    )
    return TrustedIssuerInput(approval,"root-1","evolution.commit","policy-1","evd")


def issuer():
    return TrustedOwnerIssuer("root-1","evolution.commit","policy-1")


def test_exact_approval_is_issued():
    auth=issuer().issue(req(),request_provenance="p1",evolution_identity="e1")
    assert auth.can_execute is True
    assert auth.approval_id == "a1"

@pytest.mark.parametrize("field,value",[("authority_root","root-x"),("scope","other.scope"),("policy_version","policy-x")])
def test_root_scope_policy_mismatch_fails_closed(field,value):
    base=req().__dict__.copy(); base[field]=value
    with pytest.raises(PermissionError):
        issuer().issue(TrustedIssuerInput(**base),request_provenance="p1",evolution_identity="e1")


def test_cross_evolution_approval_fails_closed():
    with pytest.raises(PermissionError):
        issuer().issue(req(),request_provenance="p1",evolution_identity="forged")


def test_missing_evidence_fails_closed():
    base=req().__dict__.copy(); base["evidence_digest"]=""
    with pytest.raises(PermissionError):
        issuer().issue(TrustedIssuerInput(**base),request_provenance="p1",evolution_identity="e1")
