"""Real SQLite commit-path rollback proof using the adapter's failure injection."""
from dataclasses import dataclass, replace
from types import SimpleNamespace

import pytest

from gnosis.core import Candidate, Engine, State
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.instances.instance import Instance
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
)
from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.storage import save_instance


@dataclass(frozen=True)
class FailureInjectionRequest(ExecutionCommitRequest):
    """Test-only immutable extension; production request remains unchanged."""

    failure_injection: str | None = None


@pytest.fixture
def real_commit_fixture(sqlite_conn):
    conn = sqlite_conn
    instance = Instance.create_root("trusted-owner", State(elements={"a": 1}))
    save_instance(conn, instance)
    parent = instance.engine.state
    candidate = Candidate(
        parent_state_id=parent.state_id,
        proposed_state=parent.with_elements({"b": 2}),
        origin="real-commit-failure-injection",
    )
    # Use a separate Engine so preparing the transition does not mutate the
    # Instance whose persisted head is under test.
    record = Engine(parent).step(candidate)
    parent_digest = canonical_digest(
        {"state_id": parent.state_id, "content_id": parent.content_id}
    )
    observations = {"fixture": "real-commit-failure-injection"}
    evidence_digest = canonical_digest(observations)
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent.state_id,
        parent_state_digest=parent_digest,
        proposed_state_digest=candidate.proposed_state.state_id,
        proposed_state_content_id=candidate.proposed_state.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_digest),
        observations=observations,
        evidence_digest=evidence_digest,
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    authorization_id = f"test-auth:{instance.instance_id}"
    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
        approval_id=authorization_id,
    )
    validity = AuthorizationValidity(
        authorization_id=authorization_id,
        policy_version="test-policy-v1",
        validity_evidence_digest=canonical_digest({"validity": "test-only"}),
    )
    request = FailureInjectionRequest(
        authorization=authorization,
        intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
        authorization_validity=validity,
    )
    return SimpleNamespace(
        conn=conn,
        instance=instance,
        candidate=candidate,
        record=record,
        request=request,
        adapter=SQLiteExecutionCommitAdapter(),
        parent_state_id=parent.state_id,
    )


def _event(conn, authorization_id):
    return conn.execute(
        "SELECT event_hash FROM audit_events WHERE event_id=?",
        (f"execution-authorization:{authorization_id}",),
    ).fetchone()


def _assert_commit_rolled_back(fixture):
    conn = fixture.conn
    request = fixture.request
    record = fixture.record
    candidate = fixture.candidate
    assert _event(conn, request.authorization.approval_id) is None
    assert conn.execute(
        "SELECT 1 FROM transitions WHERE transition_id=?", (record.transition_id,)
    ).fetchone() is None
    assert conn.execute(
        "SELECT 1 FROM candidates WHERE candidate_id=?", (candidate.candidate_id,)
    ).fetchone() is None
    assert conn.execute(
        "SELECT current_state_id FROM instances WHERE instance_id=?",
        (fixture.instance.instance_id,),
    ).fetchone()[0] == fixture.parent_state_id
    assert conn.execute(
        "SELECT 1 FROM states WHERE state_id=?",
        (candidate.proposed_state.state_id,),
    ).fetchone() is None
    assert fixture.instance.engine.state.state_id == fixture.parent_state_id


def test_real_commit_rolls_back_after_persistence_failure(real_commit_fixture):
    fixture = real_commit_fixture
    request = replace(fixture.request, failure_injection="after_audit")
    with pytest.raises(RuntimeError, match="after_audit"):
        fixture.adapter.commit(
            fixture.conn,
            fixture.instance,
            fixture.candidate,
            fixture.record,
            request,
            actor="trusted-owner",
        )
    _assert_commit_rolled_back(fixture)


def test_real_commit_failure_injection_is_not_silent(real_commit_fixture):
    fixture = real_commit_fixture
    request = replace(fixture.request, failure_injection="after_transition")
    with pytest.raises(RuntimeError, match="after_transition"):
        fixture.adapter.commit(
            fixture.conn,
            fixture.instance,
            fixture.candidate,
            fixture.record,
            request,
            actor="trusted-owner",
        )
    _assert_commit_rolled_back(fixture)
