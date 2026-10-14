from dataclasses import replace

from gnosis.context import TaskContext, TaskContextRepository
from gnosis.storage.database import close, connect


def _context(context_id, user_scope, evidence_reference):
    return TaskContext(
        context_id=context_id,
        project_id="project-1",
        task_id="task-1",
        user_scope=user_scope,
        objective="preserve context boundaries",
        current_task_state="OPEN",
        evidence_references=(evidence_reference,),
        created_at="t0",
        updated_at="t0",
    )


def test_user_scoped_contexts_keep_evidence_references_separate():
    conn = connect()
    try:
        repository = TaskContextRepository(conn)
        repository.create_context(_context("ctx-a", "user-a", "evidence-a"))
        repository.create_context(_context("ctx-b", "user-b", "evidence-b"))

        first = repository.get_context("ctx-a")
        second = repository.get_context("ctx-b")
        assert (first.user_scope, first.evidence_references) == ("user-a", ("evidence-a",))
        assert (second.user_scope, second.evidence_references) == ("user-b", ("evidence-b",))
    finally:
        close(conn)


def test_capability_declarations_round_trip_without_becoming_execution_api():
    conn = connect()
    try:
        repository = TaskContextRepository(conn)
        context = replace(
            _context("ctx-cap", "user-a", "evidence-a"),
            available_capabilities=("read_context", "request_core_commit"),
        )
        repository.create_context(context)

        recovered = repository.get_context("ctx-cap")
        assert recovered.available_capabilities == context.available_capabilities
        assert not hasattr(repository, "execute")
    finally:
        close(conn)
