from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate
from gnosis.evolution.directory_evaluation import evaluate_directory_shadow
from gnosis.evolution.directory_governance import GovernanceDecision, govern_directory_shadow
from gnosis.evolution.directory_resources import DirectoryResourceSnapshot

def evaluation(required=()):
    c=build_duplicate_candidate(["a","b"],"digest",{"b":DirectoryUsage("b",provenance_id="p1")})
    return evaluate_directory_shadow(c,{"b":DirectoryUsage("b",provenance_id="p1")},observed_file_count=10,before=DirectoryResourceSnapshot(10,1000,20),after=DirectoryResourceSnapshot(9,800,18),required_paths=required)

def test_governance_allows_valid_shadow():
    assert govern_directory_shadow(evaluation(),evidence_complete=True).decision is GovernanceDecision.ALLOW

def test_governance_rejects_invalid_shadow():
    assert govern_directory_shadow(evaluation(required=("b",)),evidence_complete=True).decision is GovernanceDecision.REJECT

def test_governance_defers_incomplete_evidence():
    assert govern_directory_shadow(evaluation(),evidence_complete=False).decision is GovernanceDecision.DEFER
