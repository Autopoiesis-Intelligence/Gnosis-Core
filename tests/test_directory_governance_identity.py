from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate
from gnosis.evolution.directory_evaluation import evaluate_directory_shadow
from gnosis.evolution.directory_governance import GovernanceDecision, govern_directory_shadow
from gnosis.evolution.directory_provenance import build_directory_provenance
from gnosis.evolution.directory_resources import DirectoryResourceSnapshot

def test_full_governance_identity_binding():
    candidate=build_duplicate_candidate(["a","b"],"digest",{"b":DirectoryUsage("b",provenance_id="p1")})
    provenance=build_directory_provenance(candidate=candidate,parent_state_id="s0",parent_state_digest="p",proposed_state_digest="n")
    evaluation=evaluate_directory_shadow(candidate,{"b":DirectoryUsage("b",provenance_id="p1")},observed_file_count=10,before=DirectoryResourceSnapshot(10,1000,20),after=DirectoryResourceSnapshot(9,800,18))
    decision=govern_directory_shadow(evaluation,provenance=provenance,evidence_complete=True)
    assert decision.decision is GovernanceDecision.ALLOW
    assert decision.candidate_id == candidate.candidate_id
    assert decision.candidate_binding_digest == candidate.candidate_binding_digest
    assert decision.provenance_id == provenance.provenance_id
    assert decision.evidence_digest == provenance.evidence_digest
    assert decision.decision_digest

def test_governance_identity_changes_with_provenance():
    candidate=build_duplicate_candidate(["a","b"],"digest",{"b":DirectoryUsage("b",provenance_id="p1")})
    p1=build_directory_provenance(candidate=candidate,parent_state_id="s0",parent_state_digest="p",proposed_state_digest="n")
    p2=build_directory_provenance(candidate=candidate,parent_state_id="s1",parent_state_digest="q",proposed_state_digest="m")
    evaluation=evaluate_directory_shadow(candidate,{"b":DirectoryUsage("b",provenance_id="p1")},observed_file_count=10,before=DirectoryResourceSnapshot(10,1000),after=DirectoryResourceSnapshot(9,800))
    d1=govern_directory_shadow(evaluation,provenance=p1,evidence_complete=True)
    d2=govern_directory_shadow(evaluation,provenance=p2,evidence_complete=True)
    assert d1.decision_digest != d2.decision_digest
