import os

import pytest

from gnosis.self_learning.e7_106_selection import (
    CandidateRecord,
    SelectionStatus,
    create_selection_record,
    selection_digest,
)
from gnosis.self_learning.e7_114_scope_lock import (
    ScopeLockError,
    assert_selection_binding,
    assert_target_commit,
    create_scope_lock,
    invalidate_scope_lock,
    revise_scope_lock,
    verify_scope_lock,
)


TEST_FIXTURE_SHA = "0123456789abcdef0123456789abcdef01234567"


def selection():
    candidate = CandidateRecord(
        candidate_id="C1",
        contract_id="E7.114",
        revision="r1",
        current_status="IMPLEMENTED",
        dependency_status="SATISFIED",
        implementation_paths=("gnosis/self_learning/e7_114_scope_lock.py",),
        acceptance_criteria_count=3,
        mapped_test_count=3,
        runtime_proof_requirements=("exact_commit",),
        existing_evidence_ids=(),
        evidence_commits=(TEST_FIXTURE_SHA,),
        known_gaps=("runtime proof",),
        trust_boundary_relevance="HIGH",
        execution_prerequisites=("python",),
        selection_status=SelectionStatus.SELECTED,
        selection_rationale="minimal deterministic trust-boundary surface",
    )
    return create_selection_record(
        selection_record_id="SEL-E7-106-1",
        batch_id="B-E7",
        baseline_id="BASE-E7-105-1",
        repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        target_commit_sha=TEST_FIXTURE_SHA,
        candidates=(candidate,),
        selected_candidate_ids=("C1",),
        reserve_candidate_ids=(),
        excluded_candidate_ids=(),
        blocked_candidate_ids=(),
        runtime_scenarios=("bounded proof",),
        evidence_capture_points=("stdout", "artifact_digest"),
        stop_conditions=("commit_mismatch", "unauthorized"),
        selection_policy_revision="E7.106-r1",
    )


def lock(target_sha=TEST_FIXTURE_SHA):
    frozen = selection()
    return create_scope_lock(
        batch_id="B-E7",
        selection_record_id=frozen.selection_record_id,
        selection_record_digest=selection_digest(frozen),
        scope_lock_id="SL-1",
        repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        branch_ref="r2/e7-114-scope-lock",
        target_commit_sha=target_sha,
        contract_ids=("E7.106", "E7.107", "E7.114"),
        criterion_ids=("C114.1", "C114.2"),
        implementation_paths=("gnosis/self_learning/e7_114_scope_lock.py",),
        runtime_paths=("tests/test_e7_114_scope_lock.py",),
        commands=("python -m pytest tests/test_e7_114_scope_lock.py",),
        expected_outcomes=("VALID",),
        evidence_destinations=("artifacts/e7-114",),
        environment_prerequisites=("python",),
        stop_conditions=("commit_mismatch",),
        evidence_policy_revision="r1",
        verification_matrix_revision="r1",
        progress_policy_revision="r1",
    )


def test_scope_lock_is_integrity_bound():
    assert verify_scope_lock(lock())


def test_scope_lock_binds_frozen_e7106_selection():
    frozen = selection()
    assert_selection_binding(
        lock(),
        selection_record_id=frozen.selection_record_id,
        selection_record_digest=selection_digest(frozen),
    )


def test_scope_lock_rejects_selection_reinterpretation():
    current = lock()
    with pytest.raises(ScopeLockError, match="selection binding"):
        assert_selection_binding(
            current,
            selection_record_id="SEL-E7-106-OTHER",
            selection_record_digest=current.selection_record_digest,
        )
    with pytest.raises(ScopeLockError, match="selection binding"):
        assert_selection_binding(
            current,
            selection_record_id=current.selection_record_id,
            selection_record_digest="b" * 64,
        )


def test_scope_lock_binds_fixture_commit():
    assert_target_commit(lock(), TEST_FIXTURE_SHA)


def test_integration_scope_binds_exact_ci_commit():
    ci_sha = os.environ.get("GITHUB_SHA")
    if not ci_sha:
        pytest.skip("GITHUB_SHA is available only in CI execution")
    assert_target_commit(lock(ci_sha), ci_sha)


def test_wrong_commit_fails_closed():
    with pytest.raises(ScopeLockError):
        assert_target_commit(lock("fedcba9876543210fedcba9876543210fedcba98"), TEST_FIXTURE_SHA)


def test_invalidation_blocks_verification():
    invalid = invalidate_scope_lock(lock(), reason="target changed")
    assert invalid.status == "INVALIDATED"
    assert not verify_scope_lock(invalid)


def test_missing_commands_are_rejected():
    frozen = selection()
    with pytest.raises(ScopeLockError):
        create_scope_lock(
            batch_id="B-E7",
            selection_record_id=frozen.selection_record_id,
            selection_record_digest=selection_digest(frozen),
            scope_lock_id="SL-2",
            repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
            branch_ref="r2/e7-114-scope-lock",
            target_commit_sha=TEST_FIXTURE_SHA,
            contract_ids=("E7.114",),
            criterion_ids=("C114.1",),
            implementation_paths=("gnosis/self_learning/e7_114_scope_lock.py",),
            runtime_paths=("tests/test_e7_114_scope_lock.py",),
            commands=(),
            expected_outcomes=("VALID",),
            evidence_destinations=("artifacts/e7-114",),
            environment_prerequisites=("python",),
            stop_conditions=("commit_mismatch",),
            evidence_policy_revision="r1",
            verification_matrix_revision="r1",
            progress_policy_revision="r1",
        )


def test_tamper_is_detected():
    from dataclasses import replace

    tampered = replace(lock(), criterion_ids=("C114.TAMPERED",))
    assert not verify_scope_lock(tampered)


def test_tampered_scope_cannot_be_invalidated():
    from dataclasses import replace

    tampered = replace(lock(), criterion_ids=("C114.TAMPERED",))
    with pytest.raises(ScopeLockError, match="invalid or tampered"):
        invalidate_scope_lock(tampered, reason="reject tampered lifecycle")


def test_valid_scope_invalidate_revise_and_reverify():
    invalid = invalidate_scope_lock(lock(), reason="target changed")
    assert invalid.status == "INVALIDATED"
    revised = revise_scope_lock(
        invalid,
        scope_lock_id="SL-1-R2",
    )
    assert revised.status == "VALID"
    assert revised.revision == invalid.revision + 1
    assert verify_scope_lock(revised)
    frozen = selection()
    assert_selection_binding(
        revised,
        selection_record_id=frozen.selection_record_id,
        selection_record_digest=selection_digest(frozen),
    )


def test_revision_cannot_mutate_frozen_execution_scope():
    invalid = invalidate_scope_lock(lock(), reason="scope change requested")
    with pytest.raises(ScopeLockError, match="frozen execution scope"):
        revise_scope_lock(invalid, target_commit_sha="fedcba9876543210fedcba9876543210fedcba98")
    with pytest.raises(ScopeLockError, match="frozen execution scope"):
        revise_scope_lock(invalid, selection_record_id="SEL-OTHER")


@pytest.mark.parametrize("command", [
    "python -m pytest tests/test_e7_114_scope_lock.py && echo bypass",
    "python -m pytest tests/test_e7_114_scope_lock.py | cat",
    "bash -c 'python -m pytest tests/test_e7_114_scope_lock.py'",
    "python -c 'print(1)'",
])
def test_shell_semantics_are_rejected(command):
    frozen = selection()
    with pytest.raises(ScopeLockError):
        create_scope_lock(
            batch_id="B-E7",
            selection_record_id=frozen.selection_record_id,
            selection_record_digest=selection_digest(frozen),
            scope_lock_id="SL-SHELL",
            repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
            branch_ref="r2/e7-114-scope-lock",
            target_commit_sha=TEST_FIXTURE_SHA,
            contract_ids=("E7.114",),
            criterion_ids=("C114.1",),
            implementation_paths=("gnosis/self_learning/e7_114_scope_lock.py",),
            runtime_paths=("tests/test_e7_114_scope_lock.py",),
            commands=(command,),
            expected_outcomes=("VALID",),
            evidence_destinations=("artifacts/e7-114",),
            environment_prerequisites=("python",),
            stop_conditions=("commit_mismatch",),
            evidence_policy_revision="r1",
            verification_matrix_revision="r1",
            progress_policy_revision="r1",
        )


def test_valid_bounded_command_is_argv_semantics():
    frozen = selection()
    lock_value = create_scope_lock(
        batch_id="B-E7",
        selection_record_id=frozen.selection_record_id,
        selection_record_digest=selection_digest(frozen),
        scope_lock_id="SL-ARGV",
        repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        branch_ref="r2/e7-114-scope-lock",
        target_commit_sha=TEST_FIXTURE_SHA,
        contract_ids=("E7.114",),
        criterion_ids=("C114.1",),
        implementation_paths=("gnosis/self_learning/e7_114_scope_lock.py",),
        runtime_paths=("tests/test_e7_114_scope_lock.py",),
        commands=("python -m pytest tests/test_e7_114_scope_lock.py",),
        expected_outcomes=("VALID",),
        evidence_destinations=("artifacts/e7-114",),
        environment_prerequisites=("python",),
        stop_conditions=("commit_mismatch",),
        evidence_policy_revision="r1",
        verification_matrix_revision="r1",
        progress_policy_revision="r1",
    )
    assert verify_scope_lock(lock_value)
