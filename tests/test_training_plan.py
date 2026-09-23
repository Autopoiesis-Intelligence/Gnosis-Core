import pytest
from gnosis.self_learning.training_plan import create_training_plan,validate_plan_scope

def make():
    return create_training_plan(intake_id="sha256:intake",allowed_data_refs=("source:1",),learning_objectives=("learn-patterns",),invariant_refs=("psi-core",),test_requirements=("counterexample",),acceptance_criteria=("ci-pass",),revision="r1")

def test_plan_is_proposed_and_complete():
    p=make(); assert p.status=="PROPOSED"; assert p.invariant_refs==("psi-core",)

def test_data_scope_is_enforced():
    assert validate_plan_scope(make(),allowed_data_refs={"source:1"}).intake_id=="sha256:intake"

def test_data_scope_escalation_is_blocked():
    with pytest.raises(PermissionError): validate_plan_scope(make(),allowed_data_refs={"source:2"})

def test_plan_identity_is_deterministic():
    assert make()==make()


def test_tampered_training_plan_identity_is_rejected():
    from dataclasses import replace
    tampered=replace(make(), plan_id="sha256:forged")
    with pytest.raises(ValueError, match="training plan identity"):
        validate_plan_scope(tampered,allowed_data_refs={"source:1"})
