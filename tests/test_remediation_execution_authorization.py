from gnosis.self_learning.remediation_execution_authorization import create_authorization,may_execute,authorization_matches_plan
def make(status="AUTHORIZED"):
    return create_authorization(plan_id="plan:1",incident_id="incident:1",action="COMPENSATE",target_resource="github:repo",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION",preconditions=("privacy:pass",),evidence_refs=("evidence:1",),authorization_basis="plan:1",status=status)
def test_authorized_can_execute(): assert may_execute(authorization=make())
def test_revoked_cannot_execute(): assert not may_execute(authorization=make("REVOKED"))
def test_expired_cannot_execute(): assert not may_execute(authorization=make("EXPIRED"))
def test_blocked_cannot_execute(): assert not may_execute(authorization=make("BLOCKED"))
def test_authorization_binds_exact_target_tuple():
    a=make()
    assert authorization_matches_plan(authorization=a,plan_id="plan:1",incident_id="incident:1",action="COMPENSATE",target_resource="github:repo",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION")
    assert not authorization_matches_plan(authorization=a,plan_id="plan:1",incident_id="incident:1",action="COMPENSATE",target_resource="github:other",scope="public:proposal",privacy_classification="SHAREABLE_ABSTRACTION")
def test_identity_is_deterministic(): assert make()==make()
