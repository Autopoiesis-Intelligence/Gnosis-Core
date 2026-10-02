import pytest

from gnosis.core import Candidate, State
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.instances.instance import Instance
from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
)
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.storage import connect, load_instance, save_instance


def _provenance(candidate, parent_state):
    observations = {"candidate_id": candidate.candidate_id}
    return build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent_state.state_id,
        parent_state_digest=parent_state.state_id,
        proposed_state_digest=candidate.proposed_state.state_id,
        observations=observations,
        proposed_state_content_id=candidate.proposed_state.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_state.state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )


def test_e759_authorization_validity_must_bind_to_request_before_mutation():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)

    parent_state = instance.engine.state
    candidate = Candidate(
        parent_state.state_id,
        parent_state.with_elements({"a": 2}),
        "e759-validity-binding",
    )
    record = instance.engine.step(candidate)
    provenance = _provenance(candidate, parent_state)

    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
        approval_id="auth-bound",
    )
    request = ExecutionCommitRequest(
        authorization=authorization,
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
        authorization_validity=AuthorizationValidity(
            "different-auth",
            "policy-1",
            "ev-1",
        ),
    )

    with pytest.raises(PermissionError, match="identity mismatch"):
        SQLiteExecutionCommitAdapter().commit(
            conn,
            instance,
            candidate,
            record,
            request,
            actor="e7.59-validity-test",
        )

    persisted = load_instance(conn, instance.instance_id)
    assert persisted.engine.state.state_id == parent_state.state_id
    assert conn.execute(
        "SELECT count(*) FROM audit_events WHERE event_id=?",
        ("execution-authorization:different-auth",),
    ).fetchone()[0] == 0
    conn.close()
