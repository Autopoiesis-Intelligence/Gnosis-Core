from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any
import sqlite3

from gnosis.ports.repositories import EvolutionMemoryRepository, ReflectionRepository
from .analyzer import ReflectionAnalyzer, ReflectionReport
from .counterexample import CounterexampleEngine
from .history import HistoricalFinding, ReflectionHistorySummary, summarize_reflection_history, unresolved_findings
from .memory_evidence import EvolutionEvidence, project_evolution_memory
from .persistence import reflection_id
from .runtime_impl import reflect


@dataclass(frozen=True)
class CumulativeReflectionReport:
    current: ReflectionReport
    history: ReflectionHistorySummary
    recurring_unresolved: tuple[HistoricalFinding, ...]
    evolution_evidence: tuple[EvolutionEvidence, ...] = ()


def reflect_with_history(
    engine: Any,
    reflection_repository: ReflectionRepository,
    evolution_memory_repository: EvolutionMemoryRepository | Any,
    *,
    minimum_repetitions: int = 2,
    instance_id: str | None = None,
) -> CumulativeReflectionReport:
    if isinstance(reflection_repository, sqlite3.Connection):
        from gnosis.adapters.sqlite_persistence import SQLiteReflectionRepository, SQLiteEvolutionMemoryRepository
        reflection_repository = SQLiteReflectionRepository(reflection_repository)
        evolution_memory_repository = SQLiteEvolutionMemoryRepository(reflection_repository._conn)
    previous = reflection_repository.list_reflection_reports()
    history = summarize_reflection_history(previous)
    recurring = unresolved_findings(previous)
    resolved_instance_id = instance_id or getattr(engine, "instance_id", None)
    records = (
        evolution_memory_repository.load_evolution_memory(resolved_instance_id)
        if resolved_instance_id
        else ()
    )
    evolution_evidence = project_evolution_memory(records)
    current = reflect(engine, minimum_repetitions=minimum_repetitions)
    current = replace(current, evolution_evidence=evolution_evidence)
    return CumulativeReflectionReport(
        current=current,
        history=history,
        recurring_unresolved=recurring,
        evolution_evidence=evolution_evidence,
    )


def reflect_and_persist(
    engine: Any,
    reflection_repository: ReflectionRepository,
    evolution_memory_repository: EvolutionMemoryRepository,
    minimum_repetitions: int = 2,
    instance_id: str | None = None,
) -> tuple[ReflectionReport, str]:
    cumulative = reflect_with_history(
        engine,
        reflection_repository,
        evolution_memory_repository,
        minimum_repetitions=minimum_repetitions,
        instance_id=instance_id,
    )
    created_at = datetime.now(timezone.utc).isoformat()
    report_key = reflection_repository.save_reflection_report(
        cumulative.current,
        created_at=created_at,
    )
    return cumulative.current, report_key


def reflection_history_context(
    reflection_repository: ReflectionRepository,
) -> tuple[dict[str, Any], ...]:
    return reflection_repository.list_reflection_reports()
