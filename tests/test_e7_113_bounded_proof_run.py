import pytest

from gnosis.self_learning.e7_113_bounded_proof_run import (
    ProofState,
    complete_proof_run,
    plan_proof_run,
)


def test_plan_is_observe_only():
    r = plan_proof_run(run_id="R1", target_commit_sha="abc")
    assert r.state is ProofState.PLANNED
    assert not r.mutation_authorized
    assert len(r.stages) == 6


def test_mutation_authorization_is_rejected():
    with pytest.raises(ValueError):
        plan_proof_run(
            run_id="R1",
            target_commit_sha="abc",
            mutation_authorized=True,
        )


def test_empty_observation_fails():
    r = plan_proof_run(run_id="R1", target_commit_sha="abc")
    x = complete_proof_run(r, (), True)
    assert x.state is ProofState.FAILED


def test_partial_observation_fails():
    r = plan_proof_run(run_id="R1", target_commit_sha="abc")
    x = complete_proof_run(r, ("E7.107:PASS", "E7.112:CLOSED"), True)
    assert x.state is ProofState.FAILED


def test_unknown_stage_fails():
    r = plan_proof_run(run_id="R1", target_commit_sha="abc")
    observations = tuple(f"{stage}:PASS" for stage in r.stages[:-1]) + (
        "E7.999:PASS",
    )
    x = complete_proof_run(r, observations, True)
    assert x.state is ProofState.FAILED


def test_duplicate_stage_fails():
    r = plan_proof_run(run_id="R1", target_commit_sha="abc")
    observations = tuple(r.stages) + ("E7.107:PASS",)
    x = complete_proof_run(r, observations, True)
    assert x.state is ProofState.FAILED


def test_failed_observation_fails_even_if_caller_passes_true():
    r = plan_proof_run(run_id="R1", target_commit_sha="abc")
    observations = tuple(
        f"{stage}:PASS" for stage in r.stages[:-1]
    ) + ("E7.112:FAIL",)
    x = complete_proof_run(r, observations, True)
    assert x.state is ProofState.FAILED


def test_complete_observed_run_passes():
    r = plan_proof_run(run_id="R1", target_commit_sha="abc")
    observations = tuple(f"{stage}:PASS" for stage in r.stages)
    x = complete_proof_run(r, observations, True)
    assert x.state is ProofState.PASSED
    assert not x.mutation_authorized
