from gnosis.evolution.commit_authorization import DirectoryCommitAuthorization

def test_authorization_is_self_verifying():
    a=DirectoryCommitAuthorization.issue(
        candidate_id="c1",candidate_binding_digest="cb1",provenance_id="p1",
        evidence_digest="e1",decision_digest="d1",governance_decision="ALLOW",
        shadow_accepted=True)
    assert a.verify()
    assert a.authorization_digest

def test_tampering_invalidates_authorization():
    a=DirectoryCommitAuthorization.issue(
        candidate_id="c1",candidate_binding_digest="cb1",provenance_id="p1",
        evidence_digest="e1",decision_digest="d1",governance_decision="ALLOW",
        shadow_accepted=True)
    object.__setattr__(a,"candidate_id","c2")
    assert not a.verify()

def test_reject_cannot_be_presented_as_valid_allow():
    a=DirectoryCommitAuthorization.issue(
        candidate_id="c1",candidate_binding_digest="cb1",provenance_id="p1",
        evidence_digest="e1",decision_digest="d1",governance_decision="REJECT",
        shadow_accepted=False)
    assert a.verify()
    assert a.governance_decision == "REJECT"
    assert not a.shadow_accepted
