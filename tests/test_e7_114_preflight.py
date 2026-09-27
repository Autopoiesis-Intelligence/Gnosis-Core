from pathlib import Path

import pytest

from gnosis.self_learning.e7_106_selection import (
    CandidateRecord,
    SelectionStatus,
    create_selection_record,
    selection_digest,
)
from gnosis.self_learning.e7_114_preflight import (
    PreflightError,
    assert_preflight_ready,
    run_preflight,
)
from gnosis.self_learning.e7_114_scope_lock import create_scope_lock


TARGET_SHA = "0123456789abcdef0123456789abcdef01234567"


def make_selection():
    candidate = CandidateRecord(
        candidate_id="C1", contract_id="E7.114", revision="r1",
        current_status="IMPLEMENTED", dependency_status="SATISFIED",
        implementation_paths=("src.py",), acceptance_criteria_count=1,
        mapped_test_count=1, runtime_proof_requirements=("exact_commit",),
        existing_evidence_ids=(), evidence_commits=(TARGET_SHA,),
        known_gaps=(), trust_boundary_relevance="HIGH",
        execution_prerequisites=("python",), selection_status=SelectionStatus.SELECTED,
        selection_rationale="preflight fixture",
    )
    return create_selection_record(
        selection_record_id="SEL-PREFLIGHT", batch_id="B-E7", baseline_id="BASE",
        repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis", target_commit_sha=TARGET_SHA,
        candidates=(candidate,), selected_candidate_ids=("C1",),
        reserve_candidate_ids=(), excluded_candidate_ids=(), blocked_candidate_ids=(),
        runtime_scenarios=("bounded proof",), evidence_capture_points=("stdout",),
        stop_conditions=("failure",), selection_policy_revision="r1",
    )


def make_lock():
    return create_scope_lock(
        batch_id="B-E7",
        selection_record_id=make_selection().selection_record_id,
        selection_record_digest=selection_digest(make_selection()),
        scope_lock_id="SL-PREFLIGHT",
        repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        branch_ref="r2/e7-114-scope-lock",
        target_commit_sha=TARGET_SHA,
        contract_ids=("E7.106", "E7.107", "E7.114"),
        criterion_ids=("C114.1", "C114.2"),
        implementation_paths=("src.py",),
        runtime_paths=("tests/test.py",),
        commands=("python -m pytest tests/test.py",),
        expected_outcomes=("PASS",),
        evidence_destinations=("artifacts",),
        environment_prerequisites=("python",),
        stop_conditions=("commit_mismatch", "evidence_failure"),
        evidence_policy_revision="r1",
        verification_matrix_revision="r1",
        progress_policy_revision="r1",
    )


def prepare(root: Path):
    (root / "src.py").write_text("x = 1\n")
    (root / "tests").mkdir()
    (root / "tests/test.py").write_text("def test_ok(): pass\n")
    (root / "artifacts").mkdir()


def test_preflight_all_passes_without_side_effects(tmp_path):
    prepare(tmp_path)
    lock = make_lock()
    report = run_preflight(
        lock,
        repository_root=tmp_path,
        resolved_commit_sha=TARGET_SHA,
        resolved_branch_ref="r2/e7-114-scope-lock",
        selection_record=make_selection(),
    )
    assert report.status == "PASS"
    assert_preflight_ready(report)
    assert report.integrity_digest
    assert not (tmp_path / "progress").exists()


def test_wrong_commit_fails_closed(tmp_path):
    prepare(tmp_path)
    report = run_preflight(
        make_lock(),
        repository_root=tmp_path,
        resolved_commit_sha="fedcba9876543210fedcba9876543210fedcba98",
        resolved_branch_ref="r2/e7-114-scope-lock",
    )
    assert report.status == "FAIL"
    with pytest.raises(PreflightError):
        assert_preflight_ready(report)


def test_missing_required_path_fails_closed(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "artifacts").mkdir()
    report = run_preflight(
        make_lock(),
        repository_root=tmp_path,
        resolved_commit_sha=TARGET_SHA,
        resolved_branch_ref="r2/e7-114-scope-lock",
    )
    assert report.status == "FAIL"
    assert any(c.check_id == "required_paths" and c.status == "FAIL" for c in report.checks)


def test_missing_evidence_destination_fails_closed(tmp_path):
    (tmp_path / "src.py").write_text("x = 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test.py").write_text("def test_ok(): pass\n")
    report = run_preflight(
        make_lock(),
        repository_root=tmp_path,
        resolved_commit_sha=TARGET_SHA,
        resolved_branch_ref="r2/e7-114-scope-lock",
    )
    assert report.status == "FAIL"
    assert any(c.check_id == "evidence_capture" and c.status == "FAIL" for c in report.checks)


def test_missing_command_fails_closed(tmp_path):
    prepare(tmp_path)
    lock = create_scope_lock(
        batch_id="B-E7",
        selection_record_id=make_selection().selection_record_id,
        selection_record_digest=selection_digest(make_selection()),
        scope_lock_id="SL-PREFLIGHT-MISSING",
        repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        branch_ref="r2/e7-114-scope-lock",
        target_commit_sha=TARGET_SHA,
        contract_ids=("E7.114",),
        criterion_ids=("C114.1",),
        implementation_paths=("src.py",),
        runtime_paths=("tests/test.py",),
        commands=("definitely-not-installed-e7-command",),
        expected_outcomes=("PASS",),
        evidence_destinations=("artifacts",),
        environment_prerequisites=("python",),
        stop_conditions=("command_missing",),
        evidence_policy_revision="r1",
        verification_matrix_revision="r1",
        progress_policy_revision="r1",
    )
    report = run_preflight(
        lock,
        repository_root=tmp_path,
        resolved_commit_sha=TARGET_SHA,
        resolved_branch_ref="r2/e7-114-scope-lock",
    )
    assert report.status == "FAIL"
    assert any(c.check_id == "commands" and c.status == "FAIL" for c in report.checks)


def test_selection_binding_fails_closed(tmp_path):
    prepare(tmp_path)
    lock = make_lock()
    mismatched = create_selection_record(
        selection_record_id="SEL-PREFLIGHT-TAMPER",
        batch_id="B-E7",
        baseline_id="BASE",
        repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        target_commit_sha=TARGET_SHA,
        candidates=make_selection().candidates,
        selected_candidate_ids=("C1",),
        reserve_candidate_ids=(),
        excluded_candidate_ids=(),
        blocked_candidate_ids=(),
        runtime_scenarios=("bounded proof",),
        evidence_capture_points=("stdout",),
        stop_conditions=("failure",),
        selection_policy_revision="r1",
    )
    report = run_preflight(
        lock,
        repository_root=tmp_path,
        resolved_commit_sha=TARGET_SHA,
        resolved_branch_ref="r2/e7-114-scope-lock",
        selection_record=mismatched,
    )
    assert report.status == "FAIL"
    assert any(c.check_id == "selection_binding" and c.status == "FAIL" for c in report.checks)
    with pytest.raises(PreflightError):
        assert_preflight_ready(report)
