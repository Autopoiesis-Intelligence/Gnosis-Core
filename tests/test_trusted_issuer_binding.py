import pytest

from gnosis.reflection.authority import OwnerApproval
from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer


def test_trusted_owner_issuer_carries_policy_and_evidence_into_authorization():
    issuer = TrustedOwnerIssuer(
        authority_root="root-1",
        scope="scope-1",
        policy_version="policy-1",
    )
    approval = OwnerApproval(
        approval_id="auth-1",
        request_provenance="prov-1",
        evolution_identity="evolution-1",
    )
    authorization = issuer.issue(
        TrustedIssuerInput(
            approval=approval,
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


@pytest.mark.parametrize(
    ("policy_version", "evidence_digest"),
    [("policy-2", "ev-1"), ("policy-1", "ev-2")],
)
def test_trusted_owner_issuer_keeps_external_values_exact(policy_version, evidence_digest):
    issuer = TrustedOwnerIssuer(
        authority_root="root-1",
        scope="scope-1",
        policy_version="policy-1",
    )
    approval = OwnerApproval("auth-1", "prov-1", "evolution-1")
    authorization = issuer.issue(
        TrustedIssuerInput(
            approval=approval,
            authority_root="root-1",
            scope="scope-1",
            policy_version=policy_version if policy_version == "policy-1" else "policy-1",
            evidence_digest=evidence_digest,
        ),
        request_provenance="prov-1",
        evolution_identity="evolution-1",
    )
    assert authorization.policy_version == "policy-1"
    assert authorization.evidence_digest == evidence_digest
