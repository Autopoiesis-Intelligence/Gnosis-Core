"""Read-only orchestration from cumulative Reflection evidence to endogenous candidates.

This layer connects durable Reflection evidence to the existing endogenous
candidate generator. It does not mutate Engine state, persist transitions,
or grant execution authority.
"""
from __future__ import annotations

from typing import Any

from .analyzer import ReflectionReport
from .endogenous import EndogenousGeneration, generate_endogenous_candidates
from .runtime import CumulativeReflectionReport


def generate_from_cumulative_reflection(
    engine: Any,
    cumulative: CumulativeReflectionReport,
    *,
    max_candidates: int | None = None,
) -> EndogenousGeneration:
    """Generate endogenous candidates using the same durable evidence seen by Reflection."""
    return generate_endogenous_candidates(
        engine.state,
        cumulative.current,
        memory_evidence=cumulative.evolution_evidence,
        max_candidates=max_candidates,
        budget=getattr(engine, "budget", None),
    )


def generate_from_reflection_report(
    engine: Any,
    report: ReflectionReport,
    *,
    memory_evidence: tuple[object, ...] = (),
    max_candidates: int | None = None,
) -> EndogenousGeneration:
    """Explicit low-level adapter for callers that already hold a reflection report."""
    return generate_endogenous_candidates(
        engine.state,
        report,
        memory_evidence=memory_evidence,
        max_candidates=max_candidates,
        budget=getattr(engine, "budget", None),
    )
