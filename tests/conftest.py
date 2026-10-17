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
    """Build a real SQLite execution path for rollback/failure-injection tests.

    The mutable wrapper is test-only: production ExecutionCommitRequest remains
    frozen. It carries the adapter's existing failure_injection test hook without
    adding a production field or changing authorization behavior.
    """
    from types import SimpleNamespace

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
    from gnosis.storage import connect, save_instance

    conn = connect()
    instance = Instance.create_root("rollback-test-owner", State(elements={"seed": 1}))
    save_instance(conn, instance)
    parent_state = instance.engine.state
    candidate = Candidate(
        parent_state.state_id,
        parent_state.with_elements({"result": "candidate"}),
        "real-commit-failure-injection",
    )
    record = instance.engine.step(candidate)
    observations = {"fixture": "real-commit-failure-injection"}
    built_provenance = build_provenance(
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
    # The current canonical-identity checker and EvidenceProvenance property
    # disagree on evaluator identity fields. Keep this fixture aligned to the
    # checker's exact contract without modifying production code.
    from gnosis.reflection.authority import _canonical_evolution_identity

    provenance = SimpleNamespace(
        **vars(built_provenance),
        provenance_id=built_provenance.provenance_id,
        evolution_identity="",
    )
    provenance.evolution_identity = _canonical_evolution_identity(provenance)
    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
        approval_id="approval-real-commit-fixture",
    )
    request = ExecutionCommitRequest(
        authorization=authorization,
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
        authorization_validity=AuthorizationValidity(
            authorization_id=authorization.approval_id,
            policy_version="test-policy-v1",
            validity_evidence_digest="test-evidence-v1",
        ),
    )
    # ExecutionCommitRequest is frozen; keep the injection knob test-only.
    mutable_request = SimpleNamespace(
        authorization=request.authorization,
        intent_snapshot=request.intent_snapshot,
        request_provenance=request.request_provenance,
        evolution_identity=request.evolution_identity,
        provenance=request.provenance,
        authorization_validity=request.authorization_validity,
        failure_injection=None,
    )

    class RealCommitFixture:
        adapter = SQLiteExecutionCommitAdapter()

        def __iter__(self):
            return iter((conn, instance, candidate, record, mutable_request))

    fixture = RealCommitFixture()
    try:
        yield fixture
    finally:
        conn.close()
