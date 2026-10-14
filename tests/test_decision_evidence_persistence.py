import sqlite3

import pytest

from gnosis.core import Candidate, State
from gnosis.evolution.decision_evidence import (
    load_decision_evidence,
    persist_decision_evidence,
)
from gnosis.evolution.evaluator import evaluate_observation
from gnosis.evolution.provenance import build_provenance, execution_id
from gnosis.evolution.replay import replay_complete
from gnosis.evolution.sandbox import run_sandbox
from gnosis.reflection.governance import GovernanceDecision
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.evolution.transaction import persist_evolution_transaction


def _candidate(state):
    return Candidate(
        parent_state_id=state.state_id,
        proposed_state=state.with_elements({"b": 2}),
        origin="decision-evidence-restart-test",
    )


def _observe(_state, candidate):
    return {"candidate_id": candidate.candidate_id, "result": "stable"}


def test_decision_evidence_reloads_independently_and_replays_after_restart(tmp_path):
    db = tmp_path / "decision-evidence.sqlite"
    state = State(elements={"a": 1})
    candidate = _candidate(state)
    sandbox = run_sandbox(state, candidate, _observe)
    execution = sandbox.execution
    evaluation = evaluate_observation(
        execution.observations,
        evidence_digest=execution.evidence_digest,
        predicate="observations_present",
    )
    governance = GovernanceDecision(
        "REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",)
    )
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=candidate.parent_state_id,
        parent_state_digest=execution.parent_state_digest,
        proposed_state_digest=execution.proposed_state_digest,
        proposed_state_content_id=candidate.proposed_state.content_id,
        candidate_binding_digest=candidate.binding_digest(execution.parent_state_digest),
        observations=execution.observations,
        evidence_digest=execution.evidence_digest,
        evaluation_status=evaluation.status,
        shadow_status=governance.shadow_status,
        invariant_status=governance.invariant_status,
        governance_decision=governance.decision,
        evaluator_identity_ref=evaluation.evaluator_identity.implementation_ref,
        evaluator_identity_version=evaluation.evaluator_identity.implementation_version,
    )

    conn = sqlite3.connect(db)
    ensure_reflection_schema(conn)
    conn.execute("BEGIN")
    evaluation_id, governance_id = persist_decision_evidence(
        conn,
        execution_id=provenance.execution_id,
        candidate_id=candidate.candidate_id,
        evidence_digest=execution.evidence_digest,
        evaluation=evaluation,
        governance=governance,
    )
    tx = persist_evolution_transaction(
        conn, provenance, event_type="PROVENANCE", payload={"status": "RECORDED"}
    )
    conn.commit()
    conn.close()

    # New connection: objects are reconstructed from independently stored payloads.
    conn = sqlite3.connect(db)
    restored_evaluation, restored_governance = load_decision_evidence(
        conn,
        evaluation_record_id=evaluation_id,
        governance_record_id=governance_id,
        execution_id=provenance.execution_id,
        candidate_id=candidate.candidate_id,
        evidence_digest=execution.evidence_digest,
    )
    replay = replay_complete(
        execution,
        provenance,
        tx.audit_record,
        observations=execution.observations,
        candidate=candidate,
        evaluation=restored_evaluation,
        governance=restored_governance,
    )
    assert replay.reproducible, replay.reasons
    assert restored_evaluation == evaluation
    assert restored_governance == governance
    conn.close()


def test_decision_evidence_rejects_tampered_payload_after_restart(tmp_path):
    db = tmp_path / "decision-evidence-tamper.sqlite"
    state = State(elements={"a": 1})
    candidate = _candidate(state)
    sandbox = run_sandbox(state, candidate, _observe)
    evaluation = evaluate_observation(
        sandbox.execution.observations,
        evidence_digest=sandbox.execution.evidence_digest,
        predicate="observations_present",
    )
    governance = GovernanceDecision(
        "REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",)
    )
    conn = sqlite3.connect(db)
    evaluation_id, governance_id = persist_decision_evidence(
        conn,
        execution_id=execution_id(candidate.candidate_id, candidate.parent_state_id, sandbox.execution.evidence_digest, sandbox.execution.parent_state_digest, sandbox.execution.proposed_state_digest),
        candidate_id=candidate.candidate_id,
        evidence_digest=sandbox.execution.evidence_digest,
        evaluation=evaluation,
        governance=governance,
    )
    conn.commit()
    conn.close()

    conn = sqlite3.connect(db)
    conn.execute(
        "UPDATE evolution_decision_evidence SET payload=? WHERE record_id=?",
        ('{"status":"PASS","rationale":[],"evidence_digest":"tampered",'
         '"evaluator_identity":{"implementation_ref":"x","implementation_version":"1"}}',
         evaluation_id),
    )
    conn.commit()
    with pytest.raises(RuntimeError, match="evaluation evidence integrity mismatch"):
        load_decision_evidence(
            conn,
            evaluation_record_id=evaluation_id,
            governance_record_id=governance_id,
            execution_id=sandbox.execution.execution_id,
            candidate_id=candidate.candidate_id,
            evidence_digest=sandbox.execution.evidence_digest,
        )
    conn.close()
