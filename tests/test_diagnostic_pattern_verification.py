from gnosis.evolution.diagnostic_pattern_verification import verify_diagnostic_pattern
from gnosis.evolution.diagnostic_patterns import DiagnosticPattern

def p(sources=("source:a","source:b"), flags=(), blind=False):
    return DiagnosticPattern("p","c","sig",("1","2"),sources,2,flags)

def test_common_mode_is_not_gap_eligible():
    v=verify_diagnostic_pattern(p(("source:a",),("COMMON_SOURCE",)))
    assert not v.eligible_for_gap
    assert "COMMON_MODE_SOURCE" in v.adequacy_flags

def test_missing_state_variation_blocks_eligibility():
    v=verify_diagnostic_pattern(p(flags=("SAME_STATE",)))
    assert not v.eligible_for_gap
    assert "STATE_VARIATION_MISSING" in v.blind_spots

def test_diverse_sources_without_blind_spots_can_pass_adequacy_gate():
    v=verify_diagnostic_pattern(p())
    assert v.eligible_for_gap

def test_counterexample_blocks_gap_eligibility():
    v=verify_diagnostic_pattern(p(), counterexample_refs=("counter:1",))
    assert not v.eligible_for_gap
