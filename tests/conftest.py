import pytest

from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.storage import connect, save_instance


@pytest.fixture
def sqlite_conn():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


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

from gnosis.storage.repositories import _persist_transition


@pytest.fixture
def real_commit_fixture():
    from types import SimpleNamespace
    from gnosis.core import Candidate, State
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.reflection.authority import (
        ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot,
        SQLiteExecutionCommitAdapter,
    )
    from gnosis.reflection.authorization_validity import AuthorizationValidity

    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    parent_state_id = instance.engine.state.state_id
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(parent_state_id, proposed, "failure-injection")
    record = instance.engine.step(candidate)
    observations = {"result": "ok"}
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=proposed.state_id,
        observations=observations,
        proposed_state_content_id=proposed.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    auth = ExecutionAuthorization(
        provenance.provenance_id, True, provenance.evolution_identity,
        approval_id="failure-injection-approval",
    )
    validity = AuthorizationValidity(
        auth.approval_id, "policy-1", provenance.evidence_digest
    )
    request = ExecutionCommitRequest(
        auth,
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
        validity,
    )
    return SimpleNamespace(
        conn=conn, instance=instance, candidate=candidate, record=record,
        request=request, adapter=SQLiteExecutionCommitAdapter(),
    )


@pytest.fixture
def provenance():
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    observations = {"fixture": "provenance"}
    return build_provenance(
        candidate_id="candidate-fixture",
        parent_state_id="parent-fixture",
        parent_state_digest="parent-fixture",
        proposed_state_digest="proposed-fixture",
        proposed_state_content_id="content-fixture",
        candidate_binding_digest="binding-fixture",
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="PASS",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
