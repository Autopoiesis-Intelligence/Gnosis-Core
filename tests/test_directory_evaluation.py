from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate
from gnosis.evolution.directory_evaluation import evaluate_directory_shadow
from gnosis.evolution.directory_resources import DirectoryResourceSnapshot

def _candidate():
    return build_duplicate_candidate(["a", "b"], "digest", {"b": DirectoryUsage("b", provenance_id="p1")})

def test_unified_shadow_requires_all_evidence():
    r = evaluate_directory_shadow(_candidate(), {"b": DirectoryUsage("b", provenance_id="p1")}, observed_file_count=10, before=DirectoryResourceSnapshot(10,1000,20), after=DirectoryResourceSnapshot(9,800,18), required_paths=["a"])
    assert r.accepted and r.semantic.preserved and r.resource_delta.non_worsening

def test_unified_shadow_rejects_resource_regression():
    r = evaluate_directory_shadow(_candidate(), {"b": DirectoryUsage("b", provenance_id="p1")}, observed_file_count=10, before=DirectoryResourceSnapshot(10,1000,20), after=DirectoryResourceSnapshot(9,1200,25))
    assert not r.accepted and "resource regression" in r.reasons

def test_unified_shadow_rejects_semantic_violation():
    r = evaluate_directory_shadow(_candidate(), {"b": DirectoryUsage("b", provenance_id="p1")}, observed_file_count=10, before=DirectoryResourceSnapshot(10,1000), after=DirectoryResourceSnapshot(9,900), required_paths=["b"])
    assert not r.accepted
