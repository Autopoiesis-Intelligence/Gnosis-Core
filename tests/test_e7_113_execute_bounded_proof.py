from types import SimpleNamespace

import pytest

import gnosis.self_learning.e7_113_execute_bounded_proof as executor


def scope():
    return SimpleNamespace(
        batch_id="B",
        target_commit_sha="a" * 40,
        repository="repo",
        criterion_ids=("C1",),
        expected_outcomes=("command exits successfully",),
        commands=("echo proof",),
        evidence_policy_revision="E1",
        verification_matrix_revision="V1",
    )


def selection():
    return SimpleNamespace(
        selection_record_id="SEL-1",
        baseline_id="BASE-1",
    )


def test_run_bounded_proof_derives_chain_from_observation(monkeypatch):
    monkeypatch.setattr(executor, "run_preflight", lambda **kwargs: SimpleNamespace(status="PASS"))
    monkeypatch.setattr(executor, "assert_preflight_ready", lambda report: None)
    monkeypatch.setattr(executor, "execute_locked_command", lambda **kwargs: (0, "observed", "", SimpleNamespace(status="PASS", actual_head_sha="a"*40), SimpleNamespace(status="PASS", actual_head_sha="a"*40), SimpleNamespace(argv0="echo", resolved_path="/bin/echo", digest="d"*64), (SimpleNamespace(path="gnosis/self_learning/e7_113_execute_bounded_proof.py", digest="d"*64),), SimpleNamespace(status="PASS", executed_paths=("gnosis/self_learning/e7_113_execute_bounded_proof.py",))))

    result = executor.run_bounded_proof(
        run_id="RUN-1",
        scope_lock=scope(),
        selection_record=selection(),
        repository_root=".",
        resolved_commit_sha="a" * 40,
        resolved_branch_ref="main",
    )

    assert result.execution_record.criteria[0].observed
    assert result.execution_record.criteria[0].passed
    assert result.acceptance_result.state.value == "ACCEPTED"
    assert result.reconciliation_snapshot.state.value == "RECONCILED"
    assert result.audit_result.state.value == "PASSED"
    assert result.closure.state.value == "CLOSED"
    assert result.proof_run.state.value == "PASSED"


def test_failed_command_cannot_become_pass(monkeypatch):
    monkeypatch.setattr(executor, "run_preflight", lambda **kwargs: SimpleNamespace(status="PASS"))
    monkeypatch.setattr(executor, "assert_preflight_ready", lambda report: None)
    monkeypatch.setattr(executor, "execute_locked_command", lambda **kwargs: (1, "", "failure", SimpleNamespace(status="PASS", actual_head_sha="a"*40), SimpleNamespace(status="PASS", actual_head_sha="a"*40), SimpleNamespace(argv0="echo", resolved_path="/bin/echo", digest="d"*64), (SimpleNamespace(path="gnosis/self_learning/e7_113_execute_bounded_proof.py", digest="d"*64),), SimpleNamespace(status="PASS", executed_paths=("gnosis/self_learning/e7_113_execute_bounded_proof.py",))))

    with pytest.raises(RuntimeError, match="independent audit"):
        executor.run_bounded_proof(
            run_id="RUN-2",
            scope_lock=scope(),
            selection_record=selection(),
            repository_root=".",
            resolved_commit_sha="a" * 40,
            resolved_branch_ref="main",
        )


def test_multiple_criteria_fail_closed(monkeypatch):
    monkeypatch.setattr(executor, "run_preflight", lambda **kwargs: SimpleNamespace(status="PASS"))
    monkeypatch.setattr(executor, "assert_preflight_ready", lambda report: None)
    monkeypatch.setattr(executor, "execute_locked_command", lambda **kwargs: (0, "observed", ""))

    locked = scope()
    locked.criterion_ids = ("C1", "C2")

    with pytest.raises(ValueError, match="exactly one criterion"):
        executor.run_bounded_proof(
            run_id="RUN-3",
            scope_lock=locked,
            selection_record=selection(),
            repository_root=".",
            resolved_commit_sha="a" * 40,
            resolved_branch_ref="main",
        )


def test_scope_lock_revalidated_before_subprocess(monkeypatch):
    locked = scope()
    monkeypatch.setattr(executor, "run_preflight", lambda **kwargs: SimpleNamespace(status="PASS"))
    monkeypatch.setattr(executor, "assert_preflight_ready", lambda report: None)
    monkeypatch.setattr(
        executor,
        "attest_checkout",
        lambda *args, **kwargs: SimpleNamespace(status="PASS", actual_head_sha="a" * 40),
    )
    monkeypatch.setattr(executor, "verify_scope_lock", lambda lock: False)
    called = {"run": False}

    def fake_run(*args, **kwargs):
        called["run"] = True
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(executor.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError, match="scope lock changed after preflight"):
        executor.execute_locked_command(
            scope_lock=locked,
            selection_record=selection(),
            repository_root=".",
            resolved_commit_sha="a" * 40,
            resolved_branch_ref="main",
        )
    assert not called["run"]


def test_executable_identity_is_attested(monkeypatch):
    path = "/tmp/fake-python"
    monkeypatch.setattr(executor.shutil, "which", lambda argv0, path=None: path)
    monkeypatch.setattr(executor.Path, "is_file", lambda self: True)
    monkeypatch.setattr(executor.Path, "read_bytes", lambda self: b"binary")
    attestation = executor.attest_executable("python", repository_root=executor.Path("."))
    assert attestation.resolved_path == executor.Path(path).resolve().as_posix()
    assert len(attestation.digest) == 64


def test_executable_mutation_fails_closed(monkeypatch):
    monkeypatch.setattr(executor.Path, "is_file", lambda self: True)
    monkeypatch.setattr(executor.Path, "read_bytes", lambda self: b"changed")
    attestation = executor.ExecutableAttestation("python", "/tmp/python", "0" * 64)
    with pytest.raises(RuntimeError, match="changed after attestation"):
        executor.assert_executable_unchanged(attestation)


def test_expected_outcome_is_immutable_and_semantic():
    assert executor.evaluate_expected_outcome("pytest exits successfully", returncode=0, stdout="", stderr="")
    assert not executor.evaluate_expected_outcome("pytest exits successfully", returncode=1, stdout="", stderr="")


def test_unknown_expected_outcome_fails_closed():
    with pytest.raises(ValueError, match="unsupported immutable expected outcome"):
        executor.evaluate_expected_outcome("anything else", returncode=0, stdout="", stderr="")
