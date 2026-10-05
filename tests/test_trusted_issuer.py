import pytest

from gnosis.reflection.authority import OwnerApproval
from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer
from gnosis.core.policy import PolicyIdentity


def req():
    policy=PolicyIdentity("test-rule",1,"impl-1")
    approval=OwnerApproval("a1","p1","e1",policy)
    return TrustedIssuerInput(approval,"root-1","evolution.commit","1","evd")


def issuer():
    return TrustedOwnerIssuer("root-1","evolution.commit","1",PolicyIdentity("test-rule",1,"impl-1"))


def test_exact_approval_is_issued():
    auth=issuer().issue(req(),request_provenance="p1",evolution_identity="e1")
    assert auth.can_execute is True
    assert auth.approval_id == "a1"

@pytest.mark.parametrize("field,value",[("authority_root","root-x"),("scope","other.scope"),("policy_version","2")])
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
