import pytest
from gnosis.self_learning.opportunity_update import propose_opportunity_update,may_apply,creates_contract
def make(prior="RESEARCH_RELEVANT",proposed="RESEARCH_RELEVANT",status="ADMITTED"): return propose_opportunity_update(opportunity_id="opp:1",prior_level=prior,proposed_level=proposed,learning_commit_id="lc:1",evidence_refs=("e1",),rationale="verified outcome",status=status)
def test_verified_learning_can_update(): assert may_apply(update=make(),learning_commit_verified=True)
def test_unverified_learning_blocks(): assert not may_apply(update=make(),learning_commit_verified=False)
def test_commercial_promotion_requires_existing_commercial_level():
 with pytest.raises(ValueError): make("RESEARCH_RELEVANT","COMMERCIAL")
def test_commercial_can_be_maintained(): assert may_apply(update=make("COMMERCIAL","COMMERCIAL"),learning_commit_verified=True)
def test_proposed_not_applied(): assert not may_apply(update=make(status="PROPOSED"),learning_commit_verified=True)
def test_evidence_required():
 with pytest.raises(ValueError): propose_opportunity_update(opportunity_id="o",prior_level="LOW_RELEVANCE",proposed_level="LOW_RELEVANCE",learning_commit_id="l",evidence_refs=(),rationale="r")
def test_no_contract_creation(): assert not creates_contract(update=make())
def test_deterministic(): assert make()==make()
