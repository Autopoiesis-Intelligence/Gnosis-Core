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


def test_endogenous_runtime_persists_transition_and_memory_atomically(monkeypatch):
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_evolution_memory, load_transition_records, save_instance

    state = State(elements={"a": 1})
    instance = Instance.create_root("owner:test", state, budget=Budget(total=3))
    instance.engine.test_fn = lambda _state, candidate: candidate.origin == "reflection:endogenous"
    conn = connect(":memory:")
    save_instance(conn, instance)

    monkeypatch.setattr(
        "gnosis.reflection.runtime.reflect",
        lambda _engine, minimum_repetitions=2: _proposal_report(),
    )

    records = run_endogenous(
        instance.engine,
        conn=conn,
        instance=instance,
        max_steps=1,
    )

    assert len(records) == 1
    assert records[0].accepted

    transitions = load_transition_records(conn, instance.instance_id)
    memory = load_evolution_memory(conn, instance.instance_id)

    assert len(transitions) == 1
    assert len(memory) == 1
    assert memory[0].candidate_id == records[0].candidate_id
    assert memory[0].transition_id == records[0].transition_id
    assert memory[0].state_id == records[0].to_state_id
    assert memory[0].proposal_id == "proposal:finding:test:test-rule:v1"
    assert memory[0].proposal_report_id is not None


def test_endogenous_runtime_memory_failure_rolls_back_transition(monkeypatch):
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_evolution_memory, load_transition_records, save_instance
    import gnosis.storage.evolution_memory as evolution_memory

    state = State(elements={"a": 1})
    instance = Instance.create_root("owner:test", state, budget=Budget(total=3))
    instance.engine.test_fn = lambda _state, candidate: candidate.origin == "reflection:endogenous"
    conn = connect(":memory:")
    save_instance(conn, instance)

    monkeypatch.setattr(
        "gnosis.reflection.runtime.reflect",
        lambda _engine, minimum_repetitions=2: _proposal_report(),
    )

    def fail_memory(*_args, **_kwargs):
        raise RuntimeError("injected memory failure")

    monkeypatch.setattr(evolution_memory, "append_evolution_memory", fail_memory)

    records = run_endogenous(
        instance.engine,
        conn=conn,
        instance=instance,
        max_steps=1,
    )

    assert len(records) == 1
    assert records[0].accepted
    assert load_transition_records(conn, instance.instance_id) == []
    assert load_evolution_memory(conn, instance.instance_id) == ()
