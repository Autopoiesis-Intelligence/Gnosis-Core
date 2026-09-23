from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate
from gnosis.evolution.directory_commit import verify_directory_commit_eligibility
from gnosis.evolution.directory_evaluation import evaluate_directory_shadow
from gnosis.evolution.directory_governance import govern_directory_shadow, GovernanceDecision
from gnosis.evolution.directory_provenance import build_directory_provenance
from gnosis.evolution.directory_resources import DirectoryResourceSnapshot

def setup(required=()):
    c=build_duplicate_candidate(["a","b"],"digest",{"b":DirectoryUsage("b",provenance_id="p1")})
    u={"b":DirectoryUsage("b",provenance_id="p1")}
    p=build_directory_provenance(candidate=c,parent_state_id="s0",parent_state_digest="p",proposed_state_digest="n")
    e=evaluate_directory_shadow(c,u,observed_file_count=10,before=DirectoryResourceSnapshot(10,1000,20),after=DirectoryResourceSnapshot(9,800,18),required_paths=required)
    d=govern_directory_shadow(e,provenance=p,evidence_complete=True)
    return c,u,p,e,d

def test_valid_allow_is_commit_eligible():
    c,u,p,e,d=setup()
    r=verify_directory_commit_eligibility(c,u,p,e,d)
    assert r.eligible

def test_reject_is_never_commit_eligible():
    c,u,p,e,d=setup(required=("b",))
    r=verify_directory_commit_eligibility(c,u,p,e,d)
    assert d.decision is GovernanceDecision.REJECT
    assert not r.eligible
