import pytest
from gnosis.self_learning.learning_evidence_admission import create_admission,may_admit,creates_execution_authority
def make(status="ADMITTED",privacy="REDACTED"):
    return create_admission(source_contract_id="E7.87",verification_refs=("verification:1",),evidence_refs=("evidence:1",),evidence_digest="sha256:e",privacy_classification=privacy,learning_scope="generalized-pattern",status=status)
def test_verified_redacted_evidence_can_admit(): assert may_admit(admission=make(),source_state="VERIFIED_ATTESTED")
def test_unverified_source_cannot_admit(): assert not may_admit(admission=make(),source_state="OPEN")
def test_private_evidence_cannot_admit(): assert not may_admit(admission=make("ADMITTED","PRIVATE"),source_state="VERIFIED_CLOSED")
def test_rejected_admission_cannot_admit(): assert not may_admit(admission=make("REJECTED"),source_state="VERIFIED_CLOSED")
def test_admission_never_creates_authority(): assert not creates_execution_authority(admission=make())
def test_deterministic(): assert make()==make()
