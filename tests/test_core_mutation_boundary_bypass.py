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


def test_authority_request_cannot_activate_or_rollback():
    from gnosis.reflection.authority import AuthorityRequest
    request = AuthorityRequest("ALLOW", ("contract-test",))
    assert request.authorized is False
    assert request.can_activate is False
    assert request.can_rollback is False


def test_boolean_approval_cannot_issue_execution_authorization():
    from gnosis.reflection.authority import issue_execution_authorization
    with pytest.raises(PermissionError):
        issue_execution_authorization(
            None,
            request_provenance="p",
            evolution_identity="e",
        )


def test_unbound_execution_request_fails_before_persistence():
    conn = __import__("gnosis.storage", fromlist=["connect"]).connect()
    instance = Instance.create_root("contract-test", State(elements={"x": 1}))
    __import__("gnosis.storage", fromlist=["save_instance"]).save_instance(conn, instance)
    parent = instance.engine.state
    candidate = Candidate(parent.state_id, parent.with_elements({"x": 2}), "bypass")
    bad = ExecutionCommitRequest(
        ExecutionAuthorization("p", True, "e"),
        ExecutionIntentSnapshot("", "", "", "", "", "", ""),
        "p", "e", object(),
    )
    record = TransitionRecord(
        parent.state_id, candidate.proposed_state.state_id,
        candidate.candidate_id, TestResult(True, ("test",)), True, "committed")
    with pytest.raises(PermissionError):
        require_execution_commit(bad)
    with pytest.raises(PermissionError):
        SQLiteExecutionCommitAdapter().commit(
            conn, instance, candidate, record, bad, actor="contract-test")
    assert conn.execute("SELECT count(*) FROM transitions").fetchone()[0] == 0
    conn.close()
