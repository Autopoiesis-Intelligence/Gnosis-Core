from gnosis.context import TaskContext, TaskContextRepository
from gnosis.storage.database import close, connect


def test_context_storage_does_not_change_core_state_tables():
    conn = connect()
    try:
        before = (
            conn.execute("SELECT COUNT(*) FROM states").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM instances").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0],
        )
        repository = TaskContextRepository(conn)
        repository.create_context(
            TaskContext(
                context_id="ctx-isolation",
                project_id="project-1",
                task_id="task-1",
                user_scope="user-1",
                objective="check boundary",
                current_task_state="OPEN",
                created_at="t0",
                updated_at="t0",
            )
        )
        repository.update_context(
            "ctx-isolation", 0, {"objective": "updated", "updated_at": "t1"}
        )
        repository.reconstruct_context("ctx-isolation")
        after = (
            conn.execute("SELECT COUNT(*) FROM states").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM instances").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0],
        )
        assert after == before
    finally:
        close(conn)
