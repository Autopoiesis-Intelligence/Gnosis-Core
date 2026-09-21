from __future__ import annotations
from dataclasses import dataclass
from .model import TaskContext

@dataclass(frozen=True)
class ContextHandoff:
    objective: str
    current_state: str
    implementation_state: str
    verification_state: str
    evidence_references: tuple[object, ...]
    unresolved_findings: tuple[object, ...]
    allowed_data_sources: tuple[object, ...]
    available_capabilities: tuple[object, ...]
    allowed_output_destinations: tuple[object, ...]
    next_permitted_action: str
    revision: int

    @classmethod
    def from_context(cls, context: TaskContext) -> "ContextHandoff":
        return cls(context.objective, context.current_task_state,
            context.implementation_state, context.verification_state,
            context.evidence_references, context.unresolved_findings,
            context.allowed_data_sources, context.available_capabilities,
            context.allowed_output_destinations, context.next_permitted_action,
            context.revision)
