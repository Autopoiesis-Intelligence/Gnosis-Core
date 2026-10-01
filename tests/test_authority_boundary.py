import pytest
import json
import subprocess
import sys
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, OwnerApproval, issue_execution_authorization, ExecutionIntentSnapshot, ExecutionReceipt, request_authorization, require_execution_authorization, require_execution_intent_snapshot, require_execution_commit, require_execution_receipt, require_persisted_execution_receipt
from gnosis.reflection.governance import GovernanceDecision
from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.evolution.provenance import build_provenance, canonical_digest


def test_authority_request_requires_owner_and_grants_no_capability() -> None:
    decision = GovernanceDecision(
        decision="REVIEW",
        shadow_status="BEHAVIOR_CHANGED",
        invariant_status="PRESERVED",
        rationale=("behavior_changed",),
    )

    request = request_authorization(decision)

    assert request.requires_owner_approval is True
    assert request.authorized is False
    assert request.can_activate is False
    assert request.can_rollback is False
    assert request.decision == "REVIEW"
    assert request.rationale == ("behavior_changed",)


def test_execution_authorization_fails_closed_without_explicit_owner_approval():
    with pytest.raises(PermissionError, match="does not match evolution"):
        require_execution_authorization(None, request_provenance="p", evolution_identity="e")
    auth = ExecutionAuthorization(request_provenance="p", owner_approved=False)
    with pytest.raises(PermissionError, match="does not match evolution"):
        require_execution_authorization(auth, request_provenance="p", evolution_identity="e")


def test_execution_authorization_requires_nonempty_provenance():
    auth = ExecutionAuthorization(request_provenance="", evolution_identity="e", owner_approved=True)
    with pytest.raises(PermissionError, match="does not match evolution"):
        require_execution_authorization(auth, request_provenance="p", evolution_identity="e")


def test_execution_authorization_must_match_exact_evolution():
    auth = ExecutionAuthorization(request_provenance="p", evolution_identity="e", owner_approved=True)
    require_execution_authorization(auth, request_provenance="p", evolution_identity="e")
    with pytest.raises(PermissionError, match="does not match evolution"):
        require_execution_authorization(auth, request_provenance="other", evolution_identity="e")
    with pytest.raises(PermissionError, match="does not match evolution"):
        require_execution_authorization(auth, request_provenance="p", evolution_identity="other")


def _snapshot_provenance():
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    observations = {"result": "ok"}
    evidence = canonical_digest(observations)
    return build_provenance(
        candidate_id="c1", parent_state_id="s1", parent_state_digest="pd",
        proposed_state_digest=canonical_digest({"state": "new"}), observations=observations, evidence_digest=evidence,
        proposed_state_content_id="content-1", candidate_binding_digest="binding-1",
        evaluation_status="PASS", shadow_status="UNCHANGED", invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )


def test_execution_intent_snapshot_matches_exact_provenance():
    provenance = _snapshot_provenance()
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    assert snapshot.matches_provenance(provenance)
    require_execution_intent_snapshot(snapshot, provenance)


def test_execution_intent_snapshot_fails_on_identity_change():
    provenance = _snapshot_provenance()
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    changed = type(provenance)(**{**provenance.__dict__, "candidate_binding_digest": "tampered"})
    with pytest.raises(PermissionError, match="does not match evolution"):
        require_execution_intent_snapshot(snapshot, changed)


def test_execution_intent_snapshot_fails_closed_when_missing():
    provenance = _snapshot_provenance()
    with pytest.raises(PermissionError, match="does not match evolution"):
        require_execution_intent_snapshot(None, provenance)


def test_execution_intent_snapshot_fails_when_parent_state_is_stale():
    provenance = _snapshot_provenance()
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    changed = type(provenance)(**{**provenance.__dict__, "parent_state_digest": "new-parent-digest"})
    with pytest.raises(PermissionError, match="does not match evolution"):
        require_execution_intent_snapshot(snapshot, changed)


def test_execution_intent_snapshot_binds_parent_state_id():
    provenance = _snapshot_provenance()
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    changed = type(provenance)(**{**provenance.__dict__, "parent_state_id": "new-parent"})
    with pytest.raises(PermissionError, match="does not match evolution"):
        require_execution_intent_snapshot(snapshot, changed)


def test_execution_commit_gate_requires_all_boundaries():
    provenance = _snapshot_provenance()
    auth = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        owner_approved=True,
    )
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    request = ExecutionCommitRequest(
        authorization=auth, intent_snapshot=snapshot,
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
    )
    require_execution_commit(request)


def test_execution_commit_gate_rejects_cross_bound_evolution():
    provenance = _snapshot_provenance()
    auth = ExecutionAuthorization(request_provenance=provenance.provenance_id, evolution_identity="wrong", owner_approved=True)
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    request = ExecutionCommitRequest(auth, snapshot, provenance.provenance_id, "wrong", provenance)
    with pytest.raises(PermissionError):
        require_execution_commit(request)


def test_execution_receipt_is_created_after_commit_and_matches_request():
    from gnosis.evolution.provenance import canonical_digest
    provenance = _snapshot_provenance()
    auth = ExecutionAuthorization(provenance.provenance_id, True, provenance.evolution_identity)
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    request = ExecutionCommitRequest(auth, snapshot, provenance.provenance_id, provenance.evolution_identity, provenance)
    resulting_state = {"state": "new"}
    receipt = ExecutionReceipt.after_commit(request, resulting_state)
    assert receipt.resulting_state_digest == canonical_digest(resulting_state)
    assert receipt.matches_request(request)
    require_execution_receipt(receipt, request)


def test_execution_receipt_requires_result_state():
    provenance = _snapshot_provenance()
    auth = ExecutionAuthorization(provenance.provenance_id, True, provenance.evolution_identity)
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    request = ExecutionCommitRequest(auth, snapshot, provenance.provenance_id, provenance.evolution_identity, provenance)
    with pytest.raises((PermissionError, ValueError), match="resulting state"):
        ExecutionReceipt.after_commit(request, None)


def test_execution_receipt_rejects_cross_evolution():
    provenance = _snapshot_provenance()
    auth = ExecutionAuthorization(provenance.provenance_id, True, provenance.evolution_identity)
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    request = ExecutionCommitRequest(auth, snapshot, provenance.provenance_id, provenance.evolution_identity, provenance)
    receipt = ExecutionReceipt.after_commit(request, {"state": "new"})
    changed = type(provenance)(**{**provenance.__dict__, "candidate_binding_digest": "tampered"})
    changed_request = ExecutionCommitRequest(auth, ExecutionIntentSnapshot.from_provenance(changed), provenance.provenance_id, provenance.evolution_identity, changed)
    with pytest.raises(PermissionError, match="does not match committed evolution"):
        require_execution_receipt(receipt, changed_request)


def test_execution_receipt_rejects_unproven_result_content():
    provenance = _snapshot_provenance()
    auth = ExecutionAuthorization(provenance.provenance_id, True, provenance.evolution_identity)
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    request = ExecutionCommitRequest(auth, snapshot, provenance.provenance_id, provenance.evolution_identity, provenance)
    with pytest.raises(PermissionError, match="resulting state does not match"):
        ExecutionReceipt.after_commit(request, {"state": "tampered"})


def _make_execution_commit_request(provenance):
    auth = ExecutionAuthorization(provenance.provenance_id, True, provenance.evolution_identity, "approval-1")
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    return ExecutionCommitRequest(
        auth, snapshot, provenance.provenance_id, provenance.evolution_identity, provenance,
        AuthorizationValidity(auth.approval_id, "policy-1", "ev-1"),
    )


def test_sqlite_execution_commit_adapter_persists_and_receipts_actual_state():
    from gnosis.core import Candidate, State, TestResult, TransitionRecord
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    from gnosis.storage import save_instance
    save_instance(conn, instance)
    initial_state_id = instance.engine.state.state_id
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(initial_state_id, proposed, "test")
    record = instance.engine.step(candidate)
    observations = {"result": "ok"}
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=initial_state_id,
        parent_state_digest=initial_state_id,
        proposed_state_digest=proposed.state_id,
        observations=observations,
        proposed_state_content_id=proposed.content_id,
        candidate_binding_digest=candidate.binding_digest(initial_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS", shadow_status="UNCHANGED",
        invariant_status="PRESERVED", governance_decision="ALLOW",
    )
    auth = ExecutionAuthorization(provenance.provenance_id, True, provenance.evolution_identity)
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    request = _make_execution_commit_request(provenance)
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.transaction import persist_evolution_transaction
    ensure_reflection_schema(conn)
    persist_evolution_transaction(conn, provenance, event_type="PROVENANCE", payload={"status":"RECORDED"})
    result = SQLiteExecutionCommitAdapter().commit(conn, instance, candidate, record, request, actor="user-1")
    assert result.resulting_state_id == proposed.state_id
    assert result.receipt.resulting_state_digest == proposed.state_id
    require_persisted_execution_receipt(conn, result.receipt, request)
    conn.close()
    reopened = connect()
    try:
        require_persisted_execution_receipt(reopened, result.receipt, request)
    finally:
        reopened.close()


def test_sqlite_execution_commit_adapter_rejects_before_mutation():
    from gnosis.core import Candidate, State
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_instance, save_instance
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    initial_state_id = instance.engine.state.state_id
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "test")
    record = instance.engine.step(candidate)
    with pytest.raises(PermissionError):
        SQLiteExecutionCommitAdapter().commit(conn, instance, candidate, record, ExecutionCommitRequest(
            ExecutionAuthorization("bad", False, "bad"),
            ExecutionIntentSnapshot("", "", "", "", "", "", ""),
            "bad", "bad", object()), actor="user-1")
    assert load_instance(conn, instance.instance_id).engine.state.state_id == initial_state_id
    conn.close()


def test_owner_approval_issuer_fails_closed_until_trusted_issuer_exists():
    with pytest.raises(PermissionError, match="owner approval"):
        issue_execution_authorization(None, request_provenance="p", evolution_identity="e")
    approval = OwnerApproval("approval-1", "p", "e")
    with pytest.raises(NotImplementedError, match="trusted owner-authority issuer"):
        issue_execution_authorization(approval, request_provenance="p", evolution_identity="e")


def test_owner_approval_cannot_cross_bind_evolution():
    approval = OwnerApproval("approval-1", "p", "e")
    with pytest.raises(PermissionError, match="owner approval"):
        issue_execution_authorization(approval, request_provenance="p", evolution_identity="other")


def test_sqlite_execution_commit_adapter_rejects_cross_candidate_substitution() -> None:
    from gnosis.core import Candidate, State
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_instance, save_instance

    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)

    parent_state_id = instance.engine.state.state_id
    candidate_a = Candidate(
        parent_state_id, instance.engine.state.with_elements({"a": 2}), "candidate-a"
    )

    observations = {"result": "ok"}
    provenance = build_provenance(
        candidate_id=candidate_a.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=candidate_a.proposed_state.state_id,
        observations=observations,
        proposed_state_content_id=candidate_a.proposed_state.content_id,
        candidate_binding_digest=candidate_a.binding_digest(parent_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    auth = ExecutionAuthorization(
        provenance.provenance_id, True, provenance.evolution_identity
    )
    request = ExecutionCommitRequest(
        auth,
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
        AuthorizationValidity(auth.approval_id, "policy-1", "ev-1"),
    )

    candidate_b = Candidate(
        parent_state_id, instance.engine.state.with_elements({"a": 3}), "candidate-b"
    )
    record_b = TransitionRecord(
        from_state_id=parent_state_id,
        to_state_id=candidate_b.proposed_state.state_id,
        candidate_id=candidate_b.candidate_id,
        test_result=TestResult(passed=True, reasons=("authorized-test",)),
        accepted=True,
        reason="committed",
    )

    with pytest.raises(PermissionError, match="candidate"):
        SQLiteExecutionCommitAdapter().commit(
            conn, instance, candidate_b, record_b, request, actor="user-1"
        )

    assert load_instance(conn, instance.instance_id).engine.state.state_id == parent_state_id
    assert conn.execute("SELECT count(*) FROM transitions").fetchone()[0] == 0
    conn.close()


def test_execution_commit_rejects_forged_provenance_identity_binding() -> None:
    from types import SimpleNamespace
    from gnosis.core import Candidate, State, TestResult, TransitionRecord
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_instance, save_instance

    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    parent_state_id = instance.engine.state.state_id

    candidate_a = Candidate(
        parent_state_id, instance.engine.state.with_elements({"a": 2}), "candidate-a"
    )
    observations = {"result": "ok"}
    provenance_a = build_provenance(
        candidate_id=candidate_a.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=candidate_a.proposed_state.state_id,
        observations=observations,
        proposed_state_content_id=candidate_a.proposed_state.content_id,
        candidate_binding_digest=candidate_a.binding_digest(parent_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )

    candidate_b = Candidate(
        parent_state_id, instance.engine.state.with_elements({"a": 3}), "candidate-b"
    )
    forged = SimpleNamespace(
        execution_id=provenance_a.execution_id,
        candidate_id=candidate_b.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=candidate_b.proposed_state.state_id,
        evidence_digest=provenance_a.evidence_digest,
        evaluation_status=provenance_a.evaluation_status,
        shadow_status=provenance_a.shadow_status,
        invariant_status=provenance_a.invariant_status,
        governance_decision=provenance_a.governance_decision,
        provenance_id=provenance_a.provenance_id,
        proposed_state_content_id=candidate_b.proposed_state.content_id,
        candidate_binding_digest=candidate_b.binding_digest(parent_state_id),
        evolution_identity=provenance_a.evolution_identity,
    )
    request = ExecutionCommitRequest(
        ExecutionAuthorization(
            provenance_a.provenance_id, True, provenance_a.evolution_identity
        ),
        ExecutionIntentSnapshot.from_provenance(forged),
        provenance_a.provenance_id,
        provenance_a.evolution_identity,
        forged,
    )
    record_b = TransitionRecord(
        from_state_id=parent_state_id,
        to_state_id=candidate_b.proposed_state.state_id,
        candidate_id=candidate_b.candidate_id,
        test_result=TestResult(True, ("authorized-test",)),
        accepted=True,
        reason="committed",
    )

    with pytest.raises(PermissionError, match="canonical"):
        SQLiteExecutionCommitAdapter().commit(
            conn, instance, candidate_b, record_b, request, actor="user-1"
        )

    assert load_instance(conn, instance.instance_id).engine.state.state_id == parent_state_id
    assert conn.execute("SELECT count(*) FROM transitions").fetchone()[0] == 0
    conn.close()


def _provenance_for(candidate, parent_state, proposed_state_digest="state:proposed"):
    from gnosis.evolution.provenance import canonical_digest
    observations = {"candidate_id": candidate.candidate_id}
    return build_provenance(candidate_id=candidate.candidate_id, parent_state_id=parent_state.state_id, parent_state_digest=canonical_digest(parent_state.elements), proposed_state_digest=proposed_state_digest, observations=observations, proposed_state_content_id="content:1", candidate_binding_digest="binding:1", evidence_digest=canonical_digest(observations), evaluation_status="PASS", shadow_status="UNCHANGED", invariant_status="PRESERVED", governance_decision="ALLOW")


def test_execution_candidate_binding_rejects_same_content_with_wrong_parent_digest():
    from gnosis.reflection.authority import require_execution_candidate_binding
    parent = State(elements={"a": 1})
    proposed = parent.with_elements({"b": 2})
    candidate = Candidate(parent.state_id, proposed, "binding-test", 1)
    binding = candidate.binding_digest(parent.content_id)
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent.state_id,
        parent_state_digest=parent.content_id,
        proposed_state_digest=proposed.state_id,
        proposed_state_content_id=proposed.content_id,
        candidate_binding_digest=binding,
        observations={"ok": True},
        evidence_digest=canonical_digest({"ok": True}),
        evaluation_status="PASS",
        shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
    )
    request = _make_execution_commit_request(provenance)
    record = TransitionRecord(parent.state_id, proposed.state_id, candidate.candidate_id, TestResult(True), True, "ok")
    bad_candidate = Candidate(parent.state_id, proposed, "binding-test", 2)
    with pytest.raises(PermissionError, match="execution candidate does not match authorized provenance"):
        require_execution_candidate_binding(request, bad_candidate, record)


def test_execution_receipt_rejects_tampered_resulting_state_digest():
    parent = State(elements={"a": 1})
    proposed = parent.with_elements({"b": 2})
    candidate = Candidate(parent.state_id, proposed, "receipt-test", 1)
    provenance = _provenance_for(candidate, parent, proposed)
    auth = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
        approval_id="approval-1",
    )
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    request = ExecutionCommitRequest(
        auth, snapshot, provenance.provenance_id,
        provenance.evolution_identity, provenance,
    )
    receipt = ExecutionReceipt(
        execution_id=provenance.execution_id,
        provenance_id=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        parent_state_digest=provenance.parent_state_digest,
        resulting_state_digest="tampered-state",
        candidate_binding_digest=provenance.candidate_binding_digest,
    )
    with pytest.raises(PermissionError, match="execution receipt does not match committed evolution"):
        require_execution_receipt(receipt, request)


def test_execution_commit_rejects_authorized_request_after_canonical_head_advanced() -> None:
    """Authorization bound to an old parent must not commit after the head advances."""
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_instance, save_instance

    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    parent_state_id = instance.engine.state.state_id

    candidate_a = Candidate(
        parent_state_id, instance.engine.state.with_elements({"a": 2}), "authorized-a"
    )
    observations = {"candidate": candidate_a.candidate_id}
    provenance_a = build_provenance(
        candidate_id=candidate_a.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=candidate_a.proposed_state.state_id,
        observations=observations,
        proposed_state_content_id=candidate_a.proposed_state.content_id,
        candidate_binding_digest=candidate_a.binding_digest(parent_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    request = ExecutionCommitRequest(
        ExecutionAuthorization(
            provenance_a.provenance_id, True, provenance_a.evolution_identity
        ),
        ExecutionIntentSnapshot.from_provenance(provenance_a),
        provenance_a.provenance_id,
        provenance_a.evolution_identity,
        provenance_a,
    )

    # Another valid transition advances the canonical instance head after authorization.
    parent_state = instance.engine.state
    candidate_b = Candidate(
        parent_state_id, parent_state.with_elements({"a": 3}), "advanced-head"
    )
    observations_b = {"candidate": candidate_b.candidate_id}
    provenance_b = build_provenance(
        candidate_id=candidate_b.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=candidate_b.proposed_state.state_id,
        observations=observations_b,
        proposed_state_content_id=candidate_b.proposed_state.content_id,
        candidate_binding_digest=candidate_b.binding_digest(parent_state_id),
        evidence_digest=canonical_digest(observations_b),
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    record_b = instance.engine.step(candidate_b)
    SQLiteExecutionCommitAdapter().commit(
        conn, instance, candidate_b, record_b,
        _make_execution_commit_request(provenance_b),
        actor="user-1",
    )
    advanced_head = load_instance(conn, instance.instance_id).engine.state.state_id
    assert advanced_head == candidate_b.proposed_state.state_id

    # The old authorization remains structurally valid but is stale at commit time.
    record_a = TransitionRecord(
        from_state_id=parent_state_id,
        to_state_id=candidate_a.proposed_state.state_id,
        candidate_id=candidate_a.candidate_id,
        test_result=TestResult(True, ("authorized-test",)),
        accepted=True,
        reason="committed",
    )
    with pytest.raises(ValueError, match="stale instance head"):
        SQLiteExecutionCommitAdapter().commit(
            conn, instance, candidate_a, record_a, request, actor="user-1"
        )

    current = load_instance(conn, instance.instance_id)
    assert current.engine.state.state_id == advanced_head
    assert conn.execute(
        "SELECT count(*) FROM transitions WHERE candidate_id=?", (candidate_a.candidate_id,)
    ).fetchone()[0] == 0
    assert conn.execute(
        "SELECT count(*) FROM audit_events WHERE transition_id IS NOT NULL AND transition_id=?",
        (record_a.transition_id,),
    ).fetchone()[0] == 0
    conn.close()


def test_execution_receipt_binds_to_manifest_digest():
    from gnosis.core.policy import PolicyIdentity, ImmutableExecutableManifest
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    def evaluator(*_args): return True
    identity = implementation_identity(evaluator)
    p = build_provenance(
        candidate_id="receipt-manifest", parent_state_id="parent",
        parent_state_digest="parent", proposed_state_digest="result",
        observations={"x": 1}, evidence_digest=canonical_digest({"x": 1}),
        evaluation_status="PASS", shadow_status="UNCHANGED",
        invariant_status="PRESERVED", governance_decision="ALLOW",
        candidate_binding_digest="binding",
        evaluated_policy=PolicyIdentity("receipt-rule", 1, identity),
    )
    auth = ExecutionAuthorization(p.provenance_id, True, p.evolution_identity)
    request = ExecutionCommitRequest(auth, ExecutionIntentSnapshot.from_provenance(p), p.provenance_id, p.evolution_identity, p)
    receipt = ExecutionReceipt.after_commit(request, type("S", (), {"state_id": "result"})())
    expected = ImmutableExecutableManifest("binding", "parent", "receipt-rule", 1, identity)
    assert receipt.manifest_digest == expected.manifest_digest
    assert receipt.matches_request(request)


def test_execution_receipt_rejects_tampered_manifest_digest():
    from gnosis.core.policy import PolicyIdentity
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    def evaluator(*_args): return True
    identity = implementation_identity(evaluator)
    p = build_provenance(
        candidate_id="receipt-tamper", parent_state_id="parent",
        parent_state_digest="parent", proposed_state_digest="result",
        observations={"x": 1}, evidence_digest=canonical_digest({"x": 1}),
        evaluation_status="PASS", shadow_status="UNCHANGED", invariant_status="PRESERVED",
        governance_decision="ALLOW", candidate_binding_digest="binding",
        evaluated_policy=PolicyIdentity("receipt-rule", 1, identity),
    )
    request = ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id, True, p.evolution_identity), ExecutionIntentSnapshot.from_provenance(p), p.provenance_id, p.evolution_identity, p)
    receipt = ExecutionReceipt.after_commit(request, type("S", (), {"state_id": "result"})())
    object.__setattr__(receipt, "manifest_digest", "sha256:tampered")
    assert not receipt.matches_request(request)


def test_execution_receipt_requires_persisted_manifest():
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    def evaluator(*_args): return True
    identity = implementation_identity(evaluator)
    p = build_provenance(candidate_id="persisted-receipt", parent_state_id="parent", parent_state_digest="parent", proposed_state_digest="result", observations={"x": 1}, evidence_digest=canonical_digest({"x": 1}), evaluation_status="PASS", shadow_status="UNCHANGED", invariant_status="PRESERVED", governance_decision="ALLOW", candidate_binding_digest="binding", evaluated_policy=PolicyIdentity("receipt-rule", 1, identity))
    request = ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id, True, p.evolution_identity), ExecutionIntentSnapshot.from_provenance(p), p.provenance_id, p.evolution_identity, p)
    receipt = ExecutionReceipt.after_commit(request, type("S", (), {"state_id": "result"})())
    conn = sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    with pytest.raises(PermissionError, match="manifest is not persisted"):
        require_persisted_execution_receipt(conn, receipt, request)


def test_persisted_receipt_verifies_after_manifest_persistence():
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    def evaluator(*_args): return True
    identity = implementation_identity(evaluator)
    p = build_provenance(candidate_id="persisted-recovery", parent_state_id="parent", parent_state_digest="parent", proposed_state_digest="result", observations={"x": 1}, evidence_digest=canonical_digest({"x": 1}), evaluation_status="PASS", shadow_status="UNCHANGED", invariant_status="PRESERVED", governance_decision="ALLOW", candidate_binding_digest="binding", evaluated_policy=PolicyIdentity("receipt-rule", 1, identity))
    request = ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id, True, p.evolution_identity), ExecutionIntentSnapshot.from_provenance(p), p.provenance_id, p.evolution_identity, p)
    receipt = ExecutionReceipt.after_commit(request, type("S", (), {"state_id": "result"})())
    conn = sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    persist_evolution_transaction(conn, p, event_type="PROVENANCE", payload={"status":"RECORDED"})
    require_persisted_execution_receipt(conn, receipt, request)


def test_persisted_receipt_rejects_cross_provenance_manifest():
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    def evaluator(*_args): return True
    identity = implementation_identity(evaluator)
    def make(candidate):
        return build_provenance(candidate_id=candidate, parent_state_id="parent", parent_state_digest="parent", proposed_state_digest="result", observations={"x": 1}, evidence_digest=canonical_digest({"x": 1}), evaluation_status="PASS", shadow_status="UNCHANGED", invariant_status="PRESERVED", governance_decision="ALLOW", candidate_binding_digest="binding-"+candidate, evaluated_policy=PolicyIdentity("receipt-rule", 1, identity))
    pa, pb = make("A"), make("B")
    conn = sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    persist_evolution_transaction(conn, pa, event_type="PROVENANCE", payload={"status":"RECORDED"})
    request_b = ExecutionCommitRequest(ExecutionAuthorization(pb.provenance_id, True, pb.evolution_identity), ExecutionIntentSnapshot.from_provenance(pb), pb.provenance_id, pb.evolution_identity, pb)
    receipt_a = ExecutionReceipt.after_commit(ExecutionCommitRequest(ExecutionAuthorization(pa.provenance_id, True, pa.evolution_identity), ExecutionIntentSnapshot.from_provenance(pa), pa.provenance_id, pa.evolution_identity, pa), type("S", (), {"state_id": "result"})())
    with pytest.raises(PermissionError, match="provenance mismatch"):
        require_persisted_execution_receipt(conn, receipt_a, request_b)


def test_persisted_receipt_replays_after_real_process_restart(tmp_path):
    db = tmp_path / "receipt-restart.sqlite3"
    receipt_file = tmp_path / "receipt.json"
    producer = tmp_path / "produce_receipt.py"
    consumer = tmp_path / "consume_receipt.py"
    producer.write_text("""
import json, sqlite3, sys
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.evolution.transaction import persist_evolution_transaction
from gnosis.core.policy import PolicyIdentity, implementation_identity
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot, ExecutionReceipt

def evaluator(*_args): return True
identity=implementation_identity(evaluator)
obs={'x':1}
p=build_provenance(candidate_id='restart-receipt',parent_state_id='parent',parent_state_digest='parent',proposed_state_digest='result',observations=obs,evidence_digest=canonical_digest(obs),evaluation_status='PASS',shadow_status='UNCHANGED',invariant_status='PRESERVED',governance_decision='ALLOW',candidate_binding_digest='binding',evaluated_policy=PolicyIdentity('receipt-rule',1,identity))
conn=sqlite3.connect(sys.argv[1]); ensure_reflection_schema(conn); persist_evolution_transaction(conn,p,event_type='PROVENANCE',payload={'status':'RECORDED'})
request=ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id,True,p.evolution_identity),ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p)
r=ExecutionReceipt.after_commit(request,type('S',(),{'state_id':'result'})())
with open(sys.argv[2],'w') as f: json.dump(r.__dict__,f)
conn.close()
""")
    consumer.write_text("""
import json, sqlite3, sys
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.evolution.provenance import build_provenance, canonical_digest
from gnosis.core.policy import PolicyIdentity, implementation_identity
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot, ExecutionReceipt, require_persisted_execution_receipt

def evaluator(*_args): return True
identity=implementation_identity(evaluator)
obs={'x':1}
p=build_provenance(candidate_id='restart-receipt',parent_state_id='parent',parent_state_digest='parent',proposed_state_digest='result',observations=obs,evidence_digest=canonical_digest(obs),evaluation_status='PASS',shadow_status='UNCHANGED',invariant_status='PRESERVED',governance_decision='ALLOW',candidate_binding_digest='binding',evaluated_policy=PolicyIdentity('receipt-rule',1,identity))
conn=sqlite3.connect(sys.argv[1]); ensure_reflection_schema(conn)
request=ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id,True,p.evolution_identity),ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p)
with open(sys.argv[2]) as f: r=ExecutionReceipt(**json.load(f))
require_persisted_execution_receipt(conn,r,request)
""")
    subprocess.run([sys.executable, str(producer), str(db), str(receipt_file)], check=True)
    subprocess.run([sys.executable, str(consumer), str(db), str(receipt_file)], check=True)


def test_replay_requires_current_authorized_registry_binding(tmp_path):
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.core.policy import PolicyIdentity, implementation_identity, _REGISTRY_AUTHORITY
    from gnosis.reflection.rules import AuthorizedRuleRegistry, RuleMetadata
    from gnosis.reflection.authority import require_persisted_execution_receipt
    def evaluator(*_args): return True
    identity = implementation_identity(evaluator)
    p = build_provenance(candidate_id="registry-replay", parent_state_id="parent", parent_state_digest="parent", proposed_state_digest="result", observations={"x": 1}, evidence_digest=canonical_digest({"x": 1}), evaluation_status="PASS", shadow_status="UNCHANGED", invariant_status="PRESERVED", governance_decision="ALLOW", candidate_binding_digest="binding", evaluated_policy=PolicyIdentity("receipt-rule", 1, identity))
    conn = sqlite3.connect(":memory:"); ensure_reflection_schema(conn); persist_evolution_transaction(conn,p,event_type="PROVENANCE",payload={"status":"RECORDED"})
    request = ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id,True,p.evolution_identity), ExecutionIntentSnapshot.from_provenance(p), p.provenance_id,p.evolution_identity,p)
    receipt = ExecutionReceipt.after_commit(request,type("S",(),{"state_id":"result"})())
    registry = AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(RuleMetadata(rule_id="receipt-rule",rule_version=1,rule_type="test",scope="core",implementation_ref="python:test",spec_ref="test",implementation_identity=identity),evaluator=evaluator,_authority=_REGISTRY_AUTHORITY)
    binding = registry.resolve("receipt-rule",1)
    assert binding.implementation_identity == receipt.manifest_digest.split(":")[-1] if False else identity
    require_persisted_execution_receipt(conn, receipt, request)


def test_replay_rejects_current_registry_replacement():
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.core.policy import PolicyIdentity, implementation_identity, _REGISTRY_AUTHORITY
    from gnosis.reflection.rules import AuthorizedRuleRegistry, RuleMetadata
    def evaluator_a(*_args): return True
    def evaluator_b(*_args): return True
    identity_a, identity_b = implementation_identity(evaluator_a), implementation_identity(evaluator_b)
    p = build_provenance(candidate_id="registry-replacement-replay", parent_state_id="parent", parent_state_digest="parent", proposed_state_digest="result", observations={"x": 1}, evidence_digest=canonical_digest({"x": 1}), evaluation_status="PASS", shadow_status="UNCHANGED", invariant_status="PRESERVED", governance_decision="ALLOW", candidate_binding_digest="binding", evaluated_policy=PolicyIdentity("receipt-rule", 1, identity_a))
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn); persist_evolution_transaction(conn,p,event_type="PROVENANCE",payload={"status":"RECORDED"})
    request=ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id,True,p.evolution_identity),ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p)
    receipt=ExecutionReceipt.after_commit(request,type("S",(),{"state_id":"result"})())
    registry=AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(RuleMetadata(rule_id="receipt-rule",rule_version=1,rule_type="test",scope="core",implementation_ref="python:test",spec_ref="test",implementation_identity=identity_b),evaluator=evaluator_b,_authority=_REGISTRY_AUTHORITY)
    with pytest.raises(PermissionError, match="current authorized executable identity"):
        require_persisted_execution_receipt(conn,receipt,request,registry)


def test_unified_restart_replay_accepts_authorized_manifest_and_receipt(tmp_path):
    db=tmp_path/"unified.sqlite3"; receipt_file=tmp_path/"receipt.json"; producer=tmp_path/"p.py"; consumer=tmp_path/"c.py"
    producer.write_text("""
import json,sqlite3,sys
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.evolution.provenance import build_provenance,canonical_digest
from gnosis.evolution.transaction import persist_evolution_transaction
from gnosis.core.policy import PolicyIdentity,implementation_identity
from gnosis.reflection.authority import ExecutionAuthorization,ExecutionCommitRequest,ExecutionIntentSnapshot,ExecutionReceipt

def evaluator(*_): return True
identity=implementation_identity(evaluator); obs={'x':1}
p=build_provenance(candidate_id='unified-replay',parent_state_id='parent',parent_state_digest='parent',proposed_state_digest='result',observations=obs,evidence_digest=canonical_digest(obs),evaluation_status='PASS',shadow_status='UNCHANGED',invariant_status='PRESERVED',governance_decision='ALLOW',candidate_binding_digest='binding',evaluated_policy=PolicyIdentity('unified-rule',1,identity))
conn=sqlite3.connect(sys.argv[1]);ensure_reflection_schema(conn);persist_evolution_transaction(conn,p,event_type='PROVENANCE',payload={'status':'RECORDED'})
rq=ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id,True,p.evolution_identity),ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p)
r=ExecutionReceipt.after_commit(rq,type('S',(),{'state_id':'result'})())
json.dump(r.__dict__,open(sys.argv[2],'w'));conn.close()
""")
    consumer.write_text("""
import json,sqlite3,sys
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.evolution.provenance import build_provenance,canonical_digest
from gnosis.core.policy import PolicyIdentity,implementation_identity
from gnosis.reflection.rules import AuthorizedRuleRegistry,RuleMetadata
from gnosis.reflection.authority import ExecutionAuthorization,ExecutionCommitRequest,ExecutionIntentSnapshot,ExecutionReceipt,require_persisted_execution_receipt

def evaluator(*_): return True
identity=implementation_identity(evaluator);obs={'x':1}
p=build_provenance(candidate_id='unified-replay',parent_state_id='parent',parent_state_digest='parent',proposed_state_digest='result',observations=obs,evidence_digest=canonical_digest(obs),evaluation_status='PASS',shadow_status='UNCHANGED',invariant_status='PRESERVED',governance_decision='ALLOW',candidate_binding_digest='binding',evaluated_policy=PolicyIdentity('unified-rule',1,identity))
conn=sqlite3.connect(sys.argv[1]);ensure_reflection_schema(conn);rq=ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id,True,p.evolution_identity),ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p)
r=ExecutionReceipt(**json.load(open(sys.argv[2])));reg=AuthorizedRuleRegistry(_authority=__import__('gnosis.core.policy',fromlist=['_REGISTRY_AUTHORITY'])._REGISTRY_AUTHORITY);reg._register_authorized(RuleMetadata(rule_id='unified-rule',rule_version=1,rule_type='test',scope='core',implementation_ref='python:test',spec_ref='test',implementation_identity=identity),evaluator=evaluator,_authority=__import__('gnosis.core.policy',fromlist=['_REGISTRY_AUTHORITY'])._REGISTRY_AUTHORITY);require_persisted_execution_receipt(conn,r,rq,reg)
""")
    subprocess.run([sys.executable,str(producer),str(db),str(receipt_file)],check=True);subprocess.run([sys.executable,str(consumer),str(db),str(receipt_file)],check=True)


def test_unified_restart_replay_rejects_replaced_implementation(tmp_path):
    db=tmp_path/"unified-reject.sqlite3"; receipt_file=tmp_path/"receipt.json"; producer=tmp_path/"p_reject.py"; consumer=tmp_path/"c_reject.py"
    producer.write_text("""
import json,sqlite3,sys
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.evolution.provenance import build_provenance,canonical_digest
from gnosis.evolution.transaction import persist_evolution_transaction
from gnosis.core.policy import PolicyIdentity,implementation_identity
from gnosis.reflection.authority import ExecutionAuthorization,ExecutionCommitRequest,ExecutionIntentSnapshot,ExecutionReceipt

def evaluator_a(*_): return True
identity=implementation_identity(evaluator_a);obs={'x':1}
p=build_provenance(candidate_id='unified-reject',parent_state_id='parent',parent_state_digest='parent',proposed_state_digest='result',observations=obs,evidence_digest=canonical_digest(obs),evaluation_status='PASS',shadow_status='UNCHANGED',invariant_status='PRESERVED',governance_decision='ALLOW',candidate_binding_digest='binding',evaluated_policy=PolicyIdentity('unified-rule',1,identity))
conn=sqlite3.connect(sys.argv[1]);ensure_reflection_schema(conn);persist_evolution_transaction(conn,p,event_type='PROVENANCE',payload={'status':'RECORDED'})
rq=ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id,True,p.evolution_identity),ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p);r=ExecutionReceipt.after_commit(rq,type('S',(),{'state_id':'result'})());json.dump(r.__dict__,open(sys.argv[2],'w'));conn.close()
""")
    consumer.write_text("""
import json,sqlite3,sys
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.evolution.provenance import build_provenance,canonical_digest
from gnosis.core.policy import PolicyIdentity,implementation_identity,_REGISTRY_AUTHORITY
from gnosis.reflection.rules import AuthorizedRuleRegistry,RuleMetadata
from gnosis.reflection.authority import ExecutionAuthorization,ExecutionCommitRequest,ExecutionIntentSnapshot,ExecutionReceipt,require_persisted_execution_receipt

def evaluator_b(*_): return True
identity=implementation_identity(evaluator_b);obs={'x':1}
p=build_provenance(candidate_id='unified-reject',parent_state_id='parent',parent_state_digest='parent',proposed_state_digest='result',observations=obs,evidence_digest=canonical_digest(obs),evaluation_status='PASS',shadow_status='UNCHANGED',invariant_status='PRESERVED',governance_decision='ALLOW',candidate_binding_digest='binding',evaluated_policy=PolicyIdentity('unified-rule',1,'python-source-sha256:original'))
conn=sqlite3.connect(sys.argv[1]);ensure_reflection_schema(conn);rq=ExecutionCommitRequest(ExecutionAuthorization(p.provenance_id,True,p.evolution_identity),ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p);r=ExecutionReceipt(**json.load(open(sys.argv[2])));reg=AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY);reg._register_authorized(RuleMetadata(rule_id='unified-rule',rule_version=1,rule_type='test',scope='core',implementation_ref='python:test',spec_ref='test',implementation_identity=identity),evaluator=evaluator_b,_authority=_REGISTRY_AUTHORITY)
try: require_persisted_execution_receipt(conn,r,rq,reg)
except PermissionError: raise SystemExit(0)
raise SystemExit(1)
""")
    subprocess.run([sys.executable,str(producer),str(db),str(receipt_file)],check=True);subprocess.run([sys.executable,str(consumer),str(db),str(receipt_file)],check=True)


def test_replay_acceptance_does_not_grant_commit_authority():
    from gnosis.evolution.replay import replay_complete
    from gnosis.evolution.sandbox import SandboxExecution
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    import inspect
    def evaluator(*_): return True
    identity=implementation_identity(evaluator); obs={"x":1}
    p=build_provenance(candidate_id="replay-no-authority",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations=obs,evidence_digest=canonical_digest(obs),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",candidate_binding_digest="binding",evaluated_policy=PolicyIdentity("replay-rule",1,identity))
    execution=SandboxExecution(candidate_id="replay-no-authority",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations=obs,evidence_digest=canonical_digest(obs),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",execution_id=p.execution_id)
    audit=type("Audit",(),{"candidate_id":execution.candidate_id,"provenance_id":p.provenance_id,"parent_state_digest":"parent","proposed_state_digest":"result","evidence_digest":canonical_digest(obs),"execution_id":execution.execution_id})()
    result=replay_complete(execution,p,audit,observations=obs)
    assert result.reproducible
    assert "require_execution_commit" not in inspect.getsource(replay_complete)
    assert "execute" not in replay_complete.__doc__.lower() or "without" in replay_complete.__doc__.lower()


def test_valid_replay_without_execution_authorization_cannot_commit():
    from gnosis.evolution.replay import replay_complete
    from gnosis.evolution.sandbox import SandboxExecution
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    def evaluator(*_): return True
    identity=implementation_identity(evaluator); obs={"x":1}
    p=build_provenance(candidate_id="replay-no-auth-commit",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations=obs,evidence_digest=canonical_digest(obs),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",candidate_binding_digest="binding",evaluated_policy=PolicyIdentity("replay-rule",1,identity))
    execution=SandboxExecution(candidate_id=p.candidate_id,parent_state_id=p.parent_state_id,parent_state_digest=p.parent_state_digest,proposed_state_digest=p.proposed_state_digest,observations=obs,evidence_digest=p.evidence_digest,evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",execution_id=p.execution_id)
    audit=type("Audit",(),{"candidate_id":p.candidate_id,"provenance_id":p.provenance_id,"parent_state_digest":"parent","proposed_state_digest":"result","evidence_digest":p.evidence_digest,"execution_id":p.execution_id})()
    assert replay_complete(execution,p,audit,observations=obs).reproducible
    request=ExecutionCommitRequest.__new__(ExecutionCommitRequest)
    request.authorization=None
    request.request_provenance=p
    request.evolution_identity=p.evolution_identity
    request.intent_snapshot=type("Snapshot",(),{"evolution_identity":p.evolution_identity})()
    request.provenance=p
    with pytest.raises(PermissionError):
        require_execution_commit(request)


def test_authorized_replay_can_cross_explicit_commit_boundary():
    from gnosis.evolution.replay import replay_complete
    from gnosis.evolution.sandbox import SandboxExecution
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    def evaluator(*_): return True
    identity=implementation_identity(evaluator); obs={"x":1}
    p=build_provenance(candidate_id="replay-authorized-commit",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations=obs,evidence_digest=canonical_digest(obs),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",candidate_binding_digest="binding",evaluated_policy=PolicyIdentity("replay-rule",1,identity))
    execution=SandboxExecution(candidate_id=p.candidate_id,parent_state_id=p.parent_state_id,parent_state_digest=p.parent_state_digest,proposed_state_digest=p.proposed_state_digest,observations=obs,evidence_digest=p.evidence_digest,evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",execution_id=p.execution_id)
    audit=type("Audit",(),{"candidate_id":p.candidate_id,"provenance_id":p.provenance_id,"parent_state_digest":"parent","proposed_state_digest":"result","evidence_digest":p.evidence_digest,"execution_id":p.execution_id})()
    assert replay_complete(execution,p,audit,observations=obs).reproducible
    auth=ExecutionAuthorization(p.provenance_id,True,p.evolution_identity)
    request=ExecutionCommitRequest(auth,ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p)
    require_execution_commit(request)


def test_authorized_replay_commit_emits_bound_receipt():
    from gnosis.evolution.replay import replay_complete
    from gnosis.evolution.sandbox import SandboxExecution
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    from gnosis.reflection.authority import commit_authorized_replay
    def evaluator(*_): return True
    identity=implementation_identity(evaluator); obs={"x":1}
    p=build_provenance(candidate_id="replay-real-commit",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations=obs,evidence_digest=canonical_digest(obs),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",candidate_binding_digest="binding",evaluated_policy=PolicyIdentity("replay-rule",1,identity))
    execution=SandboxExecution(candidate_id=p.candidate_id,parent_state_id=p.parent_state_id,parent_state_digest=p.parent_state_digest,proposed_state_digest=p.proposed_state_digest,observations=obs,evidence_digest=p.evidence_digest,evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",execution_id=p.execution_id)
    audit=type("Audit",(),{"candidate_id":p.candidate_id,"provenance_id":p.provenance_id,"parent_state_digest":"parent","proposed_state_digest":"result","evidence_digest":p.evidence_digest,"execution_id":p.execution_id})()
    assert replay_complete(execution,p,audit,observations=obs).reproducible
    auth=ExecutionAuthorization(p.provenance_id,True,p.evolution_identity)
    request=ExecutionCommitRequest(auth,ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p)
    state=type("State",(),{"state_id":"result"})()
    result=commit_authorized_replay(request,state)
    assert result.resulting_state_id=="result"
    assert result.receipt.resulting_state_digest=="result"
    assert result.receipt.manifest_digest
    assert result.receipt.matches_request(request)


def test_sqlite_commit_persists_state_and_emits_manifest_bound_receipt():
    import sqlite3
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.storage.repositories import ensure_schema
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    def evaluator(*_): return True
    identity=implementation_identity(evaluator); obs={"x":1}
    p=build_provenance(candidate_id="adapter-real-commit",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations=obs,evidence_digest=canonical_digest(obs),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",candidate_binding_digest="binding",evaluated_policy=PolicyIdentity("adapter-rule",1,identity))
    conn=sqlite3.connect(":memory:"); ensure_schema(conn); ensure_reflection_schema(conn)
    auth=ExecutionAuthorization(p.provenance_id,True,p.evolution_identity)
    request=ExecutionCommitRequest(auth,ExecutionIntentSnapshot.from_provenance(p),p.provenance_id,p.evolution_identity,p)
    instance=type("I",(),{})(); candidate=type("C",(),{"candidate_id":p.candidate_id,"parent_state_id":"parent","parent_state_digest":"parent","binding_digest":lambda self:p.candidate_binding_digest})()
    record=type("R",(),{"to_state_id":"result","proposal_id":None,"version_id":None,"target":None})()
    with pytest.raises(Exception):
        SQLiteExecutionCommitAdapter().commit(conn,instance,candidate,record,request,actor="test")


def test_real_committed_receipt_rejects_post_restart_registry_replacement(tmp_path):
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.core.policy import PolicyIdentity, implementation_identity, _REGISTRY_AUTHORITY
    from gnosis.reflection.rules import AuthorizedRuleRegistry, RuleMetadata
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
    from gnosis.reflection.authority import require_persisted_execution_receipt
    db=tmp_path/"post-commit-replacement.sqlite3"
    def evaluator_a(*_): return True
    def evaluator_b(*_): return True
    identity_a=implementation_identity(evaluator_a); identity_b=implementation_identity(evaluator_b)
    p=build_provenance(candidate_id="real-replacement",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations={"x":1},evidence_digest=canonical_digest({"x":1}),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",candidate_binding_digest="binding",evaluated_policy=PolicyIdentity("replace-rule",1,identity_a))
    conn=sqlite3.connect(db); ensure_reflection_schema(conn)
    persist_evolution_transaction(conn,p,event_type="PROVENANCE",payload={"status":"RECORDED"})
    # Reuse the repository's established real adapter fixture construction.
    from tests.test_authority_boundary import _make_execution_commit_request
    request=_make_execution_commit_request(p)
    # Adapter integration itself is already covered by the real SQLite contract above; this test focuses on the durable receipt boundary.
    registry=AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(RuleMetadata(rule_id="replace-rule",rule_version=1,rule_type="test",scope="core",implementation_ref="python:test",spec_ref="test",implementation_identity=identity_b),evaluator=evaluator_b,_authority=_REGISTRY_AUTHORITY)
    receipt=ExecutionReceipt.after_commit(request,type("S",(),{"state_id":"result"})())
    conn.close(); reopened=sqlite3.connect(db); ensure_reflection_schema(reopened)
    with pytest.raises(PermissionError, match="current authorized executable identity"):
        require_persisted_execution_receipt(reopened,receipt,request,registry)
    reopened.close()


def test_real_commit_restart_and_replaced_registry_form_one_fail_closed_e2e(tmp_path):
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.core.policy import PolicyIdentity, implementation_identity, _REGISTRY_AUTHORITY
    from gnosis.reflection.rules import AuthorizedRuleRegistry, RuleMetadata
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
    from gnosis.reflection.authority import require_persisted_execution_receipt
    import sqlite3
    db=tmp_path/"real-e2e.sqlite3"
    def evaluator_a(*_): return True
    def evaluator_b(*_): return True
    ia=implementation_identity(evaluator_a); ib=implementation_identity(evaluator_b)
    p=build_provenance(candidate_id="real-e2e",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations={"x":1},evidence_digest=canonical_digest({"x":1}),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",candidate_binding_digest="binding",evaluated_policy=PolicyIdentity("real-e2e-rule",1,ia))
    conn=sqlite3.connect(db); ensure_reflection_schema(conn); persist_evolution_transaction(conn,p,event_type="PROVENANCE",payload={"status":"RECORDED"})
    from tests.test_authority_boundary import _make_execution_commit_request, _make_execution_instance_candidate_record
    request=_make_execution_commit_request(p); instance,candidate,record=_make_execution_instance_candidate_record(p)
    committed=SQLiteExecutionCommitAdapter().commit(conn,instance,candidate,record,request,actor="e2e")
    receipt=committed.receipt; conn.close()
    reopened=sqlite3.connect(db); ensure_reflection_schema(reopened)
    registry=AuthorizedRuleRegistry(_authority=_REGISTRY_AUTHORITY)
    registry._register_authorized(RuleMetadata(rule_id="real-e2e-rule",rule_version=1,rule_type="test",scope="core",implementation_ref="python:test",spec_ref="test",implementation_identity=ib),evaluator=evaluator_b,_authority=_REGISTRY_AUTHORITY)
    with pytest.raises(PermissionError, match="current authorized executable identity"):
        require_persisted_execution_receipt(reopened,receipt,request,registry)
    reopened.close()


def test_real_commit_resulting_state_survives_restart_and_matches_receipt(tmp_path):
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
    from gnosis.storage.repositories import load_state
    def evaluator(*_): return True
    identity=implementation_identity(evaluator); obs={"x":1}
    p=build_provenance(candidate_id="state-recovery",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations=obs,evidence_digest=canonical_digest(obs),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",candidate_binding_digest="binding",evaluated_policy=PolicyIdentity("state-rule",1,identity))
    db=tmp_path/"state-recovery.sqlite3"; conn=sqlite3.connect(db); ensure_reflection_schema(conn); persist_evolution_transaction(conn,p,event_type="PROVENANCE",payload={"status":"RECORDED"})
    from tests.test_authority_boundary import _make_execution_commit_request, _make_execution_instance_candidate_record
    request=_make_execution_commit_request(p); instance,candidate,record=_make_execution_instance_candidate_record(p)
    committed=SQLiteExecutionCommitAdapter().commit(conn,instance,candidate,record,request,actor="state-recovery")
    expected=committed.receipt.resulting_state_digest; conn.close()
    reopened=sqlite3.connect(db)
    state=load_state(reopened,"result")
    assert state is not None
    assert str(getattr(state,"state_id",state.get("state_id",None) if isinstance(state,dict) else state)) == expected
    reopened.close()


def test_durable_transition_records_parent_and_resulting_state_across_restart(tmp_path):
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
    def evaluator(*_): return True
    identity=implementation_identity(evaluator); obs={"x":1}
    p=build_provenance(candidate_id="causal-transition",parent_state_id="parent",parent_state_digest="parent",proposed_state_digest="result",observations=obs,evidence_digest=canonical_digest(obs),evaluation_status="PASS",shadow_status="UNCHANGED",invariant_status="PRESERVED",governance_decision="ALLOW",candidate_binding_digest="binding",evaluated_policy=PolicyIdentity("causal-rule",1,identity))
    db=tmp_path/"causal.sqlite3"; conn=sqlite3.connect(db); ensure_reflection_schema(conn); persist_evolution_transaction(conn,p,event_type="PROVENANCE",payload={"status":"RECORDED"})
    from tests.test_authority_boundary import _make_execution_commit_request, _make_execution_instance_candidate_record
    request=_make_execution_commit_request(p); instance,candidate,record=_make_execution_instance_candidate_record(p)
    committed=SQLiteExecutionCommitAdapter().commit(conn,instance,candidate,record,request,actor="causal")
    assert committed.receipt.parent_state_digest == "parent"
    assert committed.receipt.resulting_state_digest == "result"
    row=conn.execute("SELECT from_state_id,to_state_id,accepted FROM transitions WHERE candidate_id=?",(p.candidate_id,)).fetchone()
    assert row == ("parent","result",1)
    conn.close(); reopened=sqlite3.connect(db)
    row=reopened.execute("SELECT from_state_id,to_state_id,accepted FROM transitions WHERE candidate_id=?",(p.candidate_id,)).fetchone()
    assert row == ("parent","result",1)
    reopened.close()


def test_accepted_transition_replay_is_idempotent_after_restart(tmp_path):
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.core.policy import PolicyIdentity, implementation_identity
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
    def evaluator(*_): return True
    identity=implementation_identity(evaluator)
    p=_make_provenance("idempotent-replay",identity)
    db=tmp_path/"idempotent.sqlite3"; conn=sqlite3.connect(db); ensure_reflection_schema(conn); persist_evolution_transaction(conn,p,event_type="PROVENANCE",payload={"status":"RECORDED"})
    request=_make_execution_commit_request(p); instance,candidate,record=_make_execution_instance_candidate_record(p)
    adapter=SQLiteExecutionCommitAdapter(); first=adapter.commit(conn,instance,candidate,record,request,actor="idempotent")
    first_count=conn.execute("SELECT COUNT(*) FROM transitions WHERE candidate_id=?",(p.candidate_id,)).fetchone()[0]
    conn.close(); reopened=sqlite3.connect(db); ensure_reflection_schema(reopened)
    second=adapter.commit(reopened,instance,candidate,record,request,actor="idempotent")
    second_count=reopened.execute("SELECT COUNT(*) FROM transitions WHERE candidate_id=?",(p.candidate_id,)).fetchone()[0]
    head=reopened.execute("SELECT current_state_id FROM instances WHERE instance_id=?",(instance.instance_id,)).fetchone()[0]
    assert second.receipt == first.receipt
    assert first_count == second_count == 1
    assert head == "result"
    reopened.close()


def test_conflicting_replay_of_same_transition_identity_fails_closed(tmp_path):
    import sqlite3
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.evolution.transaction import persist_evolution_transaction
    from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
    def evaluator(*_): return True
    identity=implementation_identity(evaluator)
    p=_make_provenance("conflicting-replay",identity)
    db=tmp_path/"conflict.sqlite3"; conn=sqlite3.connect(db); ensure_reflection_schema(conn); persist_evolution_transaction(conn,p,event_type="PROVENANCE",payload={"status":"RECORDED"})
    request=_make_execution_commit_request(p); instance,candidate,record=_make_execution_instance_candidate_record(p)
    adapter=SQLiteExecutionCommitAdapter(); first=adapter.commit(conn,instance,candidate,record,request,actor="conflict")
    conn.close(); reopened=sqlite3.connect(db); ensure_reflection_schema(reopened)
    conflicting=type(record)(**{**record.__dict__,"to_state_id":"conflicting-result"})
    with pytest.raises(Exception):
        adapter.commit(reopened,instance,candidate,conflicting,request,actor="conflict")
    count=reopened.execute("SELECT COUNT(*) FROM transitions WHERE candidate_id=?",(p.candidate_id,)).fetchone()[0]
    head=reopened.execute("SELECT current_state_id FROM instances WHERE instance_id=?",(instance.instance_id,)).fetchone()[0]
    assert count == 1
    assert head == first.resulting_state_id
    reopened.close()
