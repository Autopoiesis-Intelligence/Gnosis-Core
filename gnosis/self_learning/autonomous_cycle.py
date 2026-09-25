"""Bounded endogenous evolution orchestration outside the Core trust boundary."""
from dataclasses import dataclass

from gnosis.core import Engine, TransitionRecord
from gnosis.reflection.analyzer import ReflectionAnalyzer
from gnosis.reflection.endogenous import EndogenousGeneration, generate_endogenous_candidates


@dataclass(frozen=True)
class AutonomousCycleResult:
    generation: EndogenousGeneration
    transition: TransitionRecord | None


def run_one_endogenous_cycle(engine: Engine) -> AutonomousCycleResult:
    """Observe canonical history, derive proposals, generate candidates, then select.

    This is orchestration, not a second Core evolution engine. All state mutation
    remains in Engine.step_select(), so Core Test/Select semantics stay authoritative.
    """
    analyzer = ReflectionAnalyzer.from_engine(engine)
    report = analyzer.analyze(minimum_repetitions=2)
    generation = generate_endogenous_candidates(
        engine.state,
        report,
        budget=engine.budget,
    )
    if not generation.candidates:
        return AutonomousCycleResult(generation=generation, transition=None)
    transition = engine.step_select(generation.candidates)
    return AutonomousCycleResult(generation=generation, transition=transition)
