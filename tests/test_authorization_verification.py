from gnosis.evolution.commit_authorization import DirectoryCommitAuthorization
from gnosis.evolution.authorization_verification import verify_authorization_freshness

def auth():
 return DirectoryCommitAuthorization.issue(candidate_id="c1",candidate_binding_digest="cb1",provenance_id="p1",evidence_digest="e1",decision_digest="d1",governance_decision="ALLOW",shadow_accepted=True)

def test_fresh_authorization_is_valid():
 a=auth()
 r=verify_authorization_freshness(a,current_candidate_id="c1",current_candidate_binding_digest="cb1",current_provenance_id="p1",current_evidence_digest="e1",current_decision_digest="d1")
 assert r.valid

def test_stale_candidate_is_rejected():
 a=auth()
 r=verify_authorization_freshness(a,current_candidate_id="c2",current_candidate_binding_digest="cb1",current_provenance_id="p1",current_evidence_digest="e1",current_decision_digest="d1")
 assert not r.valid and "stale candidate identity" in r.reasons

def test_tampered_authorization_is_rejected():
 a=auth()
 object.__setattr__(a,"evidence_digest","e2")
 r=verify_authorization_freshness(a,current_candidate_id="c1",current_candidate_binding_digest="cb1",current_provenance_id="p1",current_evidence_digest="e1",current_decision_digest="d1")
 assert not r.valid
