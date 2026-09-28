from dataclasses import replace

import pytest

from gnosis.core.select import SelectionResult
from gnosis.core.types import Candidate, State, TestResult

from gnosis.self_learning.e7_106_selection import (
    CandidateRecord,
    SelectionError,
    SelectionStatus,
    create_selection_record,
    selection_digest,
    verify_selection_record,
)


SHA = "0123456789abcdef0123456789abcdef01234567"


def candidate(candidate_id="C1", status=SelectionStatus.SELECTED):
    return CandidateRecord(
        candidate_id=candidate_id,
        contract_id="E7.114",
        revision="r1",
        current_status="IMPLEMENTED",
        dependency_status="SATISFIED",
        implementation_paths=("gnosis/self_learning/e7_114_scope_lock.py",),
        acceptance_criteria_count=3,
        mapped_test_count=3,
        runtime_proof_requirements=("exact_commit",),
        existing_evidence_ids=(),
        evidence_commits=(SHA,),
        known_gaps=("selection origin",),
        trust_boundary_relevance="HIGH",
        execution_prerequisites=("python",),
        selection_status=status,
        selection_rationale="minimal deterministic trust-boundary surface",
    )


def record(candidates=None):
    candidates = tuple(candidates or (candidate(), candidate("C2", SelectionStatus.RESERVE)))
    return create_selection_record(
        selection_record_id="SEL-E7-106-1",
        batch_id="B-E7",
        baseline_id="BASE-E7-105-1",
        repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        target_commit_sha=SHA,
        candidates=candidates,
        selected_candidate_ids=("C1",),
        reserve_candidate_ids=("C2",),
        excluded_candidate_ids=(),
        blocked_candidate_ids=(),
        runtime_scenarios=("bounded proof",),
        evidence_capture_points=("stdout", "artifact_digest"),
        stop_conditions=("commit_mismatch", "unauthorized"),
        selection_policy_revision="E7.106-r1",
    )


def test_selection_is_frozen_and_digest_bound():
    current = record()
    assert current.frozen
    assert verify_selection_record(current)
    assert len(selection_digest(current)) == 64


def test_tampering_is_detected():
    current = record()
    tampered = replace(current, selected_candidate_ids=("C2",))
    assert not verify_selection_record(tampered)


def test_every_candidate_requires_one_explicit_state():
    with pytest.raises(SelectionError, match="explicit selection state"):
        record((candidate("C1"), candidate("C2", SelectionStatus.SELECTED), candidate("C3", SelectionStatus.INVALIDATED)))


def test_partition_and_candidate_status_must_match():
    with pytest.raises(SelectionError, match="status does not match"):
        create_selection_record(
            selection_record_id="SEL-E7-106-2",
            batch_id="B-E7",
            baseline_id="BASE",
            repository="repo",
            target_commit_sha=SHA,
            candidates=(candidate("C1", SelectionStatus.RESERVE),),
            selected_candidate_ids=("C1",),
            reserve_candidate_ids=(),
            excluded_candidate_ids=(),
            blocked_candidate_ids=(),
            runtime_scenarios=("bounded proof",),
            evidence_capture_points=("stdout",),
            stop_conditions=("failure",),
            selection_policy_revision="E7.106-r1",
        )


def test_unknown_candidate_cannot_be_selected():
    with pytest.raises(SelectionError, match="unknown candidate"):
        create_selection_record(
            selection_record_id="SEL-E7-106-3",
            batch_id="B-E7",
            baseline_id="BASE",
            repository="repo",
            target_commit_sha=SHA,
            candidates=(candidate("C1"),),
            selected_candidate_ids=("C1", "UNKNOWN"),
            reserve_candidate_ids=(),
            excluded_candidate_ids=(),
            blocked_candidate_ids=(),
            runtime_scenarios=("bounded proof",),
            evidence_capture_points=("stdout",),
            stop_conditions=("failure",),
            selection_policy_revision="E7.106-r1",
        )


def test_core_selection_result_binds_to_frozen_record():
    from gnosis.self_learning.e7_106_selection import assert_selection_result_matches_record

    current = State()
    c1 = Candidate(current.state_id, current.with_elements({"x": 1}), "A")
    c2 = Candidate(current.state_id, current.with_elements({"x": 2}), "B")
    result = SelectionResult(
        selected=c1,
        evaluated=((c1, TestResult(True)), (c2, TestResult(False))),
    )
    record_candidate = candidate(c1.candidate_id, SelectionStatus.SELECTED)
    record_reserve = candidate(c2.candidate_id, SelectionStatus.RESERVE)
    frozen = record((record_candidate, record_reserve))
    assert_selection_result_matches_record(result, frozen)


def test_core_selection_result_mismatch_is_rejected():
    from gnosis.self_learning.e7_106_selection import assert_selection_result_matches_record

    current = State()
    c1 = Candidate(current.state_id, current.with_elements({"x": 1}), "A")
    c2 = Candidate(current.state_id, current.with_elements({"x": 2}), "B")
    result = SelectionResult(
        selected=c2,
        evaluated=((c1, TestResult(True)), (c2, TestResult(False))),
    )
    frozen = record((candidate(c1.candidate_id, SelectionStatus.SELECTED), candidate(c2.candidate_id, SelectionStatus.RESERVE)))
    with pytest.raises(SelectionError, match="does not match core selection result"):
        assert_selection_result_matches_record(result, frozen)


def test_selection_record_matches_committed_transition():
    from gnosis.self_learning.e7_106_selection import assert_selection_record_matches_transition
    current = State()
    c1 = Candidate(current.state_id, current.with_elements({"x": 1}), "A")
    frozen = record((candidate(c1.candidate_id, SelectionStatus.SELECTED),))
    transition = TransitionRecord(
        from_state_id=current.state_id,
        to_state_id=c1.proposed_state.state_id,
        candidate_id=c1.candidate_id,
        test_result=TestResult(True),
        accepted=True,
        reason="committed",
        test_rule_id="test-rule:default",
    )
    assert_selection_record_matches_transition(frozen, transition)


def test_selection_record_rejects_different_transition_candidate():
    from gnosis.self_learning.e7_106_selection import assert_selection_record_matches_transition
    current = State()
    c1 = Candidate(current.state_id, current.with_elements({"x": 1}), "A")
    c2 = Candidate(current.state_id, current.with_elements({"x": 2}), "B")
    frozen = record((candidate(c1.candidate_id, SelectionStatus.SELECTED),))
    transition = TransitionRecord(
        from_state_id=current.state_id,
        to_state_id=c2.proposed_state.state_id,
        candidate_id=c2.candidate_id,
        test_result=TestResult(True),
        accepted=True,
        reason="committed",
        test_rule_id="test-rule:default",
    )
    with pytest.raises(SelectionError, match="does not match"):
        assert_selection_record_matches_transition(frozen, transition)


def test_candidate_record_binds_to_exact_core_candidate():
    from gnosis.evolution.provenance import candidate_binding_digest
    from gnosis.self_learning.e7_106_selection import (
        CandidateRecord, SelectionStatus, assert_candidate_record_matches_core_candidate,
    )
    state = State()
    core = Candidate(state.state_id, state.with_elements({"x": 1}), "C1")
    record = CandidateRecord(
        candidate_id="C1", contract_id="E7.114", revision="r1",
        current_status="IMPLEMENTED", dependency_status="SATISFIED",
        implementation_paths=("x.py",), acceptance_criteria_count=1,
        mapped_test_count=1, runtime_proof_requirements=("exact_commit",),
        existing_evidence_ids=(), evidence_commits=("0"*40,),
        known_gaps=(), trust_boundary_relevance="HIGH",
        execution_prerequisites=("python",), selection_status=SelectionStatus.SELECTED,
        selection_rationale="fixture", candidate_binding_digest=candidate_binding_digest(core),
    )
    assert_candidate_record_matches_core_candidate(core, record)


def test_candidate_record_rejects_same_id_with_changed_proposed_state():
    from gnosis.evolution.provenance import candidate_binding_digest
    from gnosis.self_learning.e7_106_selection import (
        CandidateRecord, SelectionStatus, SelectionError, assert_candidate_record_matches_core_candidate,
    )
    state = State()
    core = Candidate(state.state_id, state.with_elements({"x": 1}), "C1")
    record = CandidateRecord(
        candidate_id="C1", contract_id="E7.114", revision="r1",
        current_status="IMPLEMENTED", dependency_status="SATISFIED",
        implementation_paths=("x.py",), acceptance_criteria_count=1,
        mapped_test_count=1, runtime_proof_requirements=("exact_commit",),
        existing_evidence_ids=(), evidence_commits=("0"*40,),
        known_gaps=(), trust_boundary_relevance="HIGH",
        execution_prerequisites=("python",), selection_status=SelectionStatus.SELECTED,
        selection_rationale="fixture", candidate_binding_digest=candidate_binding_digest(core),
    )
    changed = Candidate(state.state_id, state.with_elements({"x": 2}), "C1")
    with pytest.raises(SelectionError, match="does not match"):
        assert_candidate_record_matches_core_candidate(changed, record)


def test_candidate_record_rejects_forged_binding_digest():
    from gnosis.self_learning.e7_106_selection import (
        CandidateRecord, SelectionStatus, SelectionError, assert_candidate_record_matches_core_candidate,
    )
    state = State()
    core = Candidate(state.state_id, state.with_elements({"x": 1}), "C1")
    record = CandidateRecord(
        candidate_id="C1", contract_id="E7.114", revision="r1",
        current_status="IMPLEMENTED", dependency_status="SATISFIED",
        implementation_paths=("x.py",), acceptance_criteria_count=1,
        mapped_test_count=1, runtime_proof_requirements=("exact_commit",),
        existing_evidence_ids=(), evidence_commits=("0"*40,),
        known_gaps=(), trust_boundary_relevance="HIGH",
        execution_prerequisites=("python",), selection_status=SelectionStatus.SELECTED,
        selection_rationale="fixture", candidate_binding_digest="f"*64,
    )
    with pytest.raises(SelectionError, match="does not match"):
        assert_candidate_record_matches_core_candidate(core, record)


def test_core_candidate_to_candidate_record_preserves_exact_identity():
    from gnosis.evolution.provenance import candidate_binding_digest
    from gnosis.self_learning.e7_106_selection import (
        build_candidate_record_from_core_candidate, SelectionStatus,
        assert_candidate_record_matches_core_candidate,
    )
    state = State()
    core = Candidate(state.state_id, state.with_elements({"x": 7}), "C1")
    record = build_candidate_record_from_core_candidate(
        core, contract_id="E7.114", revision="r1",
        current_status="IMPLEMENTED", dependency_status="SATISFIED",
        implementation_paths=("x.py",), acceptance_criteria_count=1,
        mapped_test_count=1, runtime_proof_requirements=("exact_commit",),
        existing_evidence_ids=(), evidence_commits=("0"*40,),
        known_gaps=(), trust_boundary_relevance="HIGH",
        execution_prerequisites=("python",), selection_status=SelectionStatus.SELECTED,
        selection_rationale="runtime fixture",
    )
    assert record.candidate_id == core.candidate_id
    assert record.candidate_binding_digest == candidate_binding_digest(core)
    assert_candidate_record_matches_core_candidate(core, record)
