from gnosis.evolution.diagnostic_patterns import aggregate_diagnostic_patterns
from gnosis.evolution.provenance import DiagnosticEvidence

def ev(i, source="source:a", state="s1", candidate="c1"):
    return DiagnosticEvidence(i,"case",state,candidate,"VERIFIED",{"reason":"failure"},(source,))

def test_repeated_same_source_is_flagged_common_mode():
    p=aggregate_diagnostic_patterns([ev("1"),ev("2")])[0]
    assert p.repetition_count==2
    assert "COMMON_SOURCE" in p.common_mode_flags

def test_independent_sources_are_retained():
    p=aggregate_diagnostic_patterns([ev("1","source:a","s1","c1"),ev("2","source:b","s2","c2")])[0]
    assert p.independent_sources==("source:a","source:b")
    assert p.common_mode_flags==()

def test_unverified_evidence_is_not_aggregated():
    e=DiagnosticEvidence("1","case","s","c","OBSERVED",{"reason":"failure"})
    assert aggregate_diagnostic_patterns([e,e])==()
