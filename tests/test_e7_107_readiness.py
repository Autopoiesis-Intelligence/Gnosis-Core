from gnosis.self_learning.e7_107_readiness import (
    CHECK_NAMES, ReadinessState, can_execute, evaluate_readiness,
    invalidate_for_commit_change,
)

def _checks(value=True):
    return {name: value for name in CHECK_NAMES}

def _record(checks=None):
    return evaluate_readiness(
        batch_id="B1", target_commit_sha="abc", repository_ref="main",
        baseline_id="BASE1", candidate_selection_id="SEL1",
        evidence_policy_revision="EP1", verification_matrix_revision="VM1",
        environment_identity={"runtime":"python"},
        checks=_checks(True) if checks is None else checks,
    )

def test_all_preflight_checks_are_required():
    r=_record()
    assert r.state is ReadinessState.READY
    assert len(r.checks)==13
    assert r.ready

def test_missing_check_blocks_ready():
    c=_checks(True); c["target_commit_available"]=False
    r=_record(c)
    assert r.state is ReadinessState.BLOCKED
    assert not r.ready

def test_only_exact_target_commit_can_execute():
    r=_record()
    assert can_execute(r,"abc")
    assert not can_execute(r,"other")

def test_target_commit_change_invalidates_readiness():
    r=_record()
    x=invalidate_for_commit_change(r,"other")
    assert x.state is ReadinessState.INVALIDATED
    assert not x.ready

def test_incomplete_checks_never_execute():
    c=_checks(True); c["evidence_destination_available"]=False
    r=_record(c)
    assert not can_execute(r,"abc")
