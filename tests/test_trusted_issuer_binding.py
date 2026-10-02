import pytest

from gnosis.reflection.authority import OwnerApproval
from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer


def make_issuer():
    return TrustedOwnerIssuer(
        authority_root="root-1",
        scope="scope-1",
        policy_version="policy-1",
    )


def make_approval():
    return OwnerApproval("auth-1", "prov-1", "evolution-1")


def test_trusted_owner_issuer_carries_policy_and_evidence_into_authorization():
    authorization = make_issuer().issue(
        TrustedIssuerInput(
            approval=make_approval(),
            authority_root="root-1",
            scope="scope-1",
            policy_version="policy-1",
            evidence_digest="ev-1",
        ),
        request_provenance="prov-1",
        evolution_identity="evolution-1",
    )

    assert authorization.policy_version == "policy-1"
    assert authorization.evidence_digest == "ev-1"


def test_trusted_owner_issuer_rejects_policy_substitution():
    with pytest.raises(PermissionError, match="policy"):
        make_issuer().issue(
            TrustedIssuerInput(
                approval=make_approval(),
                authority_root="root-1",
                scope="scope-1",
                policy_version="policy-2",
                evidence_digest="ev-1",
            ),
            request_provenance="prov-1",
            evolution_identity="evolution-1",
        )
