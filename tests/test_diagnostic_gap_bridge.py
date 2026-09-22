import pytest
from gnosis.evolution.diagnostic_gap_bridge import pattern_to_gap
from gnosis.evolution.diagnostic_pattern_verification import DiagnosticPatternVerification
from gnosis.evolution.diagnostic_patterns import DiagnosticPattern

def p(): return DiagnosticPattern("p","c","sig",("e1","e2"),("source:a","source:b"),2)

def v(ok=True): return DiagnosticPatternVerification("p",ok,2,(),())

def test_verified_pattern_becomes_hypothesis_only():
    g=pattern_to_gap(p(),v())
    assert g.trigger_kind=="diagnostic_pattern"
    assert g.source_records==("e1","e2")
    assert g.status=="HYPOTHESIS"

def test_ineligible_pattern_cannot_create_gap():
    with pytest.raises(ValueError): pattern_to_gap(p(),v(False))

def test_identity_mismatch_is_rejected():
    with pytest.raises(ValueError): pattern_to_gap(p(),DiagnosticPatternVerification("other",True,2,(),()))
