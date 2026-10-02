import pytest

from gnosis.reflection.authority import (
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
    OwnerApproval,
)
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.reflection.trusted_issuer import TrustedIssuerInput, TrustedOwnerIssuer
from tests.test_authority_boundary import _snapshot_provenance


def test_trusted_owner_issuer_to_sqlite_commit_and_receipt():
    from gnosis.core import Candidate, State
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_instance, save_instance

    conn = connect()
    try:
        instance = Instance.create_root("user-1", State(elements={"a": 1}))
        save_instance(conn, instance)
        parent_state_id = instance.engine.state.state_id
        proposed = instance.engine.state.with_elements({"b": 2})
        candidate = Candidate(parent_state_id, proposed, "e5-20")
        record = instance.engine.step(candidate)

        provenance = _snapshot_provenance()
        approval = OwnerApproval(
            approval_id="approval-e5-20-e2e",
            request_provenance=provenance.provenance_id,
            evolution_identity=provenance.evolution_identity,
        )
        issuer = TrustedOwnerIssuer("root-1", "evolution.commit", "policy-1")
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

        result = SQLiteExecutionCommitAdapter().commit(
            conn, instance, candidate, record, request, actor="user-1"
        )

        persisted = load_instance(conn, instance.instance_id)
        assert auth.owner_approved is True
        assert result.resulting_state_id == proposed.state_id
        assert persisted.engine.state.state_id == proposed.state_id
        assert result.receipt.resulting_state_digest == proposed.state_id
    finally:
        conn.close()


def test_trusted_owner_issuer_to_sqlite_rejects_cross_evolution():
    from gnosis.core import Candidate, State
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_instance, save_instance

    conn = connect()
    try:
        instance = Instance.create_root("user-1", State(elements={"a": 1}))
        save_instance(conn, instance)
        parent_state_id = instance.engine.state.state_id
        proposed = instance.engine.state.with_elements({"b": 2})
        candidate = Candidate(parent_state_id, proposed, "e5-20-cross")
        record = instance.engine.step(candidate)
        provenance = _snapshot_provenance()
        approval = OwnerApproval(
            approval_id="approval-e5-20-cross",
            request_provenance=provenance.provenance_id,
            evolution_identity="wrong-evolution",
        )
        issuer = TrustedOwnerIssuer("root-1", "evolution.commit", "policy-1")

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

        assert load_instance(conn, instance.instance_id).engine.state.state_id == parent_state_id
    finally:
        conn.close()
