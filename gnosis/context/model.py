from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TaskContext:
    context_id: str
    project_id: str
    task_id: str
    user_scope: str
    objective: str
    current_task_state: str
    required_inputs: tuple[Any, ...] = ()
    context_references: tuple[Any, ...] = ()
    evidence_references: tuple[Any, ...] = ()
    implementation_state: str = ""
    verification_state: str = "reported"
    unresolved_findings: tuple[Any, ...] = ()
    next_permitted_action: str = ""
    available_capabilities: tuple[Any, ...] = ()
    allowed_data_sources: tuple[Any, ...] = ()
    allowed_output_destinations: tuple[Any, ...] = ()
    organization_scope: str | None = None
    created_at: str = ""
    updated_at: str = ""
    revision: int = 0
