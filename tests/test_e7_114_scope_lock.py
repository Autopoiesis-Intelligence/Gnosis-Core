from gnosis.self_learning.e7_114_scope_lock import (
    ScopeLockError,
    assert_target_commit,
    create_scope_lock,
    invalidate_scope_lock,
    verify_scope_lock,
)


def lock():
    return create_scope_lock(
        batch_id="B-E7",
        scope_lock_id="SL-1",
        repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        branch_ref="r2/e7-114-scope-lock",
        target_commit_sha="0123456789abcdef0123456789abcdef01234567",
        contract_ids=("E7.106", "E7.107", "E7.114"),
        criterion_ids=("C114.1", "C114.2"),
        implementation_paths=("gnosis/self_learning/e7_114_scope_lock.py",),
        runtime_paths=("tests/test_e7_114_scope_lock.py",),
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


def test_scope_lock_binds_exact_commit():
    assert_target_commit(lock(), "0123456789abcdef0123456789abcdef01234567")


def test_wrong_commit_fails_closed():
    try:
        assert_target_commit(lock(), "fedcba9876543210fedcba9876543210fedcba98")
    except ScopeLockError:
        return
    raise AssertionError("wrong commit must fail closed")


def test_invalidation_blocks_verification():
    invalid = invalidate_scope_lock(lock(), reason="target changed")
    assert invalid.status == "INVALIDATED"
    assert not verify_scope_lock(invalid)


def test_tamper_is_detected():
    from dataclasses import replace

    tampered = replace(lock(), criterion_ids=("C114.TAMPERED",))
    assert not verify_scope_lock(tampered)
