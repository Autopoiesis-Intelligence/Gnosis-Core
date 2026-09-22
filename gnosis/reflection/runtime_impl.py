from __future__ import annotations

from typing import Any

from .analyzer import ReflectionAnalyzer, ReflectionReport
from .counterexample import CounterexampleEngine


def reflect(engine: Any, minimum_repetitions: int = 2) -> ReflectionReport:
    """Run one read-only self-analysis pass over canonical Engine history."""
    analyzer = ReflectionAnalyzer.from_engine(engine)
    report = analyzer.analyze(minimum_repetitions=minimum_repetitions)
    if not report.counterexamples:
        return report
    challenger = CounterexampleEngine(tuple(getattr(engine, "history", ())))
    results = tuple(
        challenger.challenge(finding, candidate)
        for finding, candidate in zip(report.findings, report.counterexamples)
    )
    return ReflectionReport(
        observations=report.observations,
        findings=report.findings,
        counterexamples=report.counterexamples,
        proposals=report.proposals,
        counterexample_results=results,
        evolution_evidence=report.evolution_evidence,
    )
