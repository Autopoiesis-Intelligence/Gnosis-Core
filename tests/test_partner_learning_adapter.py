import pytest
from gnosis.self_learning.partner_learning_adapter import build_request,may_submit

def make(**kw):
 d=dict(candidate_id="cand:1",result_id="r:1",contract_id="c:1",provenance_digest="sha256:p",evidence_refs=("e1",),state_digest="sha256:s",admission_verified=True);d.update(kw);return build_request(**d)
def test_ready(): assert may_submit(request=make())
def test_unverified_blocks():
 with pytest.raises(ValueError): make(admission_verified=False)
def test_evidence_required():
 with pytest.raises(ValueError): make(evidence_refs=())
def test_identity_required():
 with pytest.raises(ValueError): make(candidate_id="")
def test_deterministic(): assert make()==make()
