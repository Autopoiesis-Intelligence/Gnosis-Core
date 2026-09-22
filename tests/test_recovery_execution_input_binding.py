import sqlite3

from gnosis.core.state_identity import state_digest
from gnosis.core.types import State
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.evolution.recovery import recover_evolution_audit
from gnosis.reflection.persistence import append_evolution_audit, ensure_reflection_schema, save_evolution_provenance


def test_recovery_rejects_parent_state_substitution():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    parent = State(elements={"x": 1})
    other = State(elements={"x": 2})
    proposed = State(elements={"x": 3})
    observations = {"status": "PASS"}
    p = build_provenance(
        candidate_id="c-recovery", parent_state_id=parent.state_id,
        parent_state_digest=state_digest(parent), proposed_state_digest=proposed.content_id,
        observations=observations, proposed_state_content_id=proposed.content_id,
        evidence_digest=canonical_digest(observations), evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE", invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    pid = save_evolution_provenance(conn, p)
    append_evolution_audit(
        conn, event_type="PROVENANCE", candidate_id=p.candidate_id,
        execution_id=p.execution_id, provenance_id=pid,
        parent_state_digest=p.parent_state_digest, proposed_state_digest=p.proposed_state_digest,
        evidence_digest=p.evidence_digest, payload={"status": "PASS"},
    )
    report = recover_evolution_audit(
        conn, provenance_id=pid, observations=observations,
        proposed_state=proposed, parent_state=other,
    )
    assert not report.replay_valid
    assert "recovery execution input binding mismatch" in report.reasons
