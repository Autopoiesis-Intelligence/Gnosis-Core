from gnosis.self_learning.learning_influence_experiment import (
    run_learning_influence_experiment,
)


def test_admitted_counterexample_changes_next_cycle_input():
    result = run_learning_influence_experiment(
        feedback_id="feedback:cycle-1",
        contract_id="contract:e806",
        parent_cycle_id="cycle:1",
        parent_state_digest="sha256:state1",
        baseline_input=("candidate:baseline",),
        failure_evidence=("evidence:failure-1",),
    )
    assert result.changed_by_admitted_evidence
    assert result.evidence_input == ("evidence:failure-1",)
    assert result.baseline_input != result.evidence_input
    assert result.influence_digest.startswith("sha256:")


def test_same_evidence_is_deterministic():
    kwargs = dict(
        feedback_id="feedback:cycle-1",
        contract_id="contract:e806",
        parent_cycle_id="cycle:1",
        parent_state_digest="sha256:state1",
        baseline_input=("candidate:baseline",),
        failure_evidence=("evidence:failure-1",),
    )
    assert run_learning_influence_experiment(**kwargs) == run_learning_influence_experiment(
        **kwargs
    )
