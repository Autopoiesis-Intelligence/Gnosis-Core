"""Read-only reflection gate over repository capabilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from gnosis.ports.repositories import EvolutionRepository

from .diagnostic_artifact import build_artifact
from .persistence import reflection_id
from .runtime import reflect_with_history
from .self_diagnostic import diagnose


@dataclass(frozen=True)
class ReflectionGateResult:
    passed: bool
    instance_id: str
    transition_count: int
    durable_graph_verified: bool
    recovery_state_id: str
    report_id: str
    artifact: dict[str, Any]
    reasons: tuple[str, ...] = ()


def run_reflection_gate(
    engine: Any,
    repository: EvolutionRepository,
    instance_id: str,
    *,
    minimum_repetitions: int = 2,
) -> ReflectionGateResult:
    """Verify durable reflection evidence without owning persistence."""
    reasons: list[str] = []
    history = tuple(getattr(engine, "history", ()))
    if not history:
        reasons.append("canonical Core history is empty")

    try:
        transition_count, _ = repository.verify_durable_graph()
        durable_ok = True
    except Exception as exc:
        transition_count = 0
        durable_ok = False
        reasons.append(f"durable graph verification failed: {type(exc).__name__}")

    try:
        recovered = repository.recover_instance(instance_id)
        recovery_state_id = recovered.engine.state.state_id
    except Exception as exc:
        recovery_state_id = ""
        reasons.append(f"recovery failed: {type(exc).__name__}")

    if history and recovery_state_id and recovery_state_id != engine.state.state_id:
        reasons.append("recovered state does not match canonical engine state")

    try:
        cumulative = reflect_with_history(engine, repository, minimum_repetitions=minimum_repetitions)
        report = cumulative.current
        diagnostic = diagnose(history, minimum_repetitions=minimum_repetitions)
        artifact = build_artifact(diagnostic, artifact_id=reflection_id(report))
        report_id = reflection_id(report)
    except Exception as exc:
        report_id = ""
        artifact = {}
        reasons.append(f"reflection evidence generation failed: {type(exc).__name__}")

    if not durable_ok:
        reasons.append("instance is not proven durable")
    if artifact.get("authority") != "READ_ONLY":
        reasons.append("diagnostic artifact is not explicitly read-only")

    return ReflectionGateResult(
        passed=not reasons,
        instance_id=instance_id,
        transition_count=transition_count if transition_count else len(history),
        durable_graph_verified=durable_ok,
        recovery_state_id=recovery_state_id,
        report_id=report_id,
        artifact=artifact,
        reasons=tuple(reasons),
    )
