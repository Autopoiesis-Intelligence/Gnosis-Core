"""Runtime entry points for Gnozis self-analysis.

Reflection remains read-only with respect to canonical Core. The persisted
entry point stores the resulting evidence so later reflection passes can use
prior findings as durable evidence rather than relying on AI conversation
history.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any

from .analyzer import ReflectionAnalyzer, ReflectionReport
from .counterexample import CounterexampleEngine, validate_counterexample_result
from .history import HistoricalFinding, ReflectionHistorySummary, summarize_reflection_history, unresolved_findings
from .persistence import list_reflection_reports, reflection_id, save_reflection_report
from .memory_evidence import EvolutionEvidence, project_evolution_memory
from .endogenous import generate_endogenous_candidates
from gnosis.storage.evolution_memory import load_evolution_memory


@dataclass(frozen=True)
class CumulativeReflectionReport:
    current: ReflectionReport
    history: ReflectionHistorySummary
    recurring_unresolved: tuple[HistoricalFinding, ...]
    evolution_evidence: tuple[EvolutionEvidence, ...] = ()


def reflect(engine: Any, minimum_repetitions: int = 2) -> ReflectionReport:
    """Run one read-only self-analysis pass over canonical Engine history."""
    analyzer = ReflectionAnalyzer.from_engine(engine)
    report = analyzer.analyze(minimum_repetitions=minimum_repetitions)
    challenger = CounterexampleEngine(engine.history)
    results = tuple(
        challenger.challenge(finding, candidate)
        for finding, candidate in zip(report.findings, report.counterexamples)
    )
    for finding, candidate, result in zip(report.findings, report.counterexamples, results):
        validate_counterexample_result(finding, candidate, result, engine.history)
    return replace(report, counterexample_results=results)



def run_endogenous(
    engine: Any,
    *,
    minimum_repetitions: int = 2,
    max_steps: int | None = None,
    conn: Any | None = None,
    instance: Any | None = None,
    actor: str = "reflection:endogenous",
) -> tuple[Any, ...]:
    """Run bounded endogenous candidates through Core, optionally durably.

    When persistence context is supplied, the reflection report, transition,
    audit evidence, and EvolutionMemoryRecord are persisted. The memory record
    remains derived evidence and is committed atomically with the transition.
    """
    if conn is not None and instance is None:
        raise ValueError("instance is required when conn is supplied")
    records: list[Any] = []
    steps = 0
    while not engine.budget.exhausted():
        if max_steps is not None and steps >= max_steps:
            break
        report = reflect(engine, minimum_repetitions=minimum_repetitions)
        report_id = None
        if conn is not None:
            report_id = save_reflection_report(
                conn,
                report,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        memory_evidence = (
            load_evolution_memory(conn, instance.instance_id)
            if conn is not None else ()
        )
        generation = generate_endogenous_candidates(
            engine.state,
            report,
            memory_evidence=memory_evidence,
            budget=engine.budget,
        )
        if not generation.candidates:
            break
        record = engine.step_select(generation.candidates)
        records.append(record)
        if conn is not None:
            selected = next(
                (candidate for candidate in generation.candidates
                 if candidate.candidate_id == record.candidate_id),
                None,
            )
            if selected is None:
                raise ValueError("canonical transition selected unknown endogenous candidate")
            proposal_id = (
                generation.proposal_ids[
                    next(
                        index for index, candidate in enumerate(generation.candidates)
                        if candidate.candidate_id == selected.candidate_id
                    )
                ]
                if generation.proposal_ids else None
            )
            from gnosis.storage.repositories import _persist_transition_with_evolution_memory
            _persist_transition_with_evolution_memory(
                conn,
                instance,
                selected,
                record,
                actor=actor,
                proposal_id=proposal_id,
                proposal_report_id=report_id,
                evidence=tuple(report.findings[0].evidence_refs) if report.findings else (),
            )
        steps += 1
        if not record.accepted:
            break
    return tuple(records)

def reflect_with_history(
    engine: Any,
    conn: Any,
    *,
    minimum_repetitions: int = 2,
    instance_id: str | None = None,
) -> CumulativeReflectionReport:
    """Run a pass while exposing durable prior reflection evidence.

    Historical evidence is context for analysis only. It does not activate
    proposals, mutate Core, or change the authority of canonical state.
    """
    previous = list_reflection_reports(conn)
    history = summarize_reflection_history(previous)
    recurring = unresolved_findings(previous)
    resolved_instance_id = instance_id or getattr(engine, "instance_id", None)
    evolution_records = load_evolution_memory(conn, resolved_instance_id) if resolved_instance_id else ()
    evolution_evidence = project_evolution_memory(evolution_records)
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
    conn: Any,
    minimum_repetitions: int = 2,
    instance_id: str | None = None,
) -> tuple[ReflectionReport, str]:
    """Run reflection, incorporate prior evidence, and persist the new pass."""
    cumulative = reflect_with_history(
        engine,
        conn,
        minimum_repetitions=minimum_repetitions,
        instance_id=instance_id,
    )
    created_at = datetime.now(timezone.utc).isoformat()
    report_key = save_reflection_report(conn, cumulative.current, created_at=created_at)
    return cumulative.current, report_key


def reflection_history_context(conn: Any) -> tuple[dict[str, Any], ...]:
    """Expose persisted reflection evidence for a future analysis layer."""
    return list_reflection_reports(conn)
