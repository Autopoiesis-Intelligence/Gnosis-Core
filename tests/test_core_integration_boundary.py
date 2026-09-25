import pytest

from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.instances.instance import Instance
from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
    SQLiteExecutionCommitAdapter,
    require_execution_commit,
)


def test_external_actor_cannot_commit_without_exact_execution_authorization():
    from gnosis.storage import connect, save_instance

    conn = connect()
    instance = Instance.create_root("external-actor", State(elements={"x": 1}))
    save_instance(conn, instance)

    parent = instance.engine.state
    candidate = Candidate(
        parent.state_id,
        parent.with_elements({"x": 2}),
        "external-proposal",
    )
    record = TransitionRecord(
        parent.state_id,
        candidate.proposed_state.state_id,
        candidate.candidate_id,
        TestResult(True, ("external",)),
        True,
        "committed",
    )

    request = ExecutionCommitRequest(
        authorization=ExecutionAuthorization("", False, "", ""),
        intent_snapshot=ExecutionIntentSnapshot("", "", "", "", "", "", ""),
        request_provenance="external",
        evolution_identity="external",
        provenance=object(),
    )

    with pytest.raises(PermissionError):
        require_execution_commit(request)

    with pytest.raises(PermissionError):
        SQLiteExecutionCommitAdapter().commit(
            conn, instance, candidate, record, request, actor="external-connector"
        )

    assert instance.engine.state.elements["x"] == 1
    assert conn.execute("SELECT count(*) FROM transitions").fetchone()[0] == 0
    conn.close()


def test_context_restoration_does_not_create_execution_authority():
    from gnosis.reflection.authority import AuthorityRequest

    restored = AuthorityRequest(
        decision="ALLOW",
        rationale=("restored-context",),
        provenance="context-snapshot",
    )

    assert restored.authorized is False
    assert restored.can_activate is False
    assert restored.can_rollback is False
