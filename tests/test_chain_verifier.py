import sqlite3

from gnosis.evolution.chain_verifier import verify_persisted_chain, verify_evolution_identity_chain
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


def _identity_chain_fixture():
    from gnosis.core.types import State, Candidate, TestResult, TransitionRecord
    from gnosis.self_learning.e7_106_selection import CandidateRecord, SelectionStatus, create_selection_record
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.evolution.audit import make_audit_record
    state = State()
    candidate_id = "C1"
    candidate = CandidateRecord(
        candidate_id=candidate_id, contract_id="E7.114", revision="r1",
        current_status="IMPLEMENTED", dependency_status="SATISFIED",
        implementation_paths=("x.py",), acceptance_criteria_count=1,
        mapped_test_count=1, runtime_proof_requirements=("exact_commit",),
        existing_evidence_ids=(), evidence_commits=("0"*40,),
        known_gaps=(), trust_boundary_relevance="HIGH",
        execution_prerequisites=("python",), selection_status=SelectionStatus.SELECTED,
        selection_rationale="fixture",
    )
    reserve = CandidateRecord(
        candidate_id="C2", contract_id="E7.114", revision="r1",
        current_status="IMPLEMENTED", dependency_status="SATISFIED",
        implementation_paths=("y.py",), acceptance_criteria_count=1,
        mapped_test_count=1, runtime_proof_requirements=("exact_commit",),
        existing_evidence_ids=(), evidence_commits=("1"*40,),
        known_gaps=(), trust_boundary_relevance="HIGH",
        execution_prerequisites=("python",), selection_status=SelectionStatus.RESERVE,
        selection_rationale="fixture",
    )
    selection = create_selection_record(
        selection_record_id="SEL-1", batch_id="B-1", baseline_id="BASE-1",
        repository="repo", target_commit_sha="0"*40,
        candidates=(candidate,reserve), selected_candidate_ids=(candidate_id,),
        reserve_candidate_ids=("C2",), excluded_candidate_ids=(), blocked_candidate_ids=(),
        runtime_scenarios=("proof",), evidence_capture_points=("stdout",),
        stop_conditions=("failure",), selection_policy_revision="r1",
    )
    observations={"ok":True}
    p=build_provenance(candidate_id=candidate_id,parent_state_id=state.state_id,
        parent_state_digest="pd",proposed_state_digest="sd",observations=observations,
        evidence_digest=canonical_digest(observations),evaluation_status="PASS",
        shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW")
    tr=TransitionRecord(from_state_id=state.state_id,to_state_id="sd",candidate_id=candidate_id,
        test_result=TestResult(True),accepted=True,reason="committed",test_rule_id="rule")
    a=make_audit_record(sequence=0,event_type="PROVENANCE",candidate_id=candidate_id,
        execution_id=p.execution_id,provenance_id=p.provenance_id,parent_state_digest="pd",
        proposed_state_digest="sd",evidence_digest=p.evidence_digest,payload={"status":"RECORDED"})
    return selection,tr,{"provenance_id":p.provenance_id,"execution_id":p.execution_id,
        "candidate_id":candidate_id,"parent_state_id":state.state_id,"parent_state_digest":"pd",
        "proposed_state_digest":"sd","evidence_digest":p.evidence_digest,
        "evaluation_status":"PASS","shadow_status":"UNCHANGED","invariant_status":"PRESERVED",
        "governance_decision":"ALLOW","status":"RECORDED"},[a.__dict__],observations

def test_evolution_identity_chain_accepts_consistent_chain():
    selection,tr,prov,aud,obs=_identity_chain_fixture()
    result=verify_evolution_identity_chain(selection,tr,prov,aud,observations=obs)
    assert result.valid, result.reasons

def test_evolution_identity_chain_rejects_selection_transition_mismatch():
    selection,tr,prov,aud,obs=_identity_chain_fixture()
    from dataclasses import replace
    tr=replace(tr,candidate_id="C2")
    result=verify_evolution_identity_chain(selection,tr,prov,aud,observations=obs)
    assert not result.valid
    assert any("selection" in r or "candidate" in r for r in result.reasons)

def test_evolution_identity_chain_rejects_transition_provenance_mismatch():
    selection,tr,prov,aud,obs=_identity_chain_fixture()
    prov=dict(prov,candidate_id="C2")
    result=verify_evolution_identity_chain(selection,tr,prov,aud,observations=obs)
    assert not result.valid
    assert any("provenance" in r or "candidate" in r for r in result.reasons)

def test_evolution_identity_chain_rejects_provenance_audit_mismatch():
    selection,tr,prov,aud,obs=_identity_chain_fixture()
    aud=[dict(aud[0],candidate_id="C2")]
    result=verify_evolution_identity_chain(selection,tr,prov,aud,observations=obs)
    assert not result.valid
    assert any("audit" in r or "candidate" in r for r in result.reasons)


def test_persisted_audit_binding_tamper_is_detected():
    conn = make_connection()
    provenance = make_provenance(candidate_binding_digest="binding-original")
    result = persist_evolution_transaction(
        conn, provenance, event_type="EVOLUTION", payload={"ok": True}
    )
    conn.execute(
        "UPDATE evolution_audit SET candidate_binding_digest=? WHERE sequence=?",
        ("binding-tampered", result.audit_record.sequence),
    )
    conn.commit()
    with pytest.raises((AssertionError, ValueError, RuntimeError)):
        verify_evolution_identity_chain(conn)
