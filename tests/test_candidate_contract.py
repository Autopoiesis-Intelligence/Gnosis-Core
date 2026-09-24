from gnosis.self_learning.candidate_contract import create_candidate_contract,candidate_is_well_formed,may_enter_shadow_evaluation,candidate_grants_execution_authority
def make(status="PROPOSED"):
    return create_candidate_contract(extraction_id="extract:1",pattern_refs=("domain:finance",),relation_refs=("domain->risk",),objective="improve evidence routing",scope="core:self_learning",evidence_refs=("e1",),status=status)
def test_candidate_is_deterministic(): assert make()==make()
def test_well_formed(): assert candidate_is_well_formed(candidate=make())
def test_proposed_enters_shadow(): assert may_enter_shadow_evaluation(candidate=make())
def test_rejected_cannot_enter_shadow(): assert not may_enter_shadow_evaluation(candidate=make("REJECTED"))
def test_candidate_never_grants_authority(): assert not candidate_grants_execution_authority(candidate=make())
