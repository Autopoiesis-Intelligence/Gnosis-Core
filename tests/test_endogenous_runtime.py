# E9.2 checkpoint: canonical reflection persistence import.
from dataclasses import replace

from gnosis.core import Budget, Engine, State
from gnosis.reflection.persistence import save_reflection_report
from gnosis.reflection.analyzer import ReflectionReport
from gnosis.reflection.endogenous_runtime import generate_from_cumulative_reflection
from gnosis.reflection.runtime import CumulativeReflectionReport
from gnosis.reflection.memory_evidence import EvolutionEvidence

# E9.2 canonical contract checkpoint: EvolutionEvidence has no state_id.
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
    from gnosis.reflection.analyzer import ReflectionReport
    from gnosis.reflection.endogenous import candidate_binds_proposal, commit_endogenous_candidates
    from gnosis.reflection.runtime import reflect_with_history
    from gnosis.reflection.analyzer import RuleProposal
    from gnosis.storage import append_evolution_memory, connect, close, load_evolution_memory, save_instance
    from gnosis.storage.repositories import _persist_transition
    from gnosis.instances.instance import Instance

    db = tmp_path / "e8c-two-cycles.sqlite"
    conn = connect(db)
    instance = Instance.create_root("e8c", State(elements={"a": 1}))
    save_instance(conn, instance)

    proposal1 = RuleProposal(proposal_id="p1", finding_id="f1", rule_id="r1", target="e8c", hypothesis="cycle-1", evidence_refs=("f1",), expected_effect="cycle-1", regression_risk="low", required_test="e8c-cycle-1")
    report1 = ReflectionReport(proposals=(proposal1,))
    cumulative1 = CumulativeReflectionReport(current=report1, history=None, recurring_unresolved=(), evolution_evidence=())
    report1_id = save_reflection_report(conn, report1, created_at="2026-10-01T00:00:01Z")
    gen1 = generate_from_cumulative_reflection(instance.engine, cumulative1)
    rec1 = commit_endogenous_candidates(instance.engine, report1, gen1.candidates)
    _persist_transition(conn, instance, gen1.candidates[0], rec1, actor="e8c")
    mem1 = append_evolution_memory(conn, instance_id=instance.instance_id, candidate_id=rec1.candidate_id, transition_id=rec1.transition_id, state_id=rec1.to_state_id, proposal_id=proposal1.proposal_id, outcome="accepted", evidence=("cycle-1",), proposal_report_id=report1_id)
    close(conn)

    conn = connect(db)
    restored = load_evolution_memory(conn, instance.instance_id)
    assert [m.memory_id for m in restored] == [mem1.memory_id]
    reflection = reflect_with_history(instance.engine, conn, instance_id=instance.instance_id)
    history = reflection
    proposal2 = RuleProposal(proposal_id="p2", finding_id="f2", rule_id="r2", target="e8c", hypothesis="cycle-2", evidence_refs=("f2",), expected_effect="cycle-2", regression_risk="low", required_test="e8c-cycle-2")
    report2 = ReflectionReport(proposals=(proposal2,))
    report2_id = save_reflection_report(conn, report2, created_at="2026-10-01T00:00:02Z")
    cumulative2 = CumulativeReflectionReport(current=report2, history=history.history, recurring_unresolved=(), evolution_evidence=history.evolution_evidence)
    gen2 = generate_from_cumulative_reflection(instance.engine, cumulative2)
    assert gen2.candidates[0].proposed_state.elements["p2"]["memory_evidence_refs"] == (mem1.memory_id,)
    assert candidate_binds_proposal(gen2.candidates[0], proposal2), (gen2.candidates[0].origin, gen2.candidates[0].proposed_state.elements.get(proposal2.proposal_id), tuple((r.source, r.target, r.relation_type) for r in gen2.candidates[0].proposed_state.relations))
    rec2 = commit_endogenous_candidates(instance.engine, cumulative2.current, gen2.candidates)
    _persist_transition(conn, instance, gen2.candidates[0], rec2, actor="e8c")
    mem2 = append_evolution_memory(conn, instance_id=instance.instance_id, candidate_id=rec2.candidate_id, transition_id=rec2.transition_id, state_id=rec2.to_state_id, proposal_id=proposal2.proposal_id, outcome="accepted", evidence=("cycle-2",), proposal_report_id=report2_id)
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
    from gnosis.storage import connect
    from gnosis.reflection.persistence import ensure_reflection_schema
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
    result = verify_persisted_chain({"candidate_id": provenance.candidate_id, "execution_id": provenance.execution_id, "provenance_id": provenance.provenance_id, "parent_state_id": provenance.parent_state_id, "parent_state_digest": provenance.parent_state_digest, "proposed_state_digest": provenance.proposed_state_digest, "evidence_digest": provenance.evidence_digest, "evaluation_status": provenance.evaluation_status, "shadow_status": provenance.shadow_status, "invariant_status": provenance.invariant_status, "governance_decision": provenance.governance_decision, "status": provenance.status, "proposed_state_content_id": provenance.proposed_state_content_id, "candidate_binding_digest": provenance.candidate_binding_digest}, [dict(zip(["sequence","event_type","candidate_id","execution_id","provenance_id","parent_state_digest","proposed_state_digest","evidence_digest","payload_digest","previous_digest","record_digest"], row)) for row in rows], observations=sandbox.execution.observations)
    assert result.valid, result.reasons
    replay = replay_complete(sandbox.execution, provenance, tx.audit_record, observations=sandbox.execution.observations)
    assert replay.valid, replay.reasons
    conn.close()


def test_e9_restart_reflection_consumes_persisted_endogenous_memory(tmp_path):
    from gnosis.reflection.endogenous_runtime import evaluate_candidate_in_sandbox, build_endogenous_provenance
    from gnosis.reflection.governance import GovernanceDecision
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.storage import connect, append_evolution_memory, load_evolution_memory, save_instance
    from gnosis.storage.repositories import _persist_transition
    from gnosis.instances.instance import Instance
    from gnosis.reflection.persistence import ensure_reflection_schema, save_reflection_report
    from gnosis.reflection.runtime import reflect_with_history
    from gnosis.reflection.analyzer import RuleProposal
    db = tmp_path / "e9.sqlite"
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))
    conn = connect(db)
    ensure_reflection_schema(conn)
    proposal1 = RuleProposal(proposal_id="p-e9-1", finding_id="f-e9-1", rule_id="r-e9-1", target="e9", hypothesis="cycle-1", evidence_refs=("f-e9-1",), expected_effect="cycle-1", regression_risk="low", required_test="e9-cycle-1")
    cumulative1 = CumulativeReflectionReport(current=ReflectionReport(proposals=(proposal1,)), history=None, recurring_unresolved=(), evolution_evidence=())
    report1_id = save_reflection_report(conn, cumulative1.current, created_at="2026-10-01T00:00:01Z")
    candidate1 = generate_from_cumulative_reflection(engine, cumulative1).candidates[0]
    sandbox1, evaluation1 = evaluate_candidate_in_sandbox(engine, candidate1, lambda state, candidate: {"candidate_id": candidate.candidate_id, "observation": "stable-1"})
    governance1 = GovernanceDecision("REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",))
    provenance1 = build_endogenous_provenance(candidate1, sandbox1, evaluation1, governance1, parent_state_digest=state.content_id)
    conn = connect(db); ensure_reflection_schema(conn)
    tx1 = persist_evolution_transaction(conn, provenance1, event_type="PROVENANCE", payload={"status":"RECORDED","cycle":1})
    memory1 = append_evolution_memory(conn, instance_id="e9-instance", candidate_id=candidate1.candidate_id, transition_id=tx1.audit_record.record_digest, state_id=candidate1.parent_state_id, proposal_id=proposal1.proposal_id, outcome="accepted", evidence=(provenance1.provenance_id, provenance1.evidence_digest), proposal_report_id=report1_id)
    conn.close()
    conn = connect(db)
    restored = load_evolution_memory(conn, "e9-instance")
    assert restored and restored[0].memory_id == memory1.memory_id
    reflection = reflect_with_history(engine, conn, instance_id="e9-instance")
    assert any(item.memory_id == memory1.memory_id for item in reflection.evolution_evidence)
    proposal2 = RuleProposal(proposal_id="p-e9-2", finding_id="f-e9-2", rule_id="r-e9-2", target="e9", hypothesis="cycle-2", evidence_refs=("f-e9-2",), expected_effect="cycle-2", regression_risk="low", required_test="e9-cycle-2")
    cumulative2 = CumulativeReflectionReport(current=ReflectionReport(proposals=(proposal2,)), history=reflection.history, recurring_unresolved=(), evolution_evidence=reflection.evolution_evidence)
    report2_id = save_reflection_report(conn, cumulative2.current, created_at="2026-10-01T00:00:02Z")
    candidate2 = generate_from_cumulative_reflection(engine, cumulative2).candidates[0]
    refs = candidate2.proposed_state.elements[proposal2.proposal_id]["memory_evidence_refs"]
    assert memory1.memory_id in refs
    conn.close()


# E9.2 canonical checkpoint: persistent two-cycle test uses canonical provenance execution identity.
def test_e9_second_cycle_completes_persistent_transaction_and_memory(tmp_path):
    from gnosis.reflection.endogenous_runtime import evaluate_candidate_in_sandbox, build_endogenous_provenance
    from gnosis.reflection.governance import GovernanceDecision
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.evolution.chain_verifier import verify_persisted_chain
    from gnosis.evolution.replay import replay_complete
    from gnosis.storage import connect, append_evolution_memory, load_evolution_memory
    from gnosis.reflection.persistence import ensure_reflection_schema, save_reflection_report
    from gnosis.reflection.runtime import reflect_with_history
    from gnosis.reflection.analyzer import RuleProposal

    db = tmp_path / "e9-cycle2.sqlite"
    state = State(elements={"a": 1})
    engine = Engine(state=state, budget=Budget(total=3))

    conn = connect(db)
    ensure_reflection_schema(conn)

    proposal1 = RuleProposal(
        proposal_id="p-e9-full-1", finding_id="f-e9-full-1", rule_id="r-e9-full-1",
        target="e9-test", hypothesis="cycle-1", evidence_refs=("f-e9-full-1",),
        expected_effect="cycle-1", regression_risk="low", required_test="e9-cycle-1",
    )
    cumulative1 = CumulativeReflectionReport(
        current=ReflectionReport(proposals=(proposal1,)),
        history=None,
        recurring_unresolved=(),
        evolution_evidence=(),
    )
    report1_id = save_reflection_report(conn, cumulative1.current, created_at="2026-10-01T00:00:01Z")
    candidate1 = generate_from_cumulative_reflection(engine, cumulative1).candidates[0]
    sandbox1, evaluation1 = evaluate_candidate_in_sandbox(
        engine, candidate1,
        lambda state, candidate: {"candidate_id": candidate.candidate_id, "cycle": 1},
    )
    governance1 = GovernanceDecision("REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",))
    provenance1 = build_endogenous_provenance(
        candidate1, sandbox1, evaluation1, governance1, parent_state_digest=state.content_id
    )
    instance = Instance("e9-full", "test-owner", engine)
    save_instance(conn, instance)
    tx1 = persist_evolution_transaction(
        conn, provenance1, event_type="PROVENANCE", payload={"cycle": 1}
    )
    transition1 = engine.step(candidate1)
    _persist_transition(conn, instance, candidate1, transition1, actor="e9-test")
    rows1 = conn.execute(
        "SELECT sequence,event_type,candidate_id,execution_id,provenance_id,parent_state_digest,"
        "proposed_state_digest,evidence_digest,payload_digest,previous_digest,record_digest "
        "FROM evolution_audit ORDER BY sequence"
    ).fetchall()
    columns = [
        "sequence","event_type","candidate_id","execution_id","provenance_id",
        "parent_state_digest","proposed_state_digest","evidence_digest",
        "payload_digest","previous_digest","record_digest",
    ]
    vr1 = verify_persisted_chain(
        {
            "candidate_id": provenance1.candidate_id,
            "execution_id": provenance1.execution_id,
            "provenance_id": provenance1.provenance_id,
            "parent_state_id": provenance1.parent_state_id,
            "parent_state_digest": provenance1.parent_state_digest,
            "proposed_state_digest": provenance1.proposed_state_digest,
            "evidence_digest": provenance1.evidence_digest,
            "candidate_binding_digest": provenance1.candidate_binding_digest,
            "evaluation_status": provenance1.evaluation_status,
            "shadow_status": provenance1.shadow_status,
            "invariant_status": provenance1.invariant_status,
            "governance_decision": provenance1.governance_decision,
            "status": provenance1.status,
            "proposed_state_content_id": provenance1.proposed_state_content_id,
        },
        [dict(zip(columns, row)) for row in rows1],
        observations=sandbox1.execution.observations,
    )
    assert vr1.valid, vr1.reasons
    rr1 = replay_complete(
        sandbox1.execution, provenance1, tx1.audit_record,
        observations=sandbox1.execution.observations,
    )
    assert rr1.valid, rr1.reasons
    memory1 = append_evolution_memory(
        conn,
        instance_id="e9-full",
        candidate_id=candidate1.candidate_id,
        transition_id=transition1.transition_id,
        state_id=transition1.to_state_id,
        proposal_id=proposal1.proposal_id,
        outcome="accepted",
        evidence=(provenance1.provenance_id, provenance1.evidence_digest),
        proposal_report_id=report1_id,
    )
    conn.close()

    # The second candidate must be generated from persisted Memory #1 after a real restart.
    conn = connect(db)
    instance = __import__("gnosis.storage", fromlist=["load_instance"]).load_instance(conn, "e9-full")
    engine = instance.engine
    restored1 = load_evolution_memory(conn, "e9-full")
    assert [item.memory_id for item in restored1] == [memory1.memory_id]
    reflection = reflect_with_history(engine, conn, instance_id="e9-full")
    assert any(item.memory_id == memory1.memory_id for item in reflection.evolution_evidence)

    proposal2 = RuleProposal(
        proposal_id="p-e9-full-2", finding_id="f-e9-full-2", rule_id="r-e9-full-2",
        target="e9-test", hypothesis="cycle-2", evidence_refs=("f-e9-full-2",),
        expected_effect="cycle-2", regression_risk="low", required_test="e9-cycle-2",
    )
    cumulative2 = CumulativeReflectionReport(
        current=ReflectionReport(proposals=(proposal2,)),
        history=reflection.history,
        recurring_unresolved=(),
        evolution_evidence=reflection.evolution_evidence,
    )
    report2_id = save_reflection_report(conn, cumulative2.current, created_at="2026-10-01T00:00:02Z")
    candidate2 = generate_from_cumulative_reflection(engine, cumulative2).candidates[0]
    refs2 = candidate2.proposed_state.elements[proposal2.proposal_id]["memory_evidence_refs"]
    assert memory1.memory_id in refs2

    sandbox2, evaluation2 = evaluate_candidate_in_sandbox(
        engine, candidate2,
        lambda state, candidate: {"candidate_id": candidate.candidate_id, "cycle": 2},
    )
    governance2 = GovernanceDecision("REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",))
    provenance2 = build_endogenous_provenance(
        candidate2, sandbox2, evaluation2, governance2, parent_state_digest=engine.state.content_id
    )
    tx2 = persist_evolution_transaction(
        conn, provenance2, event_type="PROVENANCE", payload={"cycle": 2}
    )
    transition2 = engine.step(candidate2)
    _persist_transition(conn, instance, candidate2, transition2, actor="e9-test")
    rows2 = conn.execute(
        "SELECT sequence,event_type,candidate_id,execution_id,provenance_id,parent_state_digest,"
        "proposed_state_digest,evidence_digest,payload_digest,previous_digest,record_digest "
        "FROM evolution_audit ORDER BY sequence"
    ).fetchall()
    vr2 = verify_persisted_chain(
        {
            "candidate_id": provenance2.candidate_id,
            "execution_id": provenance2.execution_id,
            "provenance_id": provenance2.provenance_id,
            "parent_state_id": provenance2.parent_state_id,
            "parent_state_digest": provenance2.parent_state_digest,
            "proposed_state_digest": provenance2.proposed_state_digest,
            "evidence_digest": provenance2.evidence_digest,
            "candidate_binding_digest": provenance2.candidate_binding_digest,
            "evaluation_status": provenance2.evaluation_status,
            "shadow_status": provenance2.shadow_status,
            "invariant_status": provenance2.invariant_status,
            "governance_decision": provenance2.governance_decision,
            "status": provenance2.status,
            "proposed_state_content_id": provenance2.proposed_state_content_id,
        },
        [dict(zip(columns, row)) for row in rows2],
        observations=sandbox2.execution.observations,
    )
    assert vr2.valid, vr2.reasons
    rr2 = replay_complete(
        sandbox2.execution, provenance2, tx2.audit_record,
        observations=sandbox2.execution.observations,
    )
    assert rr2.valid, rr2.reasons

    memory2 = append_evolution_memory(
        conn,
        instance_id="e9-full",
        candidate_id=candidate2.candidate_id,
        transition_id=transition2.transition_id,
        state_id=transition2.to_state_id,
        proposal_id=proposal2.proposal_id,
        outcome="accepted",
        evidence=(provenance2.provenance_id, provenance2.evidence_digest, memory1.memory_id),
        proposal_report_id=report2_id,
    )
    conn.close()

    # A second restart must recover both generations and preserve causal references.
    conn = connect(db)
    restored2 = load_evolution_memory(conn, "e9-full")
    assert [item.memory_id for item in restored2] == [memory1.memory_id, memory2.memory_id]
    assert restored2[-1].transition_id == tx2.audit_record.record_digest
    assert restored2[-1].memory_id != restored2[0].memory_id
    assert memory1.memory_id in restored2[-1].evidence
    reflection2 = reflect_with_history(engine, conn, instance_id="e9-full")
    assert {item.memory_id for item in reflection2.evolution_evidence} == {
        memory1.memory_id, memory2.memory_id
    }
    conn.close()
