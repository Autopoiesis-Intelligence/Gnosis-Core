import pytest
from dataclasses import replace
from gnosis.self_learning.partner_learning_gate import admit_partner_candidate,may_commit
def make(**kw):
 base=dict(classification_id="cl:1",result_id="r:1",candidate_digest="sha256:candidate",evidence_refs=("e1",),classification_verified=True,replay_verified=True,receipt_received=True,core_verified=True); base.update(kw); return admit_partner_candidate(**base)
def test_all_gates_admit(): assert may_commit(admission=make())
@pytest.mark.parametrize("field",["classification_verified","replay_verified","receipt_received","core_verified"])
def test_any_missing_gate_blocks(field):
 kw={field:False}
 with pytest.raises(ValueError): make(**kw)
def test_evidence_required():
 with pytest.raises(ValueError): make(evidence_refs=())
def test_deterministic(): assert make()==make()
def test_forged_admission_identity_fails_closed():
    admission=make()
    forged=replace(admission, admission_id="sha256:forged")
    assert not may_commit(admission=forged)
def test_tampered_admission_fields_fail_closed():
    admission=make()
    forged=replace(admission, evidence_refs=("attacker-evidence",))
    assert not may_commit(admission=forged)
