import json
import sqlite3
from datetime import datetime

import pytest

from gnosis.context import ContextRevisionConflict, TaskContext, TaskContextRepository
from gnosis.storage.database import close, connect


def make_context(**overrides):
    values = dict(
        context_id="ctx-1",
        project_id="project-1",
        task_id="task-1",
        user_scope="user-1",
        organization_scope="org-1",
        objective="resume implementation",
        current_task_state="active",
        required_inputs=("input-1",),
        context_references=("context-ref-1",),
        evidence_references=("evidence-ref-1",),
        implementation_state="partially_implemented",
        verification_state="reported",
        unresolved_findings=("finding-1",),
        next_permitted_action="VERIFY",
        available_capabilities=("pytest",),
        allowed_data_sources=("repo-read",),
        allowed_output_destinations=("local-report",),
        created_at="t0",
        updated_at="t0",
        revision=0,
    )
    values.update(overrides)
    return TaskContext(**values)


def test_create_read_round_trip_preserves_every_field():
    conn = connect()
    try:
        repo = TaskContextRepository(conn)
        expected = make_context()
        repo.create_context(expected)
        assert repo.get_context(expected.context_id) == expected
    finally:
        close(conn)


def test_handoff_preserves_complete_task_identity_and_recovery_semantics():
    conn = connect()
    try:
        repo = TaskContextRepository(conn)
        expected = make_context()
        repo.create_context(expected)
        handoff = repo.reconstruct_context(expected.context_id)
        assert handoff.context_id == expected.context_id
        assert handoff.project_id == expected.project_id
        assert handoff.task_id == expected.task_id
        assert handoff.user_scope == expected.user_scope
        assert handoff.organization_scope == expected.organization_scope
        assert handoff.objective == expected.objective
        assert handoff.current_state == expected.current_task_state
        assert handoff.required_inputs == expected.required_inputs
        assert handoff.context_references == expected.context_references
        assert handoff.implementation_state == expected.implementation_state
        assert handoff.verification_state == expected.verification_state
        assert handoff.evidence_references == expected.evidence_references
        assert handoff.unresolved_findings == expected.unresolved_findings
        assert handoff.allowed_data_sources == expected.allowed_data_sources
        assert handoff.available_capabilities == expected.available_capabilities
        assert handoff.allowed_output_destinations == expected.allowed_output_destinations
        assert handoff.next_permitted_action == expected.next_permitted_action
        assert handoff.created_at == expected.created_at
        assert handoff.updated_at == expected.updated_at
        assert handoff.revision == expected.revision
    finally:
        close(conn)


def test_revision_increments_and_stale_update_leaves_stored_bytes_unchanged():
    conn = connect()
    try:
        repo = TaskContextRepository(conn)
        repo.create_context(make_context())
        updated = repo.update_context("ctx-1", 0, {"objective": "changed", "updated_at": "t1"})
        assert updated.revision == 1
        before = conn.execute(
            "SELECT * FROM task_contexts WHERE context_id=?", ("ctx-1",)
        ).fetchone()
        before_bytes = tuple(before)
        with pytest.raises(ContextRevisionConflict):
            repo.update_context("ctx-1", 0, {"objective": "must-not-apply", "updated_at": "t2"})
        after = conn.execute(
            "SELECT * FROM task_contexts WHERE context_id=?", ("ctx-1",)
        ).fetchone()
        assert tuple(after) == before_bytes
    finally:
        close(conn)


def test_close_reopen_and_fresh_repository_reconstructs_full_context(tmp_path):
    path = tmp_path / "context.db"
    conn = connect(path)
    TaskContextRepository(conn).create_context(make_context())
    close(conn)

    fresh_conn = connect(path)
    try:
        fresh_repo = TaskContextRepository(fresh_conn)
        assert fresh_repo.get_context("ctx-1") == make_context()
        handoff = fresh_repo.reconstruct_context("ctx-1")
        assert handoff.evidence_references == ("evidence-ref-1",)
        assert handoff.next_permitted_action == "VERIFY"
    finally:
        close(fresh_conn)


@pytest.mark.parametrize(
    "field,value",
    [
        ("context_id", "other-context"),
        ("project_id", "other-project"),
        ("task_id", "other-task"),
        ("user_scope", "other-user"),
        ("organization_scope", "other-org"),
        ("created_at", "t9"),
        ("revision", 9),
    ],
)
def test_identity_scope_and_revision_fields_cannot_be_patched(field, value):
    conn = connect()
    try:
        repo = TaskContextRepository(conn)
        repo.create_context(make_context())
        with pytest.raises(ValueError):
            repo.update_context("ctx-1", 0, {field: value})
        assert repo.get_context("ctx-1") == make_context()
    finally:
        close(conn)


def test_task_contexts_remain_separate_across_user_and_organization_scopes():
    conn = connect()
    try:
        repo = TaskContextRepository(conn)
        personal = make_context(context_id="personal", user_scope="user-1", organization_scope=None)
        organizational = make_context(
            context_id="org-task", user_scope="user-1", organization_scope="org-2"
        )
        other_user = make_context(context_id="other-user", user_scope="user-2", organization_scope=None)
        for context in (personal, organizational, other_user):
            repo.create_context(context)
        assert repo.get_context("personal").organization_scope is None
        assert repo.get_context("org-task").organization_scope == "org-2"
        assert repo.get_context("other-user").user_scope == "user-2"
        assert repo.reconstruct_context("personal").context_id == "personal"
    finally:
        close(conn)


@pytest.mark.parametrize("state", ["OPEN", "", "unknown", "in_progress"])
def test_invalid_task_states_are_rejected(state):
    conn = connect()
    try:
        with pytest.raises(ValueError, match="current_task_state"):
            TaskContextRepository(conn).create_context(make_context(current_task_state=state))
    finally:
        close(conn)


@pytest.mark.parametrize("state", ["", "verified", "PASS", "unknown"])
def test_invalid_verification_states_are_rejected(state):
    conn = connect()
    try:
        with pytest.raises(ValueError, match="verification_state"):
            TaskContextRepository(conn).create_context(make_context(verification_state=state))
    finally:
        close(conn)


def test_capabilities_are_reported_as_metadata_not_permissions():
    conn = connect()
    try:
        repo = TaskContextRepository(conn)
        repo.create_context(make_context(available_capabilities=("execute",)))
        handoff = repo.reconstruct_context("ctx-1")
        assert handoff.available_capabilities == ("execute",)
        assert not hasattr(handoff, "authorized_actions")
        assert not hasattr(handoff, "permission_grants")
    finally:
        close(conn)


def test_evidence_references_are_preserved_as_opaque_identifiers():
    conn = connect()
    try:
        repo = TaskContextRepository(conn)
        ref = {"source": "research", "locator": "record-17"}
        repo.create_context(make_context(evidence_references=(ref,)))
        recovered = repo.get_context("ctx-1")
        assert recovered.evidence_references == (ref,)
        assert "research" in conn.execute(
            "SELECT evidence_references FROM task_contexts WHERE context_id='ctx-1'"
        ).fetchone()[0]
    finally:
        close(conn)


def test_context_repository_does_not_create_core_or_memory_tables_in_plain_database():
    conn = sqlite3.connect(":memory:", isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        repo = TaskContextRepository(conn)
        repo.create_context(make_context())
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert tables == {"task_contexts"}
    finally:
        conn.close()


def test_cli_can_recover_context_without_initializing_core_schema(tmp_path, monkeypatch, capsys):
    from gnosis.context import cli

    path = tmp_path / "standalone-context.db"
    conn = sqlite3.connect(path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        TaskContextRepository(conn).create_context(make_context())
    finally:
        conn.close()

    monkeypatch.setattr(
        "sys.argv",
        ["gnosis-context", "--context-db", str(path), "--context-id", "ctx-1"],
    )
    cli.main()
    output = json.loads(capsys.readouterr().out)
    assert output["context_id"] == "ctx-1"
    assert output["task_id"] == "task-1"
    assert output["next_permitted_action"] == "VERIFY"

    check = sqlite3.connect(path)
    try:
        tables = {
            row[0]
            for row in check.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert tables == {"task_contexts"}
    finally:
        check.close()


def test_cli_recovery_does_not_create_context_schema_in_an_empty_database(tmp_path, monkeypatch):
    from gnosis.context import cli

    path = tmp_path / "empty.db"
    sqlite3.connect(path).close()
    monkeypatch.setattr(
        "sys.argv",
        ["gnosis-context", "--context-db", str(path), "--context-id", "missing"],
    )
    with pytest.raises(SystemExit, match="does not contain task_contexts table"):
        cli.main()

    check = sqlite3.connect(path)
    try:
        tables = {
            row[0]
            for row in check.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert tables == set()
    finally:
        check.close()


def test_context_default_verification_state_is_valid_and_persistable():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        repo = TaskContextRepository(conn)
        context = TaskContext(
            context_id="ctx-default-verification",
            project_id="project-1",
            task_id="task-default",
            user_scope="user-1",
            objective="verify default state",
            current_task_state="proposed",
        )
        stored = repo.create_context(context)
        assert stored.verification_state == "reported"
        assert repo.get_context(context.context_id).verification_state == "reported"
    finally:
        conn.close()

@pytest.mark.parametrize(
    "initial,target,allowed",
    [
        ("proposed", "active", True),
        ("proposed", "accepted", False),
        ("active", "blocked", True),
        ("blocked", "active", True),
        ("awaiting_review", "accepted", True),
        ("accepted", "corrective", True),
        ("closed", "active", False),
        ("verified", "accepted", True),
    ],
)
def test_task_state_transition_matrix(initial, target, allowed):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        repo = TaskContextRepository(conn)
        repo.create_context(make_context(current_task_state=initial))
        if allowed:
            updated = repo.update_context("ctx-1", 0, {"current_task_state": target})
            assert updated.current_task_state == target
            assert updated.revision == 1
        else:
            with pytest.raises(ValueError, match="invalid task state transition"):
                repo.update_context("ctx-1", 0, {"current_task_state": target})
            assert repo.get_context("ctx-1").current_task_state == initial
            assert repo.get_context("ctx-1").revision == 0
    finally:
        conn.close()


def test_same_task_state_can_be_kept_while_updating_other_fields():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        repo = TaskContextRepository(conn)
        repo.create_context(make_context(current_task_state="active"))
        updated = repo.update_context("ctx-1", 0, {"objective": "updated objective"})
        assert updated.current_task_state == "active"
        assert updated.objective == "updated objective"
        assert updated.revision == 1
    finally:
        conn.close()

TASK_STATE_TRANSITION_CONTRACT = {
    "proposed": {"active", "blocked", "closed"},
    "active": {"blocked", "awaiting_review", "corrective", "verified", "closed"},
    "blocked": {"active", "corrective", "closed"},
    "awaiting_review": {"active", "blocked", "corrective", "verified", "accepted"},
    "corrective": {"active", "blocked", "awaiting_review", "closed"},
    "verified": {"active", "corrective", "accepted", "closed"},
    "accepted": {"corrective", "closed"},
    "closed": set(),
}


@pytest.mark.parametrize(
    "initial,target",
    [
        (initial, target)
        for initial in TASK_STATE_TRANSITION_CONTRACT
        for target in TASK_STATE_TRANSITION_CONTRACT
        if initial != target
    ],
)
def test_every_task_state_transition_matches_contract_matrix(initial, target):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    try:
        repo = TaskContextRepository(conn)
        repo.create_context(make_context(current_task_state=initial))
        allowed = target in TASK_STATE_TRANSITION_CONTRACT[initial]
        if allowed:
            updated = repo.update_context("ctx-1", 0, {"current_task_state": target})
            assert updated.current_task_state == target
            assert updated.revision == 1
        else:
            with pytest.raises(ValueError, match="invalid task state transition"):
                repo.update_context("ctx-1", 0, {"current_task_state": target})
            assert repo.get_context("ctx-1").current_task_state == initial
            assert repo.get_context("ctx-1").revision == 0
    finally:
        conn.close()


def test_cli_recovery_does_not_create_a_missing_database_file(tmp_path, monkeypatch):
    from gnosis.context import cli

    path = tmp_path / "does-not-exist.db"
    monkeypatch.setattr(
        "sys.argv",
        ["gnosis-context", "--context-db", str(path), "--context-id", "ctx-1"],
    )
    with pytest.raises(SystemExit, match="does not exist"):
        cli.main()
    assert not path.exists()


def test_update_refreshes_updated_at_when_caller_does_not_supply_it():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    original_timestamp = "2000-01-01T00:00:00+00:00"
    try:
        repo = TaskContextRepository(conn)
        repo.create_context(make_context(updated_at=original_timestamp))
        updated = repo.update_context("ctx-1", 0, {"objective": "changed"})
        assert datetime.fromisoformat(updated.updated_at) > datetime.fromisoformat(original_timestamp)
        assert repo.get_context("ctx-1").updated_at == updated.updated_at
    finally:
        conn.close()



def test_mutating_reconstructed_handoff_does_not_change_persisted_context_and_remains_json_serializable():
    from dataclasses import asdict

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    evidence = {"source": "research", "locator": "record-17"}
    try:
        repo = TaskContextRepository(conn)
        repo.create_context(make_context(evidence_references=(evidence,)))

        handoff = repo.reconstruct_context("ctx-1")
        handoff.evidence_references[0]["locator"] = "mutated-in-memory"
        encoded = json.dumps(asdict(handoff), ensure_ascii=False, sort_keys=True)
        assert "mutated-in-memory" in encoded

        persisted = repo.get_context("ctx-1")
        assert persisted.evidence_references == ({"source": "research", "locator": "record-17"},)
    finally:
        conn.close()
