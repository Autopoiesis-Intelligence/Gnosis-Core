from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate
from gnosis.evolution.directory_evaluation import evaluate_directory_shadow
from gnosis.evolution.directory_governance import GovernanceDecision, govern_directory_shadow
from gnosis.evolution.directory_resources import DirectoryResourceSnapshot

def ev(required=()):
 c=build_duplicate_candidate(["a","b"],"digest",{"b":DirectoryUsage("b",provenance_id="p1")})
 return evaluate_directory_shadow(c,{"b":DirectoryUsage("b",provenance_id="p1")},observed_file_count=10,before=DirectoryResourceSnapshot(10,1000,20),after=DirectoryResourceSnapshot(9,800,18),required_paths=required)

def test_decision_is_evidence_bound():
 d=govern_directory_shadow(ev(),evidence_complete=True)
 assert d.decision is GovernanceDecision.ALLOW
 assert d.decision_digest

def test_reject_and_defer_have_distinct_bound_decisions():
 a=govern_directory_shadow(ev(required=("b",)),evidence_complete=True)
 b=govern_directory_shadow(ev(),evidence_complete=False)
 assert a.decision is GovernanceDecision.REJECT
 assert b.decision is GovernanceDecision.DEFER
 assert a.decision_digest != b.decision_digest
