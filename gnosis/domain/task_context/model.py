from dataclasses import dataclass

@dataclass(frozen=True)
class ReflectionBudget:
    max_iterations: int
    current_iteration: int
    token_limit: int
    tokens_consumed: int
    max_depth: int

@dataclass(frozen=True)
class TaskContext:
    task_id: str
    root_task_id: str
    tenant_id: str
    actor_id: str
    scope_id: str
    budget: ReflectionBudget
    deterministic_seed: str
    policy_bindings: tuple[str, ...]
    created_at_ms: int
    parent_task_id: str | None = None
