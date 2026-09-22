from __future__ import annotations

from typing import Any

from .analyzer import ReflectionAnalyzer, ReflectionReport


def reflect(engine: Any, minimum_repetitions: int = 2) -> ReflectionReport:
    """Run one read-only self-analysis pass over canonical Engine history."""
    analyzer = ReflectionAnalyzer.from_engine(engine)
    return analyzer.analyze(minimum_repetitions=minimum_repetitions)
