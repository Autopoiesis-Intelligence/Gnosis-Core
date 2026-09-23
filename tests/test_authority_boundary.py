import pytest
from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, OwnerApproval, issue_execution_authorization, ExecutionIntentSnapshot, ExecutionReceipt, SQLiteExecutionCommitAdapter, request_authorization, require_execution_authorization, require_execution_intent_snapshot, require_execution_commit, require_execution_receipt
from gnosis.reflection.governance import GovernanceDecision
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
    auth = ExecutionAuthorization(provenance.provenance_id, True, provenance.evolution_identity)
    snapshot = ExecutionIntentSnapshot.from_provenance(provenance)
    return ExecutionCommitRequest(auth, snapshot, provenance.provenance_id, provenance.evolution_identity, provenance)


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
    request = ExecutionCommitRequest(auth, snapshot, provenance.provenance_id, provenance.evolution_identity, provenance)
    result = SQLiteExecutionCommitAdapter().commit(conn, instance, candidate, record, request, actor="user-1")
    assert result.resulting_state_id == proposed.state_id
    assert result.receipt.resulting_state_digest == proposed.state_id
    conn.close()


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


def test_self_limitation_rejects_unverified_commit_before_persistence():
    provenance = _snapshot_provenance()
    pending = type(provenance)(**{
        **provenance.__dict__,
        "evaluation_status": "PENDING",
        "governance_decision": "REVIEW",
    })
    auth = ExecutionAuthorization(
        request_provenance=pending.provenance_id,
        evolution_identity=pending.evolution_identity,
        owner_approved=True,
    )
    snapshot = ExecutionIntentSnapshot.from_provenance(pending)
    request = ExecutionCommitRequest(
        authorization=auth,
        intent_snapshot=snapshot,
        request_provenance=pending.provenance_id,
        evolution_identity=pending.evolution_identity,
        provenance=pending,
    )
    with pytest.raises(PermissionError):
        require_execution_commit(request)


def test_self_limitation_rejects_contradictory_evidence_before_persistence():
    provenance = _snapshot_provenance()
    contradictory = type(provenance)(**{
        **provenance.__dict__,
        "evaluation_status": "FAIL",
        "governance_decision": "ALLOW",
        "invariant_status": "VIOLATED",
    })
    auth = ExecutionAuthorization(
        request_provenance=contradictory.provenance_id,
        evolution_identity=contradictory.evolution_identity,
        owner_approved=True,
    )
    snapshot = ExecutionIntentSnapshot.from_provenance(contradictory)
    request = ExecutionCommitRequest(
        authorization=auth,
        intent_snapshot=snapshot,
        request_provenance=contradictory.provenance_id,
        evolution_identity=contradictory.evolution_identity,
        provenance=contradictory,
    )
    with pytest.raises(PermissionError):
        require_execution_commit(request)


def test_sqlite_execution_commit_rejects_unverified_self_evolution_without_durable_mutation():
    from gnosis.core import Candidate, State
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_instance, save_instance

    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    parent_state_id = instance.engine.state.state_id
    proposed = instance.engine.state.with_elements({"a": 2})
    candidate = Candidate(parent_state_id, proposed, "self-evolution")
    record = instance.engine.step(candidate)

    observations = {"result": "insufficient"}
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=proposed.state_id,
        observations=observations,
        proposed_state_content_id=proposed.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PENDING",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="REVIEW",
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
    )

    before = load_instance(conn, instance.instance_id).engine.state.state_id
    before_transitions = conn.execute("SELECT count(*) FROM transitions").fetchone()[0]

    with pytest.raises(PermissionError, match="verified evaluation"):
        SQLiteExecutionCommitAdapter().commit(
            conn, instance, candidate, record, request, actor="user-1"
        )

    assert load_instance(conn, instance.instance_id).engine.state.state_id == before
    assert conn.execute("SELECT count(*) FROM transitions").fetchone()[0] == before_transitions
    conn.close()


def test_sqlite_execution_commit_rejects_contradictory_self_evolution_without_durable_mutation():
    from gnosis.core import Candidate, State
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_instance, save_instance

    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    parent_state_id = instance.engine.state.state_id
    proposed = instance.engine.state.with_elements({"a": 2})
    candidate = Candidate(parent_state_id, proposed, "self-evolution")
    record = instance.engine.step(candidate)

    observations = {"result": "contradictory"}
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent_state_id,
        parent_state_digest=parent_state_id,
        proposed_state_digest=proposed.state_id,
        observations=observations,
        proposed_state_content_id=proposed.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="FAIL",
        shadow_status="UNCHANGED",
        invariant_status="VIOLATED",
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
    )

    before = load_instance(conn, instance.instance_id).engine.state.state_id
    before_transitions = conn.execute("SELECT count(*) FROM transitions").fetchone()[0]

    with pytest.raises(PermissionError, match="preserved invariants"):
        SQLiteExecutionCommitAdapter().commit(
            conn, instance, candidate, record, request, actor="user-1"
        )

    assert load_instance(conn, instance.instance_id).engine.state.state_id == before
    assert conn.execute("SELECT count(*) FROM transitions").fetchone()[0] == before_transitions
    conn.close()


def test_self_learning_candidate_cannot_bypass_authorization_boundary():
    parent = State(elements={"a": 1})
    proposed = parent.with_elements({"a": 2})
    candidate = Candidate(parent.state_id, proposed, "self-learning:handoff:123", 1)
    provenance = _provenance_for(candidate, parent, proposed)
    request = _make_execution_commit_request(provenance)

    # Deliberately make the learning-origin candidate look otherwise valid,
    # but provide no executable owner authorization.
    request = ExecutionCommitRequest(
        authorization=ExecutionAuthorization(
            request_provenance=provenance.provenance_id,
            owner_approved=False,
            evolution_identity=provenance.evolution_identity,
        ),
        intent_snapshot=request.intent_snapshot,
        request_provenance=provenance.provenance_id,
        evolution_identity=provenance.evolution_identity,
        provenance=provenance,
    )
    record = TransitionRecord(
        parent.state_id,
        proposed.state_id,
        candidate.candidate_id,
        TestResult(True),
        True,
        "ok",
    )
    with pytest.raises(PermissionError, match="execution authorization"):
        require_execution_commit(request)
    with pytest.raises(PermissionError, match="execution authorization"):
        require_execution_candidate_binding(request, candidate, record)


def test_self_learning_materialized_candidate_requires_provenance_for_its_actual_core_identity():
    parent = State(elements={"a": 1})
    proposed = parent.with_elements({"a": 2})
    candidate = Candidate(parent.state_id, proposed, "self-learning:handoff:identity", 1)
    provenance = _provenance_for(candidate, parent, proposed)
    assert provenance.candidate_id == candidate.candidate_id

    forged = type(provenance)(**{
        **provenance.__dict__,
        "candidate_id": "promotion:source-id",
    })
    auth = ExecutionAuthorization(
        request_provenance=forged.provenance_id,
        owner_approved=True,
        evolution_identity=forged.evolution_identity,
    )
    request = ExecutionCommitRequest(
        auth,
        ExecutionIntentSnapshot.from_provenance(forged),
        forged.provenance_id,
        forged.evolution_identity,
        forged,
    )
    record = TransitionRecord(
        parent.state_id,
        proposed.state_id,
        candidate.candidate_id,
        TestResult(True),
        True,
        "ok",
    )
    with pytest.raises(PermissionError, match="execution candidate"):
        require_execution_candidate_binding(request, candidate, record)


def test_verified_self_learning_runs_full_positive_path_to_durable_commit():
    from gnosis.evolution.promotion import (
        build_promotion_handoff,
        evaluate_promotion_gate,
        make_promotion_candidate,
        materialize_candidate_from_handoff,
    )
    from gnosis.instances.instance import Instance
    from gnosis.storage import connect, load_instance, save_instance

    conn = connect()
    instance = Instance.create_root("user-self-learning", State(elements={"a": 1}))
    save_instance(conn, instance)

    parent = instance.engine.state
    proposed = parent.with_elements({"a": 2})

    promotion = make_promotion_candidate(
        candidate_id="learning:verified:positive",
        evidence_digest="evidence:positive",
        evaluation_status="PASS",
        shadow_status="IMPROVED",
        invariant_status="PRESERVED",
        governance_decision="APPROVE",
    )
    gate = evaluate_promotion_gate(
        promotion,
        provenance_valid=True,
        required_evidence=("evidence:positive",),
    )
    handoff = build_promotion_handoff(
        promotion,
        gate,
        provenance_id="provenance:handoff:positive",
        proposed_state_content_id=proposed.content_id,
    )
    candidate = materialize_candidate_from_handoff(
        handoff,
        parent_state_id=parent.state_id,
        proposed_state=proposed,
        provenance_id=handoff.provenance_id,
        source_promotion_id=handoff.promotion_id,
    )

    observations = {"learning": "verified", "shadow": "improved"}
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=parent.state_id,
        parent_state_digest=parent.state_id,
        proposed_state_digest=proposed.state_id,
        observations=observations,
        proposed_state_content_id=proposed.content_id,
        candidate_binding_digest=candidate.binding_digest(parent.state_id),
        evidence_digest=canonical_digest(observations),
        evaluation_status="PASS",
        shadow_status="IMPROVED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )
    authorization = ExecutionAuthorization(
        request_provenance=provenance.provenance_id,
        owner_approved=True,
        evolution_identity=provenance.evolution_identity,
    )
    request = ExecutionCommitRequest(
        authorization,
        ExecutionIntentSnapshot.from_provenance(provenance),
        provenance.provenance_id,
        provenance.evolution_identity,
        provenance,
    )
    record = instance.engine.step(candidate)

    require_execution_commit(request)
    require_execution_candidate_binding(request, candidate, record)

    before = load_instance(conn, instance.instance_id).engine.state.state_id
    assert before == parent.state_id
    result = SQLiteExecutionCommitAdapter().commit(
        conn, instance, candidate, record, request, actor="user-self-learning"
    )

    after = load_instance(conn, instance.instance_id).engine.state.state_id
    assert after == proposed.state_id
    assert result.receipt.resulting_state_digest == proposed.state_id
    assert result.receipt.matches_request(request)
    assert candidate.origin.startswith("self-learning:")
    conn.close()
