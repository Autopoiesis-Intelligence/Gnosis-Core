import pytest
from gnosis.self_learning.e821_integration import evaluate_e821,fail_closed_on_tamper,REQUIRED

def make(**kw):
 d=dict(completed_stages=REQUIRED,tamper_points=(),commit_verified=True); d.update(kw); return evaluate_e821(**d)
def test_clean_chain_admits(): assert make().final_admitted
def test_each_tamper_fails_closed():
 for point in ("commercial_evidence","proposal_digest","contract_binding","transfer_manifest","delivery_core_digest","receipt_status","result_binding","provenance_replay","feedback_classification","learning_admission"):
  t=make(tamper_points=(point,)); assert not t.final_admitted and fail_closed_on_tamper(trace=t)
def test_unverified_commit_blocks(): assert not make(commit_verified=False).final_admitted
def test_incomplete_chain_blocks():
 with pytest.raises(ValueError): make(completed_stages=REQUIRED[:-1])
def test_unknown_tamper_rejected():
 with pytest.raises(ValueError): make(tamper_points=("unknown",))
