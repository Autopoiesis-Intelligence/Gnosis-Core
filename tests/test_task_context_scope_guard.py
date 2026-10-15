import pytest

from gnosis.context import ContextNotFound, TaskContext, TaskContextRepository
from gnosis.context.scoped_repository import ScopedTaskContextRepository
from gnosis.storage.database import close, connect


def _context(context_id, user_scope, organization_scope=None):
    return TaskContext(
        context_id=context_id,
        project_id="project-1",
        task_id="task-1",
        user_scope=user_scope,
        organization_scope=organization_scope,
        objective="scope boundary",
        current_task_state="OPEN",
        created_at="t0",
        updated_at="t0",
    )


def test_scoped_repository_denies_cross_user_and_cross_organization_reads():
    conn = connect()
    try:
        base = TaskContextRepository(conn)
        base.create_context(_context("personal-a", "user-a"))
        base.create_context(_context("org-a", "user-a", "org-a"))
        base.create_context(_context("personal-b", "user-b"))

        personal_a = ScopedTaskContextRepository(base, user_scope="user-a")
        org_a = ScopedTaskContextRepository(
            base, user_scope="user-a", organization_scope="org-a"
        )
        with pytest.raises(ContextNotFound):
            personal_a.get_context("personal-b")
        with pytest.raises(ContextNotFound):
            personal_a.get_context("org-a")
        with pytest.raises(ContextNotFound):
            org_a.get_context("personal-a")
        assert org_a.get_context("org-a").organization_scope == "org-a"
    finally:
        close(conn)


def test_scoped_repository_rejects_scope_mutation_and_wrong_scope_creation():
    conn = connect()
    try:
        base = TaskContextRepository(conn)
        scoped = ScopedTaskContextRepository(base, user_scope="user-a")
        scoped.create_context(_context("ctx-a", "user-a"))

        with pytest.raises(ValueError, match="scope fields cannot be changed"):
            scoped.update_context("ctx-a", 0, {"user_scope": "user-b"})

        with pytest.raises(ValueError, match="scope fields cannot be changed"):
            scoped.update_context("ctx-a", 0, {"organization_scope": "org-b"})

        other_user = ScopedTaskContextRepository(base, user_scope="user-b")
        with pytest.raises(ContextNotFound):
            other_user.get_context("ctx-a")

        with pytest.raises(ContextNotFound):
            scoped.create_context(_context("ctx-wrong", "user-b"))
    finally:
        close(conn)
