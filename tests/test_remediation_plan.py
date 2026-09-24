import pytest
from gnosis.self_learning.remediation_plan import create_remediation_plan,plan_grants_execution_authority,plan_is_admissible

def make(status="ACCEPTED",kind="COMPENSATE"):
    return create_remediation_plan(incident_id="incident:1",resolution_id="resolution:1",plan_type=kind,target_resource="github:repo",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION",rationale="contained external failure",evidence_refs=("evidence:1",),preconditions=("privacy:pass",),authorization_basis="resolution:1",status=status)

def test_accepted_plan_is_admissible():
    assert plan_is_admissible(plan=make())

def test_plan_never_grants_execution_authority():
    assert not plan_grants_execution_authority(plan=make())

def test_rejected_plan_not_admissible():
    assert not plan_is_admissible(plan=make("REJECTED"))

def test_manual_review_not_mutation_plan():
    with pytest.raises(ValueError): make("ACCEPTED","MANUAL_REVIEW")

def test_identity_is_deterministic():
    assert make()==make()
