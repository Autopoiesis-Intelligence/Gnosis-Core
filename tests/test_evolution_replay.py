from gnosis.core import Candidate, State
from gnosis.evolution.replay import replay_complete, replay_evidence, replay_identity
from gnosis.evolution.sandbox import run_sandbox


def _candidate(state):
    return Candidate(
        parent_state_id=state.state_id,
        proposed_state=state.with_elements({"b": 2}),
        origin="replay-test",
    )


def _observer(_state, _candidate):
    return {"metric": 3, "status": "stable"}


def test_replay_reproduces_completed_evidence():
    state = State(elements={"a": 1})
    result = run_sandbox(state, _candidate(state), _observer)
    replay = replay_evidence(result.execution, result.execution.observations)
    assert replay.reproducible
    assert replay.expected_digest == replay.actual_digest


def test_replay_rejects_changed_observations():
    state = State(elements={"a": 1})
    result = run_sandbox(state, _candidate(state), _observer)
    replay = replay_evidence(
        result.execution,
        {"metric": 999, "status": "stable"},
    )
    assert not replay.reproducible
    assert "evidence digest mismatch" in replay.reasons


def test_replay_identity_rejects_wrong_candidate_or_parent():
    state = State(elements={"a": 1})
    result = run_sandbox(state, _candidate(state), _observer)
    assert not replay_identity(
        result.execution,
        candidate_id="tampered",
        parent_state_id=state.state_id,
        parent_state_digest=result.execution.parent_state_digest,
        proposed_state_digest=result.execution.proposed_state_digest,
    ).reproducible
    assert not replay_identity(
        result.execution,
        candidate_id=result.execution.candidate_id,
        parent_state_id="stale",
        parent_state_digest=result.execution.parent_state_digest,
        proposed_state_digest=result.execution.proposed_state_digest,
    ).reproducible


def test_complete_replay_fails_closed_when_provenance_or_audit_is_missing():
    state = State(elements={"a": 1})
    result = run_sandbox(state, _candidate(state), _observer)
    missing_provenance = replay_complete(
        result.execution, None, None, observations=result.execution.observations
    )
    assert not missing_provenance.reproducible
    assert "provenance missing" in missing_provenance.reasons

    missing_audit = replay_complete(
        result.execution, None, None, observations=result.execution.observations
    )
    assert not missing_audit.reproducible
    assert "audit record missing" in missing_audit.reasons


def test_complete_replay_rejects_audit_identity_mismatch():
    state = State(elements={"a": 1})
    result = run_sandbox(state, _candidate(state), _observer)

    class Audit:
        candidate_id = "wrong"
        execution_id = result.execution.candidate_id

    replay = replay_complete(
        result.execution, None, Audit(), observations=result.execution.observations
    )
    assert not replay.reproducible
    assert "provenance missing" in replay.reasons
    assert "audit candidate mismatch" in replay.reasons


def test_complete_replay_rejects_audit_provenance_and_digest_mismatch():
    state = State(elements={"a": 1})
    result = run_sandbox(state, _candidate(state), _observer)

    class Audit:
        candidate_id = result.execution.candidate_id
        execution_id = result.execution.candidate_id
        provenance_id = "wrong-provenance"
        parent_state_digest = "wrong-parent"
        proposed_state_digest = result.execution.proposed_state_digest
        evidence_digest = "wrong-evidence"

    replay = replay_complete(
        result.execution, None, Audit(), observations=result.execution.observations
    )
    assert not replay.reproducible
    assert "audit provenance mismatch" in replay.reasons
    assert "audit parent_state_digest mismatch" in replay.reasons
    assert "audit evidence_digest mismatch" in replay.reasons



def test_provenance_audit_crosscheck_detects_persisted_link_tampering():
    from gnosis.evolution.audit import crosscheck_provenance_audit
    from gnosis.evolution.provenance import EvidenceProvenance
    p = EvidenceProvenance(
        execution_id="e", candidate_id="c", parent_state_id="s",
        parent_state_digest="pd", proposed_state_digest="sd", evidence_digest="ed",
        evaluation_status="PASS", shadow_status="NO_BEHAVIORAL_CHANGE",
        invariant_status="PRESERVED", governance_decision="REVIEW",
    )
    from gnosis.evolution.audit import make_audit_record
    a = make_audit_record(
        sequence=0, event_type="E", candidate_id="c", execution_id="e",
        provenance_id=p.provenance_id, parent_state_digest="pd",
        proposed_state_digest="sd", evidence_digest="ed", payload={"x": 1},
    )
    assert crosscheck_provenance_audit(p, a).valid
    broken = a.__class__(**{**a.__dict__, "evidence_digest": "tampered"})
    assert not crosscheck_provenance_audit(p, broken).valid


def test_recovery_rejects_revoked_or_missing_authorization():
    from gnosis.evolution.recovery import recover_evolution_audit

    report = recover_evolution_audit(
        __import__("sqlite3").connect(":memory:"),
        provenance_id="missing",
        observations={},
        proposed_state=State(elements={}),
        authorization_valid=False,
    )
    assert not report.replay_valid
    assert "recovery authorization is not valid" in report.reasons

    report = recover_evolution_audit(
        __import__("sqlite3").connect(":memory:"),
        provenance_id="missing",
        observations={},
        proposed_state=State(elements={}),
        authorization_valid=True,
        authorization_revoked=True,
    )
    assert not report.replay_valid
    assert "recovery authorization was revoked" in report.reasons


def test_complete_replay_uses_independent_candidate_evaluation_and_governance():
    from gnosis.evolution.audit import make_audit_record
    from gnosis.evolution.evaluator import evaluate_observation
    from gnosis.evolution.provenance import build_provenance
    from gnosis.reflection.governance import GovernanceDecision

    state = State(elements={"a": 1})
    candidate = _candidate(state)
    sandbox = run_sandbox(state, candidate, _observer)
    evaluation = evaluate_observation(
        sandbox.execution.observations,
        evidence_digest=sandbox.execution.evidence_digest,
        predicate="observations_present",
    )
    governance = GovernanceDecision(
        "REVIEW", "BEHAVIOR_CHANGED", "PRESERVED", ("review required",)
    )
    provenance = build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=candidate.parent_state_id,
        parent_state_digest=sandbox.execution.parent_state_digest,
        proposed_state_digest=sandbox.execution.proposed_state_digest,
        proposed_state_content_id=candidate.proposed_state.content_id,
        candidate_binding_digest=candidate.binding_digest(sandbox.execution.parent_state_digest),
        observations=sandbox.execution.observations,
        evidence_digest=sandbox.execution.evidence_digest,
        evaluation_status=evaluation.status,
        shadow_status=governance.shadow_status,
        invariant_status=governance.invariant_status,
        governance_decision=governance.decision,
        evaluator_identity_ref=evaluation.evaluator_identity.implementation_ref,
        evaluator_identity_version=evaluation.evaluator_identity.implementation_version,
    )
    audit = make_audit_record(
        sequence=0,
        event_type="PROVENANCE",
        candidate_id=provenance.candidate_id,
        execution_id=provenance.execution_id,
        provenance_id=provenance.provenance_id,
        parent_state_digest=provenance.parent_state_digest,
        proposed_state_digest=provenance.proposed_state_digest,
        evidence_digest=provenance.evidence_digest,
        payload={"status": "RECORDED"},
    )

    replay = replay_complete(
        sandbox.execution,
        provenance,
        audit,
        observations=sandbox.execution.observations,
        candidate=candidate,
        evaluation=evaluation,
        governance=governance,
    )
    assert replay.reproducible, replay.reasons

    changed_evaluation = evaluate_observation(
        sandbox.execution.observations,
        evidence_digest=sandbox.execution.evidence_digest,
        predicate="unsupported-predicate",
    )
    rejected = replay_complete(
        sandbox.execution,
        provenance,
        audit,
        observations=sandbox.execution.observations,
        candidate=candidate,
        evaluation=changed_evaluation,
        governance=governance,
    )
    assert not rejected.reproducible
    assert "evaluation_status mismatch" in rejected.reasons
