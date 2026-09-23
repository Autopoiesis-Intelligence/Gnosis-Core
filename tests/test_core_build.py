import pytest
from gnosis.self_learning.core_build import create_build_record,build_eligible

def make(status="BUILT"):
    return create_build_record(receipt_id="sha256:receipt",core_spec_id="sha256:spec",source_revisions=("data:r1",),invariant_refs=("psi:pass",),validation_refs=("ci:pass",),build_revision="core:r1",status=status)

def test_build_record_is_provenance_bound():
    r=make()
    assert r.receipt_id=="sha256:receipt"
    assert r.core_spec_id=="sha256:spec"

def test_built_record_requires_passed_receipt():
    assert build_eligible(receipt_status="PASSED",record=make())

def test_unpassed_receipt_blocks_build_eligibility():
    assert not build_eligible(receipt_status="PARTIAL",record=make())

def test_rejected_build_is_not_eligible():
    assert not build_eligible(receipt_status="PASSED",record=make("REJECTED"))

def test_identity_is_deterministic():
    assert make()==make()
