from gnosis.self_learning.e7_108_execution_record import (
    CriterionEvidence,
    ExecutionRecord,
    ExecutionState,
    complete,
)


def _record(**changes):
    values = dict(
        batch_id="B1",
        target_commit_sha="abc",
        repository_ref="main",
        environment_identity={"python": "3.12"},
        commands=("pytest -q",),
        candidate_selection_id="SEL1",
        baseline_id="BASE1",
        evidence_policy_revision="EP1",
        verification_matrix_revision="VM1",
        criteria=(),
        state=ExecutionState.RUNNING,
    )
    values.update(changes)
    return ExecutionRecord(**values)


def test_completion_requires_criterion_evidence():
    r = _record()
    try:
        complete(r, ())
        assert False
    except ValueError:
        pass


def test_every_criterion_requires_evidence_id():
    r = _record()
    c = CriterionEvidence("C1", "pass", "pass", "", True)
    try:
        complete(r, (c,))
        assert False
    except ValueError:
        pass


def test_completed_record_requires_all_criteria_pass():
    r = _record()
    c = CriterionEvidence("C1", "pass", "pass", "EV1", True)
    x = complete(r, (c,))
    assert x.state is ExecutionState.COMPLETED
    assert x.passed


def test_failed_criterion_does_not_pass_record():
    r = _record()
    c = CriterionEvidence("C1", "pass", "fail", "EV1", False)
    x = complete(r, (c,))
    assert not x.passed


def test_same_execution_context_has_same_identity():
    assert _record().execution_id == _record().execution_id


def test_identity_ignores_runtime_state_and_criteria():
    base = _record()
    completed = complete(
        base, (CriterionEvidence("C1", "pass", "pass", "EV1", True),)
    )
    assert base.execution_id == completed.execution_id


def test_identity_changes_for_execution_context_fields():
    base = _record()
    mutations = (
        {"batch_id": "B2"},
        {"target_commit_sha": "def"},
        {"repository_ref": "release"},
        {"environment_identity": {"python": "3.13"}},
        {"commands": ("pytest -q", "python -m compileall .")},
        {"candidate_selection_id": "SEL2"},
        {"baseline_id": "BASE2"},
        {"evidence_policy_revision": "EP2"},
        {"verification_matrix_revision": "VM2"},
    )
    for mutation in mutations:
        assert _record(**mutation).execution_id != base.execution_id


def test_environment_mapping_order_is_canonicalized():
    left = _record(environment_identity={"python": "3.12", "os": "linux"})
    right = _record(environment_identity={"os": "linux", "python": "3.12"})
    assert left.execution_id == right.execution_id


def test_execution_identity_detects_context_tamper():
    original = _record()
    tampered = _record(target_commit_sha="tampered")
    assert original.execution_id != tampered.execution_id
