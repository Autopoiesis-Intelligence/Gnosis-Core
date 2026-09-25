import pytest
from gnosis.reflection.authorization_validity import AuthorizationValidity


def valid(): return AuthorizationValidity("auth-1","policy-1","ev-1")

def test_exact_validity_passes(): valid().require_valid(expected_policy_version="policy-1",expected_evidence_digest="ev-1")

@pytest.mark.parametrize("obj,policy,evidence",[(AuthorizationValidity("auth-1","policy-x","ev-1"),"policy-1","ev-1"),(AuthorizationValidity("auth-1","policy-1","ev-x"),"policy-1","ev-1"),(AuthorizationValidity("auth-1","policy-1","ev-1",True),"policy-1","ev-1")])
def test_invalid_or_revoked_fails_closed(obj,policy,evidence):
    with pytest.raises(PermissionError): obj.require_valid(expected_policy_version=policy,expected_evidence_digest=evidence)
