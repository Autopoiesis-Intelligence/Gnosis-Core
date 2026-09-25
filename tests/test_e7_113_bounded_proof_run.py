import pytest
from gnosis.self_learning.e7_113_bounded_proof_run import ProofState, complete_proof_run, plan_proof_run

def test_plan_is_observe_only():
    r=plan_proof_run(run_id="R1",target_commit_sha="abc")
    assert r.state is ProofState.PLANNED
    assert not r.mutation_authorized
    assert len(r.stages)==6

def test_mutation_authorization_is_rejected():
    with pytest.raises(ValueError):
        plan_proof_run(run_id="R1",target_commit_sha="abc",mutation_authorized=True)

def test_empty_observation_fails():
    r=plan_proof_run(run_id="R1",target_commit_sha="abc")
    x=complete_proof_run(r,(),True)
    assert x.state is ProofState.FAILED

def test_passing_observed_run_passes():
    r=plan_proof_run(run_id="R1",target_commit_sha="abc")
    x=complete_proof_run(r,("E7.107:PASS","E7.112:CLOSED"),True)
    assert x.state is ProofState.PASSED
    assert not x.mutation_authorized
