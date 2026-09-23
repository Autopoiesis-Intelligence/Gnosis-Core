import pytest
from gnosis.core import State, TestResult, TransitionRecord
from gnosis.reflection import ReflectionAnalyzer, reflect


def transition(candidate_id: str, accepted: bool, reason: str) -> TransitionRecord:
    state = State(elements={"n": 1})
    result = TestResult(passed=accepted, reasons=(reason,) if reason else ())
    return TransitionRecord(
        from_state_id=state.state_id,
        to_state_id=state.state_id,
        candidate_id=candidate_id,
        test_result=result,
        accepted=accepted,
        reason=reason,
    )


def test_reflection_observes_core_history_and_proposes_without_mutation():
    history = [
        transition("a", False, "invariant X failed"),
        transition("b", False, "invariant X failed"),
        transition("c", True, "committed"),
    ]
    analyzer = ReflectionAnalyzer(history)
    report = analyzer.analyze()

    assert len(report.observations) == 5
    assert sum(o.kind == "transition_outcome" for o in report.observations) == 3
    assert sum(o.kind == "rejection_reason" for o in report.observations) == 2
    assert len(report.findings) == 1
    assert len(report.counterexamples) == 1
    assert len(report.proposals) == 1
    assert report.proposals[0].status == "PROPOSED"
    assert report.proposals[0].evidence_refs
    assert "invariant X failed" in report.proposals[0].hypothesis

    # Reflection is read-only: the source evidence remains identical.
    assert tuple(history) == analyzer._transitions


def test_runtime_reflects_engine_history_without_mutation():
    class EngineLike:
        def __init__(self):
            self.history = [
                transition("a", False, "repeated"),
                transition("b", False, "repeated"),
            ]

    engine = EngineLike()
    before = tuple(engine.history)
    report = reflect(engine)

    assert len(report.proposals) == 1
    assert tuple(engine.history) == before


def test_reflection_does_not_create_finding_for_single_occurrence():
    report = ReflectionAnalyzer(
        [transition("a", False, "one-off"), transition("b", True, "committed")]
    ).analyze()

    assert report.findings == ()
    assert report.counterexamples == ()
    assert report.proposals == ()


def test_reflection_ids_are_deterministic():
    history = [
        transition("a", False, "same reason"),
        transition("b", False, "same reason"),
    ]

    first = ReflectionAnalyzer(history).analyze()
    second = ReflectionAnalyzer(history).analyze()

    assert first.findings[0].finding_id == second.findings[0].finding_id
    assert first.proposals[0].proposal_id == second.proposals[0].proposal_id


def test_reflection_never_returns_activation_command():
    history = [
        transition("a", False, "repeated"),
        transition("b", False, "repeated"),
    ]
    report = ReflectionAnalyzer(history).analyze()

    proposal = report.proposals[0]
    assert proposal.status == "PROPOSED"
    assert not hasattr(proposal, "activate")
    assert not hasattr(proposal, "commit")


def test_reflection_provenance_rejects_tampered_finding_evidence():
    from gnosis.reflection.analyzer import (
        Finding, ReflectionObservation, ReflectionReport, validate_reflection_provenance,
    )
    observation = ReflectionObservation(
        observation_id="observation:1",
        transition_id="transition:1:c1",
        kind="rejection_reason",
        value="bad",
        evidence_ref="transition:1:c1",
    )
    finding = Finding(
        finding_id="finding:1",
        claim="x",
        observation_ids=("observation:1",),
        evidence_refs=("transition:foreign:c9",),
        reproducibility=2,
        falsification_condition="x",
    )
    report = ReflectionReport(observations=(observation,), findings=(finding,))
    with pytest.raises(ValueError, match="finding observation/evidence provenance mismatch"):
        validate_reflection_provenance(report)


def test_reflection_provenance_rejects_proposal_with_foreign_finding_evidence():
    from gnosis.reflection.analyzer import (
        Finding, ReflectionObservation, ReflectionReport, RuleProposal,
        validate_reflection_provenance,
    )
    observation = ReflectionObservation(
        observation_id="observation:1",
        transition_id="transition:1:c1",
        kind="rejection_reason",
        value="bad",
        evidence_ref="transition:1:c1",
    )
    finding = Finding(
        finding_id="finding:1",
        claim="x",
        observation_ids=("observation:1",),
        evidence_refs=("transition:1:c1",),
        reproducibility=2,
        falsification_condition="x",
    )
    proposal = RuleProposal(
        proposal_id="proposal:1",
        finding_id="finding:1",
        target="rule:v1",
        hypothesis="h",
        evidence_refs=("transition:foreign:c9",),
        expected_effect="e",
        regression_risk="r",
        required_test="t",
    )
    report = ReflectionReport(
        observations=(observation,),
        findings=(finding,),
        proposals=(proposal,),
    )
    with pytest.raises(ValueError, match="proposal/finding evidence provenance mismatch"):
        validate_reflection_provenance(report)


def test_reflection_provenance_rejects_counterexample_for_unknown_finding():
    from gnosis.reflection.analyzer import CounterexampleCandidate, ReflectionReport, validate_reflection_provenance
    candidate = CounterexampleCandidate(
        candidate_id="counterexample:finding:foreign",
        finding_id="finding:foreign",
        method="replay",
        success_condition="x",
        evidence_refs=("transition:1:c1",),
    )
    with pytest.raises(ValueError, match="counterexample references unknown finding"):
        validate_reflection_provenance(ReflectionReport(counterexamples=(candidate,)))


def test_reflection_provenance_rejects_counterexample_with_foreign_evidence():
    from gnosis.reflection.analyzer import (
        CounterexampleCandidate, Finding, ReflectionObservation, ReflectionReport,
        validate_reflection_provenance,
    )
    observation = ReflectionObservation(
        observation_id="observation:1",
        transition_id="transition:1:c1",
        kind="rejection_reason",
        value="bad",
        evidence_ref="transition:1:c1",
    )
    finding = Finding(
        finding_id="finding:1",
        claim="x",
        observation_ids=("observation:1",),
        evidence_refs=("transition:1:c1",),
        reproducibility=2,
        falsification_condition="x",
    )
    candidate = CounterexampleCandidate(
        candidate_id="counterexample:finding:1",
        finding_id="finding:1",
        method="replay",
        success_condition="x",
        evidence_refs=("transition:foreign:c9",),
    )
    report = ReflectionReport(
        observations=(observation,),
        findings=(finding,),
        counterexamples=(candidate,),
    )
    with pytest.raises(ValueError, match="counterexample/finding evidence provenance mismatch"):
        validate_reflection_provenance(report)


def test_transition_evidence_identity_is_stable_across_history_reordering():
    first = transition("c0", False, "same")
    second = transition("c1", False, "same")
    reordered = (second, first)
    assert first.transition_id != second.transition_id
    assert first.transition_id == reordered[1].transition_id
    assert second.transition_id == reordered[0].transition_id
