from gnosis.core import Budget, Candidate, Engine, State
from gnosis.reflection.analyzer import ReflectionReport, RuleProposal
from gnosis.reflection.runtime import run_endogenous


def _seed_candidate(state):
    return Candidate(
        parent_state_id=state.state_id,
        proposed_state=state.with_elements({"seed": 1}),
        origin="external:seed",
    )


def _proposal_report() -> ReflectionReport:
    finding_id = "finding:test"
    proposal_id = "proposal:finding:test:test-rule:v1"
    counterexample_id = f"counterexample:{finding_id}"
    return ReflectionReport(
        proposals=(
            RuleProposal(
                proposal_id=proposal_id,
                finding_id=finding_id,
                target="test-rule:v1",
                hypothesis="test endogenous hypothesis",
                evidence_refs=("transition:1",),
                expected_effect="test",
                regression_risk="test",
                required_test="test",
                rule_id="test-rule",
                current_version=1,
                proposed_version=2,
                finding_refs=(finding_id,),
                counterexample_refs=(counterexample_id,),
            ),
        ),
    )


def test_endogenous_runtime_bridge_uses_canonical_engine_transition_path(monkeypatch):
    state = State(elements={"a": 1})
    engine = Engine(
        state=state,
        budget=Budget(total=4),
        test_fn=lambda _state, candidate: candidate.origin == "reflection:endogenous",
    )

    monkeypatch.setattr(
        "gnosis.reflection.runtime.reflect",
        lambda _engine, minimum_repetitions=2: _proposal_report(),
    )

    records = run_endogenous(engine, max_steps=1)

    assert len(records) == 1
    assert records[0].accepted
    assert records[0].from_state_id == state.state_id
    assert records[0].candidate_id.startswith("candidate:")
    assert engine.state.state_id != state.state_id


def test_endogenous_runtime_bridge_does_not_commit_when_canonical_test_rejects(monkeypatch):
    state = State(elements={"a": 1})
    engine = Engine(
        state=state,
        budget=Budget(total=3),
        test_fn=lambda _state, _candidate: False,
    )

    monkeypatch.setattr(
        "gnosis.reflection.runtime.reflect",
        lambda _engine, minimum_repetitions=2: _proposal_report(),
    )

    records = run_endogenous(engine, max_steps=1)

    assert len(records) == 1
    assert not records[0].accepted
    assert engine.state.state_id == state.state_id
