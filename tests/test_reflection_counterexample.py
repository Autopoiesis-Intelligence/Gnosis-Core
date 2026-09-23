import pytest
from gnosis.core import TestResult, TransitionRecord
from gnosis.reflection import CounterexampleEngine, ReflectionAnalyzer, reflect
from gnosis.reflection.counterexample import CounterexampleResult


def _record(index: int, accepted: bool, candidate_id: str, reason: str) -> TransitionRecord:
    return TransitionRecord(
        from_state_id=f"state:{index}",
        to_state_id=f"state:{index + 1}",
        candidate_id=candidate_id,
        test_result=TestResult(passed=accepted, reasons=(reason,)),
        accepted=accepted,
        reason=reason,
    )


def test_counterexample_is_inconclusive_when_no_accepted_match_exists():
    history = (
        _record(0, False, "c1", "repeated failure"),
        _record(1, False, "c2", "repeated failure"),
    )
    analyzer = ReflectionAnalyzer(history)
    report = analyzer.analyze()
    result = CounterexampleEngine(history).challenge(
        report.findings[0], report.counterexamples[0]
    )
    assert result.status == "INCONCLUSIVE"


def test_counterexample_refutes_unconditional_rejection_hypothesis():
    history = (
        _record(0, False, "same", "repeated failure"),
        _record(1, False, "same", "repeated failure"),
        _record(2, True, "same", "committed"),
    )
    analyzer = ReflectionAnalyzer(history)
    report = analyzer.analyze()
    result = CounterexampleEngine(history).challenge(
        report.findings[0], report.counterexamples[0]
    )
    assert result.status == "REFUTED"
    assert result.evidence_refs == (_record(2, True, "same", "committed").transition_id,)


def test_runtime_reflection_executes_counterexample_stage_without_mutating_history():
    history = [
        _record(0, False, "c1", "repeated failure"),
        _record(1, False, "c2", "repeated failure"),
    ]

    class EngineLike:
        def __init__(self, history):
            self.history = history

    engine = EngineLike(history)
    report = reflect(engine)

    assert report.counterexample_results[0].status == "INCONCLUSIVE"
    assert engine.history == history


def test_counterexample_result_rejects_foreign_candidate():
    from gnosis.reflection.counterexample import CounterexampleResult, validate_counterexample_result
    history=(_record(0, False, "c1", "repeated failure"),)
    analyzer=ReflectionAnalyzer(history)
    report=analyzer.analyze()
    finding, candidate = report.findings[0], report.counterexamples[0]
    result=CounterexampleResult(
        candidate_id="counterexample:foreign",
        finding_id=finding.finding_id,
        status="INCONCLUSIVE",
        evidence_refs=finding.evidence_refs,
        explanation="x",
    )
    with pytest.raises(ValueError, match="counterexample result/candidate identity mismatch"):
        validate_counterexample_result(finding,candidate,result,history)


def test_counterexample_result_rejects_nonaccepted_refuted_evidence():
    from gnosis.reflection.counterexample import CounterexampleResult, validate_counterexample_result
    history=(_record(0, False, "c1", "repeated failure"),)
    analyzer=ReflectionAnalyzer(history)
    report=analyzer.analyze()
    finding, candidate = report.findings[0], report.counterexamples[0]
    result=CounterexampleResult(
        candidate_id=candidate.candidate_id,
        finding_id=finding.finding_id,
        status="REFUTED",
        evidence_refs=("transition:0:c1",),
        explanation="tampered",
    )
    with pytest.raises(ValueError, match="refuted counterexample evidence"):
        validate_counterexample_result(finding,candidate,result,history)


def test_reloaded_refuted_counterexample_requires_canonical_accepted_history():
    from gnosis.reflection.persistence import validate_reloaded_counterexample_evidence
    result = CounterexampleResult(
        candidate_id="counterexample:finding:1",
        finding_id="finding:1",
        status="REFUTED",
        evidence_refs=("transition:0:c1",),
        explanation="x",
    )
    rejected = _record(0, False, "c1", "rejected")
    with pytest.raises(RuntimeError, match="persisted counterexample evidence"):
        validate_reloaded_counterexample_evidence(result, (rejected,))
