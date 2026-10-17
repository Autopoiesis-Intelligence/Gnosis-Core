from dataclasses import replace

from gnosis.context import ContextRevisionConflict, TaskContext, TaskContextRepository
from gnosis.storage.database import close, connect


def test_all_context_fields_survive_database_reopen(tmp_path):
    database_path = tmp_path / "task-context.sqlite3"
    original = TaskContext(
        context_id="ctx-reopen",
        project_id="project-7",
        task_id="task-42",
        user_scope="user-7",
        organization_scope="org-3",
        objective="resume work without losing evidence boundaries",
        current_task_state="BLOCKED",
        required_inputs=({"name": "spec", "ref": "doc:spec-1"},),
        context_references=("chat:17", "commit:abc123"),
        evidence_references=("ci:run-44", "sha:deadbeef"),
        implementation_state="implemented-not-runtime-proven",
        verification_state="CI_PENDING",
        unresolved_findings=({"id": "gap-1", "status": "OPEN"},),
        next_permitted_action="inspect_exact_head_ci",
        available_capabilities=("read_repository", "propose_patch"),
        allowed_data_sources=("github",),
        allowed_output_destinations=("pull_request",),
        created_at="2026-10-15T00:00:00Z",
        updated_at="2026-10-15T00:01:00Z",
        revision=4,
    )

    conn = connect(database_path)
    try:
        TaskContextRepository(conn).create_context(original)
    finally:
        close(conn)

    reopened = connect(database_path)
    try:
        repository = TaskContextRepository(reopened)
        recovered = repository.get_context("ctx-reopen")
        assert recovered == original

        handoff = repository.reconstruct_context("ctx-reopen")
        assert handoff.objective == original.objective
        assert handoff.current_state == original.current_task_state
        assert handoff.implementation_state == original.implementation_state
        assert handoff.verification_state == original.verification_state
        assert handoff.evidence_references == original.evidence_references
        assert handoff.unresolved_findings == original.unresolved_findings
        assert handoff.revision == original.revision
    finally:
        close(reopened)


def test_stale_revision_conflict_leaves_entire_record_unchanged():
    conn = connect()
    try:
        repository = TaskContextRepository(conn)
        original = TaskContext(
            context_id="ctx-cas",
            project_id="project-1",
            task_id="task-1",
            user_scope="user-1",
            objective="original",
            current_task_state="OPEN",
            evidence_references=("evidence:original",),
            implementation_state="not-started",
            verification_state="NOT_RUN",
            created_at="t0",
            updated_at="t0",
        )
        repository.create_context(original)
        repository.update_context(
            "ctx-cas", 0, {"objective": "updated", "updated_at": "t1"}
        )
        before = repository.get_context("ctx-cas")

        try:
            repository.update_context(
                "ctx-cas",
                0,
                {
                    "objective": "stale-write-must-not-land",
                    "evidence_references": ("evidence:tampered",),
                    "verification_state": "PASS",
                    "updated_at": "t2",
                },
            )
        except ContextRevisionConflict:
            pass
        else:
            raise AssertionError("stale revision unexpectedly succeeded")

        assert repository.get_context("ctx-cas") == before
    finally:
        close(conn)
