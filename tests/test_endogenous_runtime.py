from dataclasses import replace

from gnosis.core import Budget, Engine, State
from gnosis.reflection.analyzer import ReflectionReport
from gnosis.reflection.endogenous_runtime import generate_from_cumulative_reflection
from gnosis.reflection.runtime import CumulativeReflectionReport
from gnosis.reflection.memory_evidence import EvolutionEvidence


def test_cumulative_evolution_memory_is_bound_into_next_candidate():
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))
    proposal = type("P", (), {
        "proposal_id": "proposal-1",
        "finding_id": "finding-1",
        "rule_id": "rule-1",
        "current_version": 1,
        "proposed_version": 2,
        "hypothesis": "bounded endogenous hypothesis",
        "evidence_refs": ("finding-1",),
    })()
    report = ReflectionReport(proposals=(proposal,))
    evidence = EvolutionEvidence(
        memory_id="memory-1",
        candidate_id="candidate-1",
        transition_id="transition-1",
        outcome="accepted",
        evidence=(),
    )
    cumulative = CumulativeReflectionReport(
        current=report,
        history=None,
        recurring_unresolved=(),
        evolution_evidence=(evidence,),
    )

    generation = generate_from_cumulative_reflection(engine, cumulative)

    assert len(generation.candidates) == 1
    node = generation.candidates[0].proposed_state.elements["proposal-1"]
    assert node["memory_evidence_refs"] == ("memory-1",)
    assert node["historical_memory_outcomes"] == ("accepted",)
    assert node["memory_signature"] == ("memory-1",)


def test_cumulative_adapter_is_read_only():
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))
    before = engine.state
    report = ReflectionReport(proposals=())
    cumulative = CumulativeReflectionReport(
        current=report,
        history=None,
        recurring_unresolved=(),
        evolution_evidence=(),
    )

    generation = generate_from_cumulative_reflection(engine, cumulative)

    assert generation.candidates == ()
    assert engine.state == before


def test_two_evolution_cycles_preserve_memory_causality_across_restart(tmp_path):
    from gnosis.reflection.analyzer import ReflectionReport, RuleProposal
    from gnosis.reflection.endogenous import commit_endogenous_candidates
    from gnosis.reflection.runtime import reflect_with_history
    from gnosis.storage import append_evolution_memory, connect, close, ensure_reflection_schema, load_evolution_memory, save_instance
    from gnosis.reflection.persistence import save_reflection_report
    from gnosis.storage.repositories import _persist_transition
    from gnosis.instances.instance import Instance

    db = tmp_path / "e8c-two-cycles.sqlite"
    conn = connect(db)
    ensure_reflection_schema(conn)
    instance = Instance.create_root("e8c", State(elements={"a": 1}))
    save_instance(conn, instance)

    proposal1 = RuleProposal(proposal_id="p1", finding_id="f1", target="r1:v1", hypothesis="cycle-1", evidence_refs=("f1",), expected_effect="persist memory evidence", regression_risk="test-only", required_test="two-cycle memory persistence", rule_id="r1")
    report1 = ReflectionReport(proposals=(proposal1,))
    report1_id = save_reflection_report(conn, report1, created_at="2026-10-13T00:00:01+00:00")
    cumulative1 = CumulativeReflectionReport(current=report1, history=None, recurring_unresolved=(), evolution_evidence=())
    gen1 = generate_from_cumulative_reflection(instance.engine, cumulative1)
    rec1 = commit_endogenous_candidates(instance.engine, report1, gen1.candidates)
    _persist_transition(conn, instance, gen1.candidates[0], rec1, actor="e8c")
    mem1 = append_evolution_memory(conn, instance_id=instance.instance_id, candidate_id=rec1.candidate_id, transition_id=rec1.transition_id, state_id=rec1.to_state_id, proposal_id=proposal1.proposal_id, proposal_report_id=report1_id, outcome="accepted", evidence=("cycle-1",))
    close(conn)

    conn = connect(db)
    restored = load_evolution_memory(conn, instance.instance_id)
    assert [m.memory_id for m in restored] == [mem1.memory_id]
    history = reflect_with_history(instance.engine, conn, instance_id=instance.instance_id)
    proposal2 = RuleProposal(proposal_id="p2", finding_id="f2", target="r2:v1", hypothesis="cycle-2", evidence_refs=("f2",), expected_effect="reuse persisted memory evidence", regression_risk="test-only", required_test="two-cycle memory persistence", rule_id="r2")
    report2 = ReflectionReport(proposals=(proposal2,))
    report2_id = save_reflection_report(conn, report2, created_at="2026-10-13T00:00:02+00:00")
    cumulative2 = CumulativeReflectionReport(current=ReflectionReport(proposals=(proposal2,)), history=history.history, recurring_unresolved=(), evolution_evidence=history.evolution_evidence)
    gen2 = generate_from_cumulative_reflection(instance.engine, cumulative2)
    assert gen2.candidates[0].proposed_state.elements["p2"]["memory_evidence_refs"] == (mem1.memory_id,)
    rec2 = commit_endogenous_candidates(instance.engine, cumulative2.current, gen2.candidates)
    _persist_transition(conn, instance, gen2.candidates[0], rec2, actor="e8c")
    mem2 = append_evolution_memory(conn, instance_id=instance.instance_id, candidate_id=rec2.candidate_id, transition_id=rec2.transition_id, state_id=rec2.to_state_id, proposal_id=proposal2.proposal_id, proposal_report_id=report2_id, outcome="accepted", evidence=("cycle-2",))
    close(conn)

    conn = connect(db)
    final_memory = load_evolution_memory(conn, instance.instance_id)
    assert [m.memory_id for m in final_memory] == [mem1.memory_id, mem2.memory_id]
    final_reflection = reflect_with_history(instance.engine, conn, instance_id=instance.instance_id)
    assert {m.memory_id for m in final_reflection.evolution_evidence} == {mem1.memory_id, mem2.memory_id}
    close(conn)


def test_memory_aware_endogenous_generation_is_deterministically_replayable():
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))
    proposal = type("P", (), {"proposal_id":"p-replay","finding_id":"f-replay","rule_id":"r-replay","current_version":1,"proposed_version":2,"hypothesis":"replayable","evidence_refs":("f-replay",)})()
    report = ReflectionReport(proposals=(proposal,))
    evidence = EvolutionEvidence(memory_id="m-replay", candidate_id="c-prev", transition_id="t-prev", outcome="accepted", evidence=())
    cumulative = CumulativeReflectionReport(current=report, history=None, recurring_unresolved=(), evolution_evidence=(evidence,))
    first = generate_from_cumulative_reflection(engine, cumulative)
    second = generate_from_cumulative_reflection(engine, cumulative)
    assert len(first.candidates) == len(second.candidates) == 1
    assert first.candidates[0].candidate_id == second.candidates[0].candidate_id
    assert first.candidates[0].proposed_state.state_id == second.candidates[0].proposed_state.state_id
    assert first.candidates[0].proposed_state.content_id == second.candidates[0].proposed_state.content_id


def test_memory_aware_candidate_uses_canonical_sandbox_without_core_mutation():
    from gnosis.reflection.endogenous_runtime import evaluate_candidate_in_sandbox
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))
    proposal = type("P", (), {"proposal_id":"p-sandbox","finding_id":"f-sandbox","rule_id":"r-sandbox","current_version":1,"proposed_version":2,"hypothesis":"sandboxed","evidence_refs":("f-sandbox",)})()
    report = ReflectionReport(proposals=(proposal,))
    cumulative = CumulativeReflectionReport(current=report, history=None, recurring_unresolved=(), evolution_evidence=())
    generation = generate_from_cumulative_reflection(engine, cumulative)
    candidate = generation.candidates[0]
    before = engine.state
    result, evaluation = evaluate_candidate_in_sandbox(
        engine, candidate, lambda state, candidate: {"candidate_id": candidate.candidate_id, "state_id": state.state_id}
    )
    assert result.accepted_for_evaluation
    assert result.execution.candidate_id == candidate.candidate_id
    assert result.execution.parent_state_id == before.state_id
    assert result.execution.evidence_digest
    assert evaluation.status == "PASS"
    assert engine.state == before


def test_endogenous_evaluation_review_binds_to_canonical_provenance_without_authority():
    from gnosis.reflection.endogenous_runtime import build_endogenous_provenance, evaluate_candidate_in_sandbox
    from gnosis.reflection.governance import GovernanceDecision
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))
    proposal = type("P", (), {"proposal_id":"p-prov","finding_id":"f-prov","rule_id":"r-prov","current_version":1,"proposed_version":2,"hypothesis":"provenance","evidence_refs":("f-prov",)})()
    cumulative = CumulativeReflectionReport(current=ReflectionReport(proposals=(proposal,)), history=None, recurring_unresolved=(), evolution_evidence=())
    candidate = generate_from_cumulative_reflection(engine, cumulative).candidates[0]
    sandbox, evaluation = evaluate_candidate_in_sandbox(
        engine, candidate, lambda state, candidate: {"candidate_id": candidate.candidate_id, "observation": "stable"}
    )
    governance = GovernanceDecision("REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",))
    provenance = build_endogenous_provenance(candidate, sandbox, evaluation, governance, parent_state_digest=state.content_id)
    assert provenance.evaluation_status == "PASS"
    assert provenance.governance_decision == "REVIEW"
    assert provenance.candidate_binding_digest == candidate.binding_digest(state.content_id)
    assert governance.can_activate is False
    assert governance.can_rollback is False
    assert engine.state == state


def test_endogenous_provenance_persists_and_replays_after_restart(tmp_path):
    from gnosis.reflection.endogenous_runtime import build_endogenous_provenance, evaluate_candidate_in_sandbox
    from gnosis.reflection.governance import GovernanceDecision
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.evolution.chain_verifier import verify_persisted_chain
    from gnosis.evolution.replay import replay_complete
    from gnosis.reflection.persistence import list_evolution_provenance
    from gnosis.storage import connect, ensure_reflection_schema
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))
    proposal = type("P", (), {"proposal_id":"p-d5","finding_id":"f-d5","rule_id":"r-d5","current_version":1,"proposed_version":2,"hypothesis":"durable","evidence_refs":("f-d5",)})()
    cumulative = CumulativeReflectionReport(current=ReflectionReport(proposals=(proposal,)), history=None, recurring_unresolved=(), evolution_evidence=())
    candidate = generate_from_cumulative_reflection(engine, cumulative).candidates[0]
    sandbox, evaluation = evaluate_candidate_in_sandbox(engine, candidate, lambda state, candidate: {"candidate_id": candidate.candidate_id, "observation": "stable"})
    governance = GovernanceDecision("REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",))
    provenance = build_endogenous_provenance(candidate, sandbox, evaluation, governance, parent_state_digest=state.content_id)
    db = tmp_path / "e8d5.sqlite"
    conn = connect(db); ensure_reflection_schema(conn)
    tx = persist_evolution_transaction(conn, provenance, event_type="PROVENANCE", payload={"status":"RECORDED"})
    rows = conn.execute("SELECT sequence,event_type,candidate_id,execution_id,provenance_id,parent_state_digest,proposed_state_digest,evidence_digest,payload_digest,previous_digest,record_digest FROM evolution_audit ORDER BY sequence").fetchall()
    persisted_provenance = list_evolution_provenance(conn, candidate_id=provenance.candidate_id)[0]
    result = verify_persisted_chain(persisted_provenance, [dict(zip(["sequence","event_type","candidate_id","execution_id","provenance_id","parent_state_digest","proposed_state_digest","evidence_digest","payload_digest","previous_digest","record_digest"], row)) for row in rows], observations=sandbox.execution.observations)
    assert result.valid, result.reasons
    replay = replay_complete(
        sandbox.execution, provenance, tx.audit_record,
        observations=sandbox.execution.observations,
        evaluation_status=evaluation.status,
        shadow_status=governance.shadow_status,
        invariant_status=governance.invariant_status,
        governance_decision=governance.decision,
    )
    assert replay.reproducible, replay.reasons
    incomplete = replay_complete(
        sandbox.execution, provenance, tx.audit_record,
        observations=sandbox.execution.observations,
    )
    assert not incomplete.reproducible
    assert "independent evaluation/governance evidence missing" in incomplete.reasons
    from dataclasses import replace
    tampered = replace(provenance, governance_decision="APPROVE")
    rejected = replay_complete(
        sandbox.execution, tampered, tx.audit_record,
        observations=sandbox.execution.observations,
        evaluation_status=evaluation.status,
        shadow_status=governance.shadow_status,
        invariant_status=governance.invariant_status,
        governance_decision=governance.decision,
    )
    assert not rejected.reproducible
    assert "governance_decision mismatch" in rejected.reasons
    conn.close()


def test_e9_restart_reflection_consumes_persisted_endogenous_memory(tmp_path):
    from gnosis.core import Candidate
    from gnosis.instances.instance import Instance
    from gnosis.reflection.analyzer import RuleProposal
    from gnosis.reflection.endogenous_runtime import evaluate_candidate_in_sandbox, build_endogenous_provenance
    from gnosis.reflection.governance import GovernanceDecision
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.reflection.persistence import save_reflection_report
    from gnosis.storage import connect, ensure_reflection_schema, append_evolution_memory, load_evolution_memory, save_instance
    from gnosis.storage.repositories import _persist_transition
    from gnosis.reflection.runtime import reflect_with_history

    db = tmp_path / "e9.sqlite"
    state = State(elements={"a": 1})
    instance = Instance.create_root("e9-owner", state)
    engine = instance.engine
    proposal1 = RuleProposal(
        proposal_id="p-e9-1", finding_id="f-e9-1", target="r-e9-1:v1",
        hypothesis="cycle-1", evidence_refs=("f-e9-1",),
        expected_effect="exercise persisted memory", regression_risk="test-only",
        required_test="restart test", rule_id="r-e9-1",
    )
    cumulative1 = CumulativeReflectionReport(current=ReflectionReport(proposals=(proposal1,)), history=None, recurring_unresolved=(), evolution_evidence=())
    candidate1 = generate_from_cumulative_reflection(engine, cumulative1).candidates[0]
    sandbox1, evaluation1 = evaluate_candidate_in_sandbox(engine, candidate1, lambda state, candidate: {"candidate_id": candidate.candidate_id, "observation": "stable-1"})
    governance1 = GovernanceDecision("REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",))
    provenance1 = build_endogenous_provenance(candidate1, sandbox1, evaluation1, governance1, parent_state_digest=state.content_id)

    conn = connect(db)
    ensure_reflection_schema(conn)
    save_instance(conn, instance)
    tx1 = persist_evolution_transaction(conn, provenance1, event_type="PROVENANCE", payload={"status": "RECORDED", "cycle": 1})

    # Evolution memory must reference a canonical persisted Core transition,
    # not the unrelated digest of the evolution-audit record.
    transition_candidate = Candidate(
        engine.state.state_id,
        engine.state.with_elements({"memory-cycle": 1}),
        "memory-evidence-test",
    )
    transition = engine.step(transition_candidate)
    _persist_transition(conn, instance, transition_candidate, transition, actor="test")
    report_id = save_reflection_report(
        conn, ReflectionReport(proposals=(proposal1,)),
        created_at="2026-10-13T00:00:00+00:00",
    )
    memory1 = append_evolution_memory(
        conn, instance_id=instance.instance_id,
        candidate_id=transition.candidate_id, transition_id=transition.transition_id,
        state_id=transition.to_state_id, proposal_id=proposal1.proposal_id,
        proposal_report_id=report_id,
        outcome="accepted" if transition.accepted else "rejected",
        evidence=(provenance1.provenance_id, provenance1.evidence_digest),
    )
    conn.close()

    conn = connect(db)
    restored = load_evolution_memory(conn, instance.instance_id)
    assert restored and restored[0].memory_id == memory1.memory_id
    reflection = reflect_with_history(engine, conn, instance_id=instance.instance_id)
    assert any(item.memory_id == memory1.memory_id for item in reflection.evolution_evidence)
    proposal2 = RuleProposal(
        proposal_id="p-e9-2", finding_id="f-e9-2", target="r-e9-2:v1",
        hypothesis="cycle-2", evidence_refs=("f-e9-2",),
        expected_effect="consume persisted memory", regression_risk="test-only",
        required_test="restart test", rule_id="r-e9-2",
    )
    cumulative2 = CumulativeReflectionReport(current=ReflectionReport(proposals=(proposal2,)), history=reflection.history, recurring_unresolved=(), evolution_evidence=reflection.evolution_evidence)
    candidate2 = generate_from_cumulative_reflection(engine, cumulative2).candidates[0]
    refs = candidate2.proposed_state.elements[proposal2.proposal_id]["memory_evidence_refs"]
    assert memory1.memory_id in refs
    conn.close()


def test_e9_second_cycle_completes_persistent_transaction_and_memory(tmp_path):
    from gnosis.core import Candidate
    from gnosis.instances.instance import Instance
    from gnosis.reflection.analyzer import RuleProposal
    from gnosis.reflection.endogenous_runtime import evaluate_candidate_in_sandbox, build_endogenous_provenance
    from gnosis.reflection.governance import GovernanceDecision
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.evolution.chain_verifier import verify_persisted_chain
    from gnosis.evolution.replay import replay_complete
    from gnosis.reflection.persistence import list_evolution_provenance, save_reflection_report
    from gnosis.storage import connect, ensure_reflection_schema, append_evolution_memory, load_evolution_memory, save_instance
    from gnosis.storage.repositories import _persist_transition

    db = tmp_path / "e9-cycle2.sqlite"
    state = State(elements={"a": 1})
    instance = Instance.create_root("e9-owner", state)
    engine = instance.engine
    conn = connect(db)
    ensure_reflection_schema(conn)
    save_instance(conn, instance)
    previous = None
    for cycle in (1, 2):
        proposal = RuleProposal(
            proposal_id=f"p-e9-full-{cycle}", finding_id=f"f-e9-full-{cycle}",
            target=f"r-e9-full-{cycle}:v1", hypothesis=f"cycle-{cycle}",
            evidence_refs=(f"f-e9-full-{cycle}",),
            expected_effect="exercise persisted memory", regression_risk="test-only",
            required_test="two-cycle restart test", rule_id=f"r-e9-full-{cycle}",
        )
        evidence = () if previous is None else (previous.provenance_id, previous.evidence_digest)
        cumulative = CumulativeReflectionReport(current=ReflectionReport(proposals=(proposal,)), history=None, recurring_unresolved=(), evolution_evidence=())
        candidate = generate_from_cumulative_reflection(engine, cumulative).candidates[0]
        parent_digest = engine.state.content_id
        sandbox, evaluation = evaluate_candidate_in_sandbox(engine, candidate, lambda state, candidate: {"candidate_id": candidate.candidate_id, "cycle": cycle})
        governance = GovernanceDecision("REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",))
        provenance = build_endogenous_provenance(candidate, sandbox, evaluation, governance, parent_state_digest=parent_digest)
        tx = persist_evolution_transaction(conn, provenance, event_type="PROVENANCE", payload={"cycle": cycle})
        rows = conn.execute("SELECT sequence,event_type,candidate_id,execution_id,provenance_id,parent_state_digest,proposed_state_digest,evidence_digest,payload_digest,previous_digest,record_digest FROM evolution_audit ORDER BY sequence").fetchall()
        persisted_provenance = list_evolution_provenance(conn, candidate_id=provenance.candidate_id)[0]
        vr = verify_persisted_chain(persisted_provenance, [dict(zip(["sequence","event_type","candidate_id","execution_id","provenance_id","parent_state_digest","proposed_state_digest","evidence_digest","payload_digest","previous_digest","record_digest"], row)) for row in rows], observations=sandbox.execution.observations)
        assert vr.valid, vr.reasons
        rr = replay_complete(
            sandbox.execution, provenance, tx.audit_record,
            observations=sandbox.execution.observations,
            evaluation_status=evaluation.status,
            shadow_status=governance.shadow_status,
            invariant_status=governance.invariant_status,
            governance_decision=governance.decision,
        )
        assert rr.reproducible, rr.reasons

        # Persist a real transition in the Core transition ledger. The
        # provenance audit digest above is deliberately not used as transition_id.
        transition_candidate = Candidate(
            engine.state.state_id,
            engine.state.with_elements({"memory-cycle": cycle}),
            "memory-evidence-test",
        )
        transition = engine.step(transition_candidate)
        _persist_transition(conn, instance, transition_candidate, transition, actor="test")
        report_id = save_reflection_report(
            conn, ReflectionReport(proposals=(proposal,)),
            created_at=f"2026-10-13T00:00:0{cycle}+00:00",
        )
        append_evolution_memory(
            conn, instance_id=instance.instance_id,
            candidate_id=transition.candidate_id, transition_id=transition.transition_id,
            state_id=transition.to_state_id, proposal_id=proposal.proposal_id,
            proposal_report_id=report_id,
            outcome="accepted" if transition.accepted else "rejected",
            evidence=(provenance.provenance_id, provenance.evidence_digest, *evidence),
        )
        previous = provenance
    restored = load_evolution_memory(conn, instance.instance_id)
    assert len(restored) == 2
    assert restored[-1].transition_id
    assert restored[-1].memory_id != restored[0].memory_id
    conn.close()
