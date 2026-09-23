import pytest
from gnosis.evolution.provenance import build_provenance, verify_evidence_digest, canonical_digest, provenance_id_for


def test_provenance_accepts_matching_evidence_digest():
    observations = {"metric": 1, "nested": {"ok": True}}
    digest = canonical_digest(observations)
    result = build_provenance(
        candidate_id="candidate:1",
        parent_state_id="state:1",
        observations=observations,
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
    candidate_binding_digest="binding-digest",
        evidence_digest=digest,
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    assert result.status == "RECORDED"
    assert result.provenance_id.startswith("provenance:")
    assert verify_evidence_digest(observations, digest)


def test_provenance_rejects_tampered_observations():
    observations = {"metric": 1}
    from gnosis.evolution.provenance import canonical_digest
    digest = canonical_digest(observations)
    assert not verify_evidence_digest({"metric": 2}, digest)
    try:
        build_provenance(
            candidate_id="candidate:1",
            parent_state_id="state:1",
            parent_state_digest="parent-digest",
            proposed_state_digest="proposed-digest",
            observations={"metric": 2},
            evidence_digest=digest,
            evaluation_status="PASS",
            shadow_status="NO_BEHAVIORAL_CHANGE",
            invariant_status="PRESERVED",
            governance_decision="REVIEW",
        )
    except ValueError as exc:
        assert "mismatch" in str(exc)
    else:
        raise AssertionError("tampered evidence must be rejected")


def test_provenance_persists_and_reloads_without_activation():
    import sqlite3
    from gnosis.evolution.provenance import canonical_digest
    from gnosis.reflection.persistence import (
        ensure_reflection_schema,
        load_evolution_provenance,
        save_evolution_provenance,
    )
    observations = {"metric": 7}
    provenance = build_provenance(
        candidate_id="candidate:2",
        parent_state_id="state:2",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    stored = save_evolution_provenance(conn, provenance)
    loaded = load_evolution_provenance(conn, stored)
    assert loaded["evidence_digest"] == provenance.evidence_digest
    assert loaded["candidate_id"] == provenance.candidate_id
    assert loaded["status"] == "RECORDED"


def test_crosscheck_accepts_intact_provenance():
    from gnosis.evolution.provenance import (
        canonical_digest,
        crosscheck_provenance,
        execution_id,
    )
    observations = {"metric": 9}
    digest = canonical_digest(observations)
    provenance = build_provenance(
        candidate_id="candidate:3",
        parent_state_id="state:3",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=digest,
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    result = crosscheck_provenance(
        provenance=provenance,
        candidate_id="candidate:3",
        parent_state_id="state:3",
        observations=observations,
        evidence_digest=digest,
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        execution_id_value=execution_id("candidate:3", "state:3", digest, "parent-digest", "proposed-digest"),
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    assert result.valid
    assert result.reasons == ()


def test_crosscheck_rejects_chain_mismatch():
    from gnosis.evolution.provenance import canonical_digest, crosscheck_provenance, execution_id
    observations = {"metric": 9}
    digest = canonical_digest(observations)
    provenance = build_provenance(
        candidate_id="candidate:4",
        parent_state_id="state:4",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=digest,
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    result = crosscheck_provenance(
        provenance=provenance,
        candidate_id="candidate:tampered",
        parent_state_id="state:4",
        observations=observations,
        evidence_digest=digest,
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        execution_id_value=execution_id("candidate:tampered", "state:4", digest, "parent-digest", "proposed-digest"),
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    assert not result.valid
    assert any("candidate_id mismatch" in reason for reason in result.reasons)


def test_stored_provenance_crosscheck_detects_tampering():
    import sqlite3
    from gnosis.evolution.provenance import canonical_digest
    from gnosis.reflection.persistence import (
        crosscheck_stored_provenance,
        ensure_reflection_schema,
        save_evolution_provenance,
    )
    observations = {"metric": 11}
    digest = canonical_digest(observations)
    provenance = build_provenance(
        candidate_id="candidate:5",
        parent_state_id="state:5",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=digest,
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    conn = sqlite3.connect(":memory:")
    ensure_reflection_schema(conn)
    stored = save_evolution_provenance(conn, provenance)
    assert crosscheck_stored_provenance(conn, stored, observations=observations).valid
    result = crosscheck_stored_provenance(conn, stored, observations={"metric": 999})
    assert not result.valid
    assert any("observation digest mismatch" in reason for reason in result.reasons)


def test_promotion_gate_is_review_only_even_when_eligible():
    from gnosis.evolution.promotion import evaluate_promotion_gate, make_promotion_candidate
    candidate = make_promotion_candidate(
        candidate_id="candidate:6",
        evidence_digest="digest",
        evaluation_status="PASS",
        shadow_status="IMPROVED",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
    )
    gate = evaluate_promotion_gate(candidate, provenance_valid=True)
    assert gate.eligible
    assert gate.status == "REVIEW_ONLY"
    assert gate.can_activate is False
    assert candidate.can_activate is False


def test_promotion_gate_fails_closed_on_provenance():
    from gnosis.evolution.promotion import evaluate_promotion_gate, make_promotion_candidate
    candidate = make_promotion_candidate(
        candidate_id="candidate:7",
        evidence_digest="digest",
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
    )
    gate = evaluate_promotion_gate(candidate, provenance_valid=False)
    assert not gate.eligible
    assert "provenance cross-check failed" in gate.reasons


def test_promotion_gate_rejects_unsafe_statuses():
    from gnosis.evolution.promotion import evaluate_promotion_gate, make_promotion_candidate
    candidate = make_promotion_candidate(
        candidate_id="candidate:8",
        evidence_digest="digest",
        evaluation_status="REVIEW",
        shadow_status="BEHAVIOR_CHANGED",
        invariant_status="REGRESSED",
        governance_decision="REJECT",
    )
    gate = evaluate_promotion_gate(candidate, provenance_valid=True)
    assert not gate.eligible
    assert len(gate.reasons) == 4


def test_crosscheck_rejects_state_digest_mismatch():
    from gnosis.evolution.provenance import canonical_digest, crosscheck_provenance, execution_id
    observations = {"metric": 12}
    digest = canonical_digest(observations)
    provenance = build_provenance(
        candidate_id="candidate:state-bind",
        parent_state_id="state:bind",
        parent_state_digest="parent-digest",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=digest,
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    result = crosscheck_provenance(
        provenance=provenance,
        candidate_id="candidate:state-bind",
        parent_state_id="state:bind",
        parent_state_digest="wrong-parent",
        proposed_state_digest="proposed-digest",
        observations=observations,
        evidence_digest=digest,
        execution_id_value=execution_id("candidate:state-bind", "state:bind", digest, "wrong-parent", "proposed-digest"),
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    assert not result.valid
    assert "parent_state_digest mismatch" in result.reasons


def test_state_content_identity_is_canonical_and_version_independent():
    from gnosis.core.types import State
    a = State(elements={"b": 2, "a": {"x": 1}}, version=1)
    b = State(elements={"a": {"x": 1}, "b": 2}, version=99)
    assert a.content_id == b.content_id
    assert a.state_id != b.state_id


def test_state_content_identity_changes_with_content():
    from gnosis.core.types import State
    a = State(elements={"x": 1})
    b = State(elements={"x": 2})
    assert a.content_id != b.content_id


def test_list_evolution_provenance_candidate_scope_preserves_binding_digest() -> None:
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.reflection.persistence import ensure_reflection_schema, list_evolution_provenance, save_evolution_provenance
    from gnosis.storage import connect

    conn = connect()
    ensure_reflection_schema(conn)
    observations = {"x": 1}
    p = build_provenance(
        candidate_id="candidate:list",
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
    save_evolution_provenance(conn, p)
    rows = list_evolution_provenance(conn, candidate_id=p.candidate_id)
    assert rows[0]["candidate_binding_digest"] == p.candidate_binding_digest
    conn.close()


def test_classify_evolution_provenance_rejects_forged_nonempty_identity() -> None:
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.reflection.persistence import classify_evolution_provenance, ensure_reflection_schema, list_evolution_provenance, save_evolution_provenance
    from gnosis.storage import connect

    conn = connect()
    ensure_reflection_schema(conn)
    observations = {"x": 1}
    p = build_provenance(
        candidate_id="candidate:classify",
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
    save_evolution_provenance(conn, p)
    row = list_evolution_provenance(conn)[0]
    assert classify_evolution_provenance(row) == "canonical"
    row["evolution_identity"] = "evolution:forged"
    assert classify_evolution_provenance(row) == "malformed"
    conn.close()


def test_promotion_gate_rejects_mismatched_required_evidence_digest():
    from gnosis.evolution.promotion import evaluate_promotion_gate, make_promotion_candidate
    candidate = make_promotion_candidate(
        candidate_id="candidate:evidence-mismatch",
        evidence_digest="digest:actual",
        evaluation_status="PASS",
        shadow_status="IMPROVED",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
    )
    gate = evaluate_promotion_gate(
        candidate, provenance_valid=True, required_evidence=("digest:other",)
    )
    assert gate.eligible is False
    assert "candidate evidence digest is not in required evidence" in gate.reasons


def test_load_evolution_provenance_rejects_stored_identity_tamper():
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.reflection.persistence import ensure_reflection_schema, load_evolution_provenance, save_evolution_provenance
    from gnosis.storage import connect

    conn = connect()
    ensure_reflection_schema(conn)
    observations = {"x": 1}
    p = build_provenance(
        candidate_id="candidate:stored-id-tamper",
        parent_state_id="state:1",
        parent_state_digest="parent:1",
        proposed_state_digest="state:2",
        observations=observations,
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    pid = save_evolution_provenance(conn, p)
    conn.execute(
        "UPDATE evolution_provenance SET provenance_id=? WHERE provenance_id=?",
        ("forged-provenance-id", pid),
    )
    with pytest.raises(RuntimeError, match="stored provenance identity mismatch"):
        load_evolution_provenance(conn, pid)


def test_promotion_gate_distinguishes_evidence_roles():
    from gnosis.evolution.promotion import evaluate_promotion_gate, make_promotion_candidate
    candidate = make_promotion_candidate(
        candidate_id="candidate:roles",
        evidence_digest="digest:roles",
        evaluation_status="PASS",
        shadow_status="IMPROVED",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
    )
    gate = evaluate_promotion_gate(
        candidate,
        provenance_valid=True,
        evidence_roles={
            "DETECTION": ("det:1",),
            "EXPLANATION": ("exp:1",),
            "AUTHORIZATION": (),
        },
    )
    assert gate.eligible is False
    assert "authorization evidence is missing" in gate.reasons


def test_promotion_candidate_binds_authorization_context():
    from gnosis.evolution.promotion import make_promotion_candidate

    candidate = make_promotion_candidate(
        candidate_id="candidate:auth-context",
        evidence_digest="digest:auth",
        evaluation_status="PASS",
        shadow_status="IMPROVED",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
        authorization_scope="scope:1",
        authorization_target="target:1",
        policy_version="policy:v1",
        authorization_freshness="epoch:7",
    )
    assert candidate.authorization_scope == "scope:1"
    assert candidate.authorization_target == "target:1"
    assert candidate.policy_version == "policy:v1"
    assert candidate.authorization_freshness == "epoch:7"

    other = make_promotion_candidate(
        candidate_id="candidate:auth-context",
        evidence_digest="digest:auth",
        evaluation_status="PASS",
        shadow_status="IMPROVED",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
        authorization_scope="scope:2",
        authorization_target="target:1",
        policy_version="policy:v1",
        authorization_freshness="epoch:7",
    )
    assert other.candidate_id != candidate.candidate_id


def test_promotion_gate_rejects_stale_authorization_context():
    from gnosis.evolution.promotion import evaluate_promotion_gate, make_promotion_candidate

    candidate = make_promotion_candidate(
        candidate_id="candidate:stale-auth",
        evidence_digest="digest:stale-auth",
        evaluation_status="PASS",
        shadow_status="IMPROVED",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
        authorization_scope="scope:v1",
        authorization_target="target:v1",
        policy_version="policy:v1",
        authorization_freshness="epoch:1",
    )
    gate = evaluate_promotion_gate(
        candidate,
        provenance_valid=True,
        expected_authorization_scope="scope:v1",
        expected_authorization_target="target:v1",
        expected_policy_version="policy:v2",
        expected_authorization_freshness="epoch:2",
    )
    assert not gate.eligible
    assert "authorization policy version is stale or mismatched" in gate.reasons
    assert "authorization freshness is stale or mismatched" in gate.reasons
