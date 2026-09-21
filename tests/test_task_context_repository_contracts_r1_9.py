import pytest

from gnosis.adapters.sqlite_persistence import SQLiteTaskContextRepository
from gnosis.context import ContextRevisionConflict, TaskContext
from gnosis.storage import connect


def make_context():
    return TaskContext(
        context_id="ctx-contract", project_id="project-1", task_id="task-1",
        user_scope="user-1", objective="test", current_task_state="OPEN",
        evidence_references=("opaque-ref-1",), next_permitted_action="VERIFY",
        created_at="t0", updated_at="t0",
    )


def test_task_context_adapter_preserves_revision_cas_and_recovery():
    conn = connect(":memory:")
    repo = SQLiteTaskContextRepository(conn)
    repo.create_context(make_context())
    updated = repo.update_context("ctx-contract", 0, {"objective": "changed", "updated_at": "t1"})
    assert updated.revision == 1
    with pytest.raises(ContextRevisionConflict):
        repo.update_context("ctx-contract", 0, {"objective": "must-not-apply"})
    assert repo.get_context("ctx-contract").objective == "changed"
    assert repo.reconstruct_context("ctx-contract").next_permitted_action == "VERIFY"


def test_task_context_identity_and_revision_are_not_mutable():
    conn = connect(":memory:")
    repo = SQLiteTaskContextRepository(conn)
    repo.create_context(make_context())
    with pytest.raises(ValueError):
        repo.update_context("ctx-contract", 0, {"context_id": "other"})
    with pytest.raises(ValueError):
        repo.update_context("ctx-contract", 0, {"revision": 9})
