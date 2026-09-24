import pytest
from gnosis.self_learning.opportunity_reclassification import propose_reclassification,evidence_sufficient,level_changed,may_apply,creates_execution_authority
def make(prev="LOW_RELEVANCE",new="RESEARCH_RELEVANT",status="ACCEPTED",refs=("e1",)):
    return propose_reclassification(opportunity_id="opp:1",previous_level=prev,proposed_level=new,evidence_refs=refs,reason="new evidence",status=status)
def test_evidence_required(): assert evidence_sufficient(event=make())
def test_level_change_is_explicit(): assert level_changed(event=make())
def test_accepted_change_can_apply(): assert may_apply(event=make())
def test_same_level_is_not_change(): assert not may_apply(event=make("LOW_RELEVANCE","LOW_RELEVANCE"))
def test_proposed_does_not_apply(): assert not may_apply(event=make(status="PROPOSED"))
def test_no_evidence_is_rejected(): 
    with pytest.raises(ValueError): make(refs=())
def test_reclassification_never_grants_authority(): assert not creates_execution_authority(event=make())
def test_deterministic(): assert make()==make()
