import pytest
from gnosis.core.verification_coverage import VerificationCoverage, coverage_digest, verify_adequacy

def test_complete_coverage_is_adequate():
    c=VerificationCoverage("rule-d",("A","B"),("A","B"))
    verify_adequacy(c,coverage_digest(c))

def test_pass_does_not_hide_missing_obligation():
    c=VerificationCoverage("rule-d",("A","B"),("A",))
    with pytest.raises(ValueError,match="incomplete"):
        verify_adequacy(c,coverage_digest(c))

def test_coverage_tamper_is_detected():
    c=VerificationCoverage("rule-d",("A","B"),("A","B"))
    tampered=VerificationCoverage("rule-d",("A","B"),("A",))
    with pytest.raises(ValueError,match="digest"):
        verify_adequacy(tampered,coverage_digest(c))
