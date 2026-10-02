from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
    OwnerApproval,
)
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer
from tests.test_authority_boundary import _snapshot_provenance


def test_trusted_owner_issuer_creates_bound_execution_authorization():
    provenance = _snapshot_provenance()
    approval = OwnerApproval(
        approval_id="approval-e5-20",
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
    )
    issuer = TrustedOwnerIssuer(
        authority_root="root-1",
        scope="evolution.commit",
        policy_version="policy-1",
    )
    auth = issuer.issue(
        TrustedIssuerInput(
            approval=approval,
            authority_root="root-1",
            scope="evolution.commit",
            policy_version="policy-1",
            evidence_digest=provenance.evidence_digest,
        ),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
    )

    assert isinstance(auth, ExecutionAuthorization)
    assert auth.owner_approved is True
    assert auth.approval_id == approval.approval_id
    assert auth.request_provenance == provenance.provenance_id
    assert auth.evolution_identity == provenance.evolution_identity

    request = ExecutionCommitRequest(
        authorization=auth,
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
        authorization_validity=AuthorizationValidity(
            approval.approval_id, "policy-1", "ev-1"
        ),
    )

    from gnosis.reflection.authority import require_execution_commit

    require_execution_commit(request)


def test_trusted_owner_issuer_rejects_cross_bound_approval():
    provenance = _snapshot_provenance()
    approval = OwnerApproval(
        approval_id="approval-e5-20",
        request_provenance=provenance.provenance_id,
        evolution_identity="different-evolution",
    )
    issuer = TrustedOwnerIssuer("root-1", "evolution.commit", "policy-1")

    import pytest

    with pytest.raises(PermissionError, match="evolution"):
        issuer.issue(
            TrustedIssuerInput(
                approval=approval,
                authority_root="root-1",
                scope="evolution.commit",
                policy_version="policy-1",
                evidence_digest=provenance.evidence_digest,
            ),
            request_provenance=provenance.provenance_id,
            evolution_identity=provenance.evolution_identity,
        )
