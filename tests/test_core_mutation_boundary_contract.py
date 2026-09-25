import pytest

from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.instances.instance import Instance
from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
    SQLiteExecutionCommitAdapter,
)


def _request(candidate, parent):
    observations = {"contract": "CORE-MUTATION-BOUNDARY-01"}
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent.state_id,
        parent_state_digest=parent.state_id,
        proposed_state_digest=candidate.proposed_state.state_id,
        observations=observations,
        proposed_state_content_id=candidate.proposed_state.content_id,
        candidate_binding_digest=candidate.binding_digest(parent.state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    return ExecutionCommitRequest(
        ExecutionAuthorization(
            provenance.provenance_id, True, provenance.evolution_identity
        ),
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
    )


def test_boundary_rejects_unauthorized_mutation_without_persistence():
    conn = __import__("gnosis.storage", fromlist=["connect"]).connect()
    instance = Instance.create_root("contract-test", State(elements={"x": 1}))
    __import__("gnosis.storage", fromlist=["save_instance"]).save_instance(conn, instance)
    parent = instance.engine.state
    candidate = Candidate(parent.state_id, parent.with_elements({"x": 2}), "boundary-negative")
    record = TransitionRecord(
        parent.state_id,
        candidate.proposed_state.state_id,
        candidate.candidate_id,
        TestResult(True, ("test",)),
        True,
        "committed",
    )
    bad = ExecutionCommitRequest(
        ExecutionAuthorization("forged", False, "forged"),
        ExecutionIntentSnapshot("", "", "", "", "", "", ""),
        "forged",
        "forged",
        object(),
    )
    with pytest.raises(PermissionError):
        SQLiteExecutionCommitAdapter().commit(
            conn, instance, candidate, record, bad, actor="contract-test"
        )
    current = __import__("gnosis.storage", fromlist=["load_instance"]).load_instance(
        conn, instance.instance_id
    )
    assert current.engine.state.state_id == parent.state_id
    assert conn.execute("SELECT count(*) FROM transitions").fetchone()[0] == 0
    conn.close()


def test_boundary_rejects_candidate_substitution():
    conn = __import__("gnosis.storage", fromlist=["connect"]).connect()
    instance = Instance.create_root("contract-test", State(elements={"x": 1}))
    __import__("gnosis.storage", fromlist=["save_instance"]).save_instance(conn, instance)
    parent = instance.engine.state
    authorized = Candidate(parent.state_id, parent.with_elements({"x": 2}), "authorized")
    request = _request(authorized, parent)
    substituted = Candidate(parent.state_id, parent.with_elements({"x": 3}), "substituted")
    record = TransitionRecord(
        parent.state_id,
        substituted.proposed_state.state_id,
        substituted.candidate_id,
        TestResult(True, ("test",)),
        True,
        "committed",
    )
    with pytest.raises(PermissionError):
        SQLiteExecutionCommitAdapter().commit(
            conn, instance, substituted, record, request, actor="contract-test"
        )
    assert __import__("gnosis.storage", fromlist=["load_instance"]).load_instance(
        conn, instance.instance_id
    ).engine.state.state_id == parent.state_id
    assert conn.execute("SELECT count(*) FROM transitions").fetchone()[0] == 0
    conn.close()
