import pytest
from gnosis.core.check_identity import check_identity, verify_check_identity, verify_check_execution

def test_check_identity_round_trip():
    i=check_identity("A","check:A",{"predicate":"x>0"})
    assert verify_check_identity(i,{"predicate":"x>0"})

def test_check_definition_tamper_detected():
    i=check_identity("A","check:A",{"predicate":"x>0"})
    assert not verify_check_identity(i,{"predicate":"x>=0"})

def test_obligation_substitution_detected():
    i=check_identity("A","check:A",{"predicate":"x>0"})
    j=check_identity("B","check:A",{"predicate":"x>0"})
    assert i != j

def test_execution_must_match_check_identity():
    i=check_identity("A","check:A",{"predicate":"x>0"})
    verify_check_execution(i,"check:A",True)
    with pytest.raises(ValueError,match="identity"):
        verify_check_execution(i,"check:B",True)

def test_failed_execution_cannot_be_accepted():
    i=check_identity("A","check:A",{"predicate":"x>0"})
    with pytest.raises(ValueError,match="failed"):
        verify_check_execution(i,"check:A",False)
