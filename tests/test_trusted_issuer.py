import pytest

from gnosis.reflection.authority import OwnerApproval
from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer


def req():
    # This dataclass can be constructed by any caller; its fields are not a signature.
    approval = OwnerApproval("a1", "p1", "e1")
    return TrustedIssuerInput(approval, "root-1", "evolution.commit", "policy-1", "evd")


def issuer():
    return TrustedOwnerIssuer("root-1", "evolution.commit", "policy-1")


def test_caller_constructed_approval_never_grants_execution_authority():
    with pytest.raises(PermissionError, match="unsigned OwnerApproval"):
        issuer().issue(req(), request_provenance="p1", evolution_identity="e1")


@pytest.mark.parametrize(
    "field,value",
    [("authority_root", "root-x"), ("scope", "other.scope"), ("policy_version", "policy-x")],
)
def test_root_scope_policy_mismatch_fails_closed(field, value):
    base = req().__dict__.copy()
    base[field] = value
    with pytest.raises(PermissionError):
        issuer().issue(
            TrustedIssuerInput(**base),
            request_provenance="p1",
            evolution_identity="e1",
        )


def test_cross_evolution_approval_fails_closed():
    with pytest.raises(PermissionError):
        issuer().issue(req(), request_provenance="p1", evolution_identity="forged")


def test_missing_evidence_fails_closed():
    base = req().__dict__.copy()
    base["evidence_digest"] = ""
    with pytest.raises(PermissionError):
        issuer().issue(
            TrustedIssuerInput(**base),
            request_provenance="p1",
            evolution_identity="e1",
        )
