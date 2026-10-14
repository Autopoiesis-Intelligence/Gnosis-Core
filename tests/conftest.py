import pytest

from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.storage import connect, save_instance
from gnosis.storage.repositories import _persist_transition
from gnosis.evolution.provenance import build_provenance, canonical_digest


@pytest.fixture
def sqlite_conn():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def provenance():
    observations = {"result": "ok"}
    evidence = canonical_digest(observations)
    return build_provenance(
        candidate_id="c1",
        parent_state_id="s1",
        parent_state_digest="pd",
        proposed_state_digest=canonical_digest({"state": "new"}),
        observations=observations,
        evidence_digest=evidence,
        proposed_state_content_id="content-1",
        candidate_binding_digest="binding-1",
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )


@pytest.fixture
def persisted_transition():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "test")
    record = instance.engine.step(candidate)
    _persist_transition(conn, instance, candidate, record, actor="test")
    return conn, instance, record


@pytest.fixture
def real_commit_fixture():
    """Build a real authorized SQLite commit path for rollback injection tests."""
    from dataclasses import dataclass

    from gnosis.reflection.authority import (
        ExecutionAuthorization,
        ExecutionCommitRequest,
        ExecutionIntentSnapshot,
    )
    from gnosis.reflection.authorization_validity import AuthorizationValidity
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter

    @dataclass
    class _Fixture:
        conn: object
        instance: object
        candidate: object
        record: object
        request: object
        adapter: object

        def __iter__(self):
            yield self.conn
            yield self.instance
            yield self.candidate
            yield self.record
            yield self.request

    conn = connect()
    instance = Instance.create_root("trusted-owner", State(elements={"a": 1}))
    save_instance(conn, instance)
    parent = instance.engine.state
    candidate = Candidate(parent.state_id, parent.with_elements({"b": 2}), "failure-injection")
    record = instance.engine.step(candidate)
    observations = {"result": "failure-injection-fixture"}
    validity = AuthorizationValidity("auth-failure-injection", "policy-1", "ev-1")
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
    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
        approval_id=validity.authorization_id,
    )
    request = ExecutionCommitRequest(
        authorization=authorization,
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
        authorization_validity=validity,
    )
    return _Fixture(conn, instance, candidate, record, request, SQLiteExecutionCommitAdapter())
