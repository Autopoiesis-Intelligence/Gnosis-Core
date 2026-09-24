import pytest
from gnosis.self_learning.partner_replay import replay_partner_result,may_enter_learning
def make(**kw):
 base=dict(result_id="r:1",delivery_id="d:1",manifest_id="m:1",contract_id="c:1",core_digest="sha256:core",result_digest="sha256:result",expected_core_digest="sha256:core",expected_delivery_id="d:1",expected_manifest_id="m:1",expected_contract_id="c:1",evidence_refs=("e1",))
 base.update(kw); return replay_partner_result(**base)
def test_verified_replay(): assert may_enter_learning(decision=make())
def test_core_digest_mismatch_rejects(): assert not may_enter_learning(decision=make(expected_core_digest="sha256:other"))
def test_delivery_mismatch_rejects(): assert not may_enter_learning(decision=make(expected_delivery_id="d:x"))
def test_manifest_mismatch_rejects(): assert not may_enter_learning(decision=make(expected_manifest_id="m:x"))
def test_contract_mismatch_rejects(): assert not may_enter_learning(decision=make(expected_contract_id="c:x"))
def test_evidence_required():
 with pytest.raises(ValueError): make(evidence_refs=())
def test_deterministic(): assert make()==make()
