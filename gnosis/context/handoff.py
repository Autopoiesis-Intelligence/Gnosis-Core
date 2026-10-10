from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .model import TaskContext


@dataclass(frozen=True)
class ContextHandoff:
    """Compact, terminal-independent representation of a durable task."""

    context_id: str
    project_id: str
    task_id: str
    user_scope: str
    organization_scope: str | None
    objective: str
    current_state: str
    required_inputs: tuple[Any, ...]
    context_references: tuple[Any, ...]
    implementation_state: str
    verification_state: str
    evidence_references: tuple[Any, ...]
    unresolved_findings: tuple[Any, ...]
    allowed_data_sources: tuple[Any, ...]
    available_capabilities: tuple[Any, ...]
    allowed_output_destinations: tuple[Any, ...]
    next_permitted_action: str
    created_at: str
    updated_at: str
    revision: int

    @classmethod
    def from_context(cls, context: TaskContext) -> "ContextHandoff":
        return cls(
            context_id=context.context_id,
            project_id=context.project_id,
            task_id=context.task_id,
            user_scope=context.user_scope,
            organization_scope=context.organization_scope,
            objective=context.objective,
            current_state=context.current_task_state,
            required_inputs=context.required_inputs,
            context_references=context.context_references,
            implementation_state=context.implementation_state,
            verification_state=context.verification_state,
            evidence_references=context.evidence_references,
            unresolved_findings=context.unresolved_findings,
            allowed_data_sources=context.allowed_data_sources,
            available_capabilities=context.available_capabilities,
            allowed_output_destinations=context.allowed_output_destinations,
            next_permitted_action=context.next_permitted_action,
            created_at=context.created_at,
            updated_at=context.updated_at,
            revision=context.revision,
        )
