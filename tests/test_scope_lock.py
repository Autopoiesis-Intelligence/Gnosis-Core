from dataclasses import FrozenInstanceError

import pytest

from gnosis.self_learning.scope_lock import (
    create_scope_lock,
    invalidate_scope_lock,
    serialize_scope_lock,
    validate_scope_lock,
)


def make_lock():
    return create_scope_lock(
        batch_id="BATCH-001",
        repository="Autopoiesis-Intelligence/Gnosis-Core",
        ref="refs/heads/main",
        target_commit_sha="abc123",
        selected_contract_ids=("E7.113",),
        selected_criterion_ids=("C1",),
        implementation_paths=("gnosis/self_learning/scope_lock.py",),
        test_runtime_paths=("tests/test_scope_lock.py",),
        commands=("pytest tests/test_scope_lock.py",),
        expected_outcomes=("scope lock validates",),
        evidence_destinations=("artifacts/e7.114/",),
        environment_prerequisites=("python>=3.11",),
        stop_conditions=("wrong commit", "missing evidence"),
        evidence_policy_revision="E7.108-r1",
        verification_matrix_revision="E7.103-r1",
        progress_calculation_policy_revision="progress-r1",
    )


def test_scope_lock_is_immutable_and_hashed():
    lock = make_lock()
    with pytest.raises(FrozenInstanceError):
        lock.target_commit_sha = "foreign"


def test_scope_lock_validates_exact_commit_paths_and_progress():
    lock = make_lock()
    validate_scope_lock(
        lock,
        actual_commit_sha="abc123",
        available_paths=(
            "gnosis/self_learning/scope_lock.py",
            "tests/test_scope_lock.py",
        ),
        progress_before={"E7.114": 0},
        progress_after={"E7.114": 0},
    )


def test_scope_lock_rejects_wrong_commit():
    lock = make_lock()
    with pytest.raises(ValueError, match="target commit"):
        validate_scope_lock(
            lock,
            actual_commit_sha="foreign",
            available_paths=(
                "gnosis/self_learning/scope_lock.py",
                "tests/test_scope_lock.py",
            ),
            progress_before=0,
            progress_after=0,
        )


def test_scope_lock_rejects_missing_path():
    lock = make_lock()
    with pytest.raises(ValueError, match="paths unavailable"):
        validate_scope_lock(
            lock,
            actual_commit_sha="abc123",
            available_paths=("gnosis/self_learning/scope_lock.py",),
            progress_before=0,
            progress_after=0,
        )


def test_scope_lock_rejects_progress_change():
    lock = make_lock()
    with pytest.raises(ValueError, match="must not change progress"):
        validate_scope_lock(
            lock,
            actual_commit_sha="abc123",
            available_paths=(
                "gnosis/self_learning/scope_lock.py",
                "tests/test_scope_lock.py",
            ),
            progress_before=0,
            progress_after=1,
        )


def test_invalidation_is_preserved_and_blocks_execution():
    lock = make_lock()
    invalidated = invalidate_scope_lock(lock, reason="environment drift")
    assert invalidated.status == "INVALIDATED"
    assert invalidated.invalidation_reason == "environment drift"
    with pytest.raises(ValueError, match="not executable"):
        validate_scope_lock(
            invalidated,
            actual_commit_sha="abc123",
            available_paths=(
                "gnosis/self_learning/scope_lock.py",
                "tests/test_scope_lock.py",
            ),
            progress_before=0,
            progress_after=0,
        )


def test_serialization_is_canonical_json():
    lock = make_lock()
    assert serialize_scope_lock(lock).startswith('{"batch_id":"BATCH-001"')
