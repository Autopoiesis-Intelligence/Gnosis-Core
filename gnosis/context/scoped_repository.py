from __future__ import annotations

from typing import Any, Mapping

from .model import TaskContext
from .repository import ContextNotFound, TaskContextRepository


class ScopedTaskContextRepository:
    """Apply explicit user/organization scope checks around context access.

    This is an isolation guard for application callers, not an authentication
    mechanism. The caller must obtain its scope from a trusted identity layer.
    """

    def __init__(
        self,
        repository: TaskContextRepository,
        *,
        user_scope: str,
        organization_scope: str | None = None,
    ) -> None:
        if not user_scope:
            raise ValueError("user_scope is required")
        self._repository = repository
        self._user_scope = user_scope
        self._organization_scope = organization_scope

    def create_context(self, context: TaskContext) -> TaskContext:
        self._require_scope(context)
        return self._repository.create_context(context)

    def get_context(self, context_id: str) -> TaskContext:
        context = self._repository.get_context(context_id)
        self._require_scope(context)
        return context

    def update_context(
        self, context_id: str, expected_revision: int, patch: Mapping[str, Any]
    ) -> TaskContext:
        current = self.get_context(context_id)
        if {"user_scope", "organization_scope"} & set(patch):
            raise ValueError("scope fields cannot be changed through a scoped repository")
        updated = self._repository.update_context(
            context_id, expected_revision, patch
        )
        self._require_scope(updated)
        return updated

    def reconstruct_context(self, context_id: str):
        self.get_context(context_id)
        return self._repository.reconstruct_context(context_id)

    def _require_scope(self, context: TaskContext) -> None:
        if (
            context.user_scope != self._user_scope
            or context.organization_scope != self._organization_scope
        ):
            # Do not disclose whether a context exists outside this caller's scope.
            raise ContextNotFound(context.context_id)
