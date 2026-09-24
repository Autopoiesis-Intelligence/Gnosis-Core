import pytest
from gnosis.self_learning.learning_input import create_learning_input,may_enter_learning,may_cross_scope,preserves_isolation
def make(conf="GENERAL",scope="general",status="ADMITTED"):
    return create_learning_input(cycle_id="cycle:1",source_ref="source:1",evidence_refs=("e1",),scope=scope,confidentiality=conf,status=status)
def test_admitted_input_can_enter_learning(): assert may_enter_learning(item=make())
def test_unadmitted_input_cannot_enter_learning(): assert not may_enter_learning(item=make(status="PROPOSED"))
def test_partner_private_isolated_from_other_scope(): assert not may_cross_scope(item=make("PARTNER_PRIVATE","partner:a"),target_scope="partner:b")
def test_partner_private_can_stay_in_own_scope(): assert preserves_isolation(item=make("PARTNER_PRIVATE","partner:a"),target_scope="partner:a")
def test_general_can_cross_matching_scope_only(): assert may_cross_scope(item=make("GENERAL","general"),target_scope="general")
def test_deterministic(): assert make()==make()
