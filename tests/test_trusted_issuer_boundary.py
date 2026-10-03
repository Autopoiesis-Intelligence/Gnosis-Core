import pytest

from gnosis.reflection.authority import (
    ExecutionAuthorization,
    require_execution_authorization,
)
from gnosis.reflection.trusted_issuer import (
    TrustedIssuerInput,
    TrustedOwnerIssuer,
)
from gnosis.reflection.authority import OwnerApproval


def test_execution_authorization_requires_trusted_issuer_attestation():
    auth = ExecutionAuthorization(
        request_provenance="p",
        owner_approved=True,
        evolution_identity="e",
        approval_id="approval-1",
        policy_version="policy-1",
    )
    with pytest.raises(PermissionError, match="trusted issuer attestation"):
        require_execution_authorization(auth, request_provenance="p", evolution_identity="e")


def test_trusted_owner_issuer_emits_bound_attestation():
    issuer = TrustedOwnerIssuer("root-1", "core-evolution", "policy-1")
    approval = OwnerApproval("approval-1", "p", "e")
    auth = issuer.issue(
        TrustedIssuerInput(
            approval=approval,
            authority_root="root-1",
            scope="core-evolution",
            policy_version="policy-1",
            evidence_digest="evidence-1",
        ),
        request_provenance="p",
        evolution_identity="e",
    )
    require_execution_authorization(auth, request_provenance="p", evolution_identity="e")
    assert auth.issuer_attestation is not None
    assert auth.issuer_attestation.authority_root == "root-1"
    assert auth.issuer_attestation.scope == "core-evolution"
    assert auth.issuer_attestation.policy_version == "policy-1"


def test_trusted_owner_issuer_rejects_policy_substitution():
    issuer = TrustedOwnerIssuer("root-1", "core-evolution", "policy-1")
    approval = OwnerApproval("approval-1", "p", "e")
    with pytest.raises(PermissionError, match="policy"):
        issuer.issue(
            TrustedIssuerInput(approval, "root-1", "core-evolution", "policy-2", "evidence-1"),
            request_provenance="p",
            evolution_identity="e",
        )
