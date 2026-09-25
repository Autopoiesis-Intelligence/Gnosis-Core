from gnosis.self_learning.e7_108_execution_record import (
    CriterionEvidence, ExecutionRecord, ExecutionState, complete
)

def _record():
    return ExecutionRecord(
        batch_id="B1", target_commit_sha="abc", repository_ref="main",
        environment_identity={"python":"3.12"},
        commands=("pytest -q",), candidate_selection_id="SEL1",
        baseline_id="BASE1", evidence_policy_revision="EP1",
        verification_matrix_revision="VM1", criteria=(),
        state=ExecutionState.RUNNING,
    )

def test_completion_requires_criterion_evidence():
    r=_record()
    try:
        complete(r, ())
        assert False
    except ValueError:
        pass

def test_every_criterion_requires_evidence_id():
    r=_record()
    c=CriterionEvidence("C1","pass","pass","",True)
    try:
        complete(r,(c,))
        assert False
    except ValueError:
        pass

def test_completed_record_requires_all_criteria_pass():
    r=_record()
    c=CriterionEvidence("C1","pass","pass","EV1",True)
    x=complete(r,(c,))
    assert x.state is ExecutionState.COMPLETED
    assert x.passed

def test_failed_criterion_does_not_pass_record():
    r=_record()
    c=CriterionEvidence("C1","pass","fail","EV1",False)
    x=complete(r,(c,))
    assert not x.passed
