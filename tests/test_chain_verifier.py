import sqlite3

from gnosis.evolution.chain_verifier import verify_persisted_chain
from gnosis.evolution.provenance import EvidenceProvenance, build_provenance, canonical_digest
from gnosis.reflection.persistence import append_evolution_audit, ensure_reflection_schema, save_evolution_provenance, list_evolution_audit


def test_independent_verifier_accepts_persisted_chain():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    observations = {"result": "ok"}
    p = build_provenance(
        candidate_id="c", parent_state_id="s", parent_state_digest="pd",
        proposed_state_digest="sd", observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS", shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED", governance_decision="REVIEW",
    )
    pid = save_evolution_provenance(conn, p)
    append_evolution_audit(
        conn, event_type="EVOLUTION_RECORDED", candidate_id="c", execution_id=p.execution_id,
        provenance_id=pid, parent_state_digest="pd", proposed_state_digest="sd",
        evidence_digest=p.evidence_digest, payload={"status": "RECORDED"},
    )
    rows = list_evolution_audit(conn)
    provenance_row = {
        "provenance_id": pid, "execution_id": p.execution_id, "candidate_id": "c",
        "parent_state_id": "s", "parent_state_digest": "pd",
        "proposed_state_digest": "sd", "evidence_digest": p.evidence_digest,
        "evaluation_status": "PASS", "shadow_status": "NO_BEHAVIORAL_CHANGE",
        "invariant_status": "PRESERVED", "governance_decision": "REVIEW",
        "status": "RECORDED",
    }
    audit_rows = [row.__dict__ for row in rows]
    result = verify_persisted_chain(provenance_row, audit_rows, observations=observations)
    assert result.valid, result.reasons


def test_independent_verifier_fails_closed_on_tampered_persisted_data():
    observations = {"result": "ok"}
    provenance = {
        "provenance_id": "provenance:wrong",
        "execution_id": "e", "candidate_id": "c", "parent_state_id": "s",
        "parent_state_digest": "pd", "proposed_state_digest": "sd",
        "evidence_digest": canonical_digest(observations),
        "evaluation_status": "PASS", "shadow_status": "NO_BEHAVIORAL_CHANGE",
        "invariant_status": "PRESERVED", "governance_decision": "REVIEW",
        "status": "RECORDED",
    }
    result = verify_persisted_chain(provenance, [], observations=observations)
    assert not result.valid
    assert "audit chain missing" in result.reasons


def test_persisted_provenance_carries_canonical_evolution_identity():
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    observations = {"result": "ok"}
    p = build_provenance(
        candidate_id="c", parent_state_id="s", parent_state_digest="pd",
        proposed_state_digest="sd", observations=observations,
        evidence_digest=canonical_digest(observations), evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE", invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    from gnosis.reflection.persistence import save_evolution_provenance, load_evolution_provenance
    pid = save_evolution_provenance(conn, p)
    row = load_evolution_provenance(conn, pid)
    assert row["evolution_identity"] == p.evolution_identity


def test_verify_persisted_chain_rejects_duplicate_audit_links() -> None:
    from gnosis.evolution.audit import make_audit_record
    from gnosis.evolution.chain_verifier import verify_persisted_chain
    from gnosis.evolution.provenance import build_provenance, canonical_digest

    observations = {"x": 1}
    p = build_provenance(
        candidate_id="candidate:duplicate-audit",
        parent_state_id="state:1",
        parent_state_digest="parent:1",
        proposed_state_digest="state:2",
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    a0 = make_audit_record(
        sequence=0, event_type="PROVENANCE", candidate_id=p.candidate_id,
        execution_id=p.execution_id, provenance_id=p.provenance_id,
        parent_state_digest=p.parent_state_digest,
        proposed_state_digest=p.proposed_state_digest,
        evidence_digest=p.evidence_digest, payload={"status": "RECORDED"},
    )
    a1 = make_audit_record(
        sequence=1, event_type="PROVENANCE", candidate_id=p.candidate_id,
        execution_id=p.execution_id, provenance_id=p.provenance_id,
        parent_state_digest=p.parent_state_digest,
        proposed_state_digest=p.proposed_state_digest,
        evidence_digest=p.evidence_digest, payload={"status": "DUPLICATE"},
        previous_digest=a0.record_digest,
    )
    row = {
        "provenance_id": p.provenance_id,
        "execution_id": p.execution_id,
        "candidate_id": p.candidate_id,
        "parent_state_id": p.parent_state_id,
        "parent_state_digest": p.parent_state_digest,
        "proposed_state_digest": p.proposed_state_digest,
        "evidence_digest": p.evidence_digest,
        "evolution_identity": p.evolution_identity,
        "proposed_state_content_id": p.proposed_state_content_id,
        "candidate_binding_digest": p.candidate_binding_digest,
        "evaluation_status": p.evaluation_status,
        "shadow_status": p.shadow_status,
        "invariant_status": p.invariant_status,
        "governance_decision": p.governance_decision,
        "status": p.status,
    }
    result = verify_persisted_chain(row, [a0.__dict__, a1.__dict__], observations=observations)
    assert not result.valid
    assert "multiple audit records linked to provenance" in result.reasons
