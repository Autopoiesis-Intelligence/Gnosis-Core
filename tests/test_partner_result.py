import pytest
from gnosis.self_learning.partner_result import record_partner_result,may_enter_learning,binds_delivery
def make(status="VERIFIED",kind="SUCCESS_SIGNAL"): return record_partner_result(delivery_id="d:1",contract_id="c:1",partner_scope="partner:a",result_digest="sha256:r",evidence_refs=("e1",),outcome_class=kind,status=status)
def test_verified_received_result_can_enter_learning(): assert may_enter_learning(result=make(),receipt_received=True,core_verified=True)
def test_receipt_required(): assert not may_enter_learning(result=make(),receipt_received=False,core_verified=True)
def test_core_verification_required(): assert not may_enter_learning(result=make(),receipt_received=True,core_verified=False)
def test_inconclusive_does_not_enter(): assert not may_enter_learning(result=make(kind="INCONCLUSIVE"),receipt_received=True,core_verified=True)
def test_delivery_binding(): assert binds_delivery(result=make(),delivery_id="d:1",contract_id="c:1")
def test_wrong_binding(): assert not binds_delivery(result=make(),delivery_id="d:x",contract_id="c:1")
def test_evidence_required():
 with pytest.raises(ValueError): record_partner_result(delivery_id="d",contract_id="c",partner_scope="partner:a",result_digest="r",evidence_refs=(),outcome_class="SUCCESS_SIGNAL")
def test_deterministic(): assert make()==make()
