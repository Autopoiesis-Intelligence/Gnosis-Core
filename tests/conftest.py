from dataclasses import dataclass
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


@dataclass
class RealCommitFixture:
    conn: object
    instance: object
    candidate: object
    record: object
    request: object
    adapter: object

    def __iter__(self):
        # Preserve the original five-value test unpacking while exposing adapter.
        yield self.conn
        yield self.instance
        yield self.candidate
        yield self.record
        yield self.request


@pytest.fixture
def real_commit_fixture():
    from gnosis.core import Candidate, State, TestResult, TransitionRecord
    from gnosis.evolution.provenance import canonical_digest, build_provenance
    from gnosis.reflection.authority import (
        ExecutionAuthorization,
        ExecutionCommitRequest,
        ExecutionIntentSnapshot,
    )
    from gnosis.reflection.authorization_validity import AuthorizationValidity
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter

    conn = connect()
    try:
        instance = Instance.create_root("fixture-owner", State(elements={"root": 1}))
        save_instance(conn, instance)
        parent_state = instance.engine.state
        proposed_state = parent_state.with_elements({"next": 2})
        candidate = Candidate(parent_state.state_id, proposed_state, "real-commit-fixture")
        record = TransitionRecord(
            from_state_id=parent_state.state_id,
            to_state_id=proposed_state.state_id,
            candidate_id=candidate.candidate_id,
            test_result=TestResult(passed=True, reasons=()),
            accepted=True,
            reason="fixture transition",
            test_rule_id="test:real-commit-fixture",
        )
        observations = {"fixture": "real-commit"}
        evidence_digest = canonical_digest(observations)
        provenance = build_provenance(
            candidate_id=candidate.candidate_id,
            parent_state_id=parent_state.state_id,
            parent_state_digest=parent_state.state_id,
            proposed_state_digest=proposed_state.state_id,
            proposed_state_content_id=proposed_state.content_id,
            candidate_binding_digest=candidate.binding_digest(parent_state.state_id),
            observations=observations,
            evidence_digest=evidence_digest,
            evaluation_status="PASS",
            shadow_status="UNCHANGED",
            invariant_status="PRESERVED",
            governance_decision="ALLOW",
        )
        authorization = ExecutionAuthorization(
            request_provenance=provenance.provenance_id,
            owner_approved=True,
            evolution_identity=provenance.evolution_identity,
            approval_id="real-commit-fixture-auth",
        )
        validity = AuthorizationValidity(
            authorization_id=authorization.approval_id,
            policy_version="fixture-policy-v1",
            validity_evidence_digest="fixture-validity-evidence",
        )
        request = ExecutionCommitRequest(
            authorization=authorization,
            intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
            request_provenance=provenance.provenance_id,
            evolution_identity=provenance.evolution_identity,
            provenance=provenance,
            authorization_validity=validity,
        )
        yield RealCommitFixture(
            conn=conn,
            instance=instance,
            candidate=candidate,
            record=record,
            request=request,
            adapter=SQLiteExecutionCommitAdapter(),
        )
    finally:
        conn.close()
