import pytest
from gnosis.context import ContextRevisionConflict, TaskContext, TaskContextRepository
from gnosis.storage.database import close, connect

def make_context():
    return TaskContext(
        context_id="ctx-1", project_id="project-1", task_id="task-1",
        user_scope="user-1", objective="test", current_task_state="OPEN",
        evidence_references=("research-ref-1",), next_permitted_action="VERIFY",
        created_at="t0", updated_at="t0",
    )

def test_create_get_and_reconstruct():
    conn=connect()
    try:
        repo=TaskContextRepository(conn)
        repo.create_context(make_context())
        assert repo.get_context("ctx-1") == make_context()
        handoff=repo.reconstruct_context("ctx-1")
        assert handoff.objective == "test"
        assert handoff.next_permitted_action == "VERIFY"
    finally:
        close(conn)

def test_revision_cas_rejects_stale_update_without_mutation():
    conn=connect()
    try:
        repo=TaskContextRepository(conn)
        repo.create_context(make_context())
        updated=repo.update_context("ctx-1",0,{"objective":"changed","updated_at":"t1"})
        assert updated.revision == 1
        with pytest.raises(ContextRevisionConflict):
            repo.update_context("ctx-1",0,{"objective":"must-not-apply","updated_at":"t2"})
        current=repo.get_context("ctx-1")
        assert current.objective == "changed"
        assert current.revision == 1
    finally:
        close(conn)

def test_reopen_persists_context():
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        path=f"{d}/context.db"
        conn=connect(path)
        TaskContextRepository(conn).create_context(make_context())
        close(conn)
        conn=connect(path)
        try:
            assert TaskContextRepository(conn).get_context("ctx-1").objective == "test"
        finally:
            close(conn)

def test_immutable_identity_and_revision_fields_are_rejected():
    conn=connect()
    try:
        repo=TaskContextRepository(conn)
        repo.create_context(make_context())
        with pytest.raises(ValueError):
            repo.update_context("ctx-1",0,{"context_id":"other"})
        with pytest.raises(ValueError):
            repo.update_context("ctx-1",0,{"revision":9})
    finally:
        close(conn)
