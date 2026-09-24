import pytest

from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.reflection.gate import run_reflection_gate
from gnosis.storage import connect, save_instance, persist_transition


def test_reflection_gate_reaches_durable_read_only_evidence():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"a": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "test")
    record = instance.engine.step(candidate)
    _persist_transition(conn, instance, candidate, record, actor="test")

    result = run_reflection_gate(instance.engine, conn, instance.instance_id)

    assert result.passed
    assert result.transition_count == 1
    assert result.durable_graph_verified
    assert result.recovery_state_id == instance.engine.state.state_id
    assert result.report_id.startswith("reflection:")
    assert result.artifact["authority"] == "READ_ONLY"
    conn.close()


def test_reflection_gate_fails_closed_without_canonical_history():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    result = run_reflection_gate(instance.engine, conn, instance.instance_id)
    assert not result.passed
    assert "canonical Core history is empty" in result.reasons
    conn.close()


def test_reflection_gate_fails_when_evolution_recovery_is_invalidated():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"a": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "test")
    record = instance.engine.step(candidate)
    _persist_transition(conn, instance, candidate, record, actor="test")

    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.reflection.persistence import append_evolution_audit, ensure_reflection_schema, save_evolution_provenance
    ensure_reflection_schema(conn)
    observations = {"status": "PASS"}
    p = build_provenance(
        candidate_id="gate-evolution", parent_state_id="s1",
        parent_state_digest="pd", proposed_state_digest="sd",
        observations=observations, evidence_digest=canonical_digest(observations),
        evaluation_status="PASS", shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED", governance_decision="REVIEW",
    )
    save_evolution_provenance(conn, p)
    append_evolution_audit(
        conn, event_type="PROVENANCE", candidate_id=p.candidate_id,
        execution_id=p.execution_id, provenance_id=p.provenance_id,
        parent_state_digest=p.parent_state_digest,
        proposed_state_digest=p.proposed_state_digest,
        evidence_digest=p.evidence_digest, payload={"status": "PASS"},
    )
    conn.execute("UPDATE evolution_audit SET evidence_digest='tampered'")

    result = run_reflection_gate(instance.engine, conn, instance.instance_id)
    assert not result.passed
    assert "evolution provenance/audit recovery failed" in result.reasons
    conn.close()

from gnosis.storage.repositories import _persist_transition
