from gnosis.self_learning.pattern_extraction import extract_patterns,extraction_is_deterministic,may_generate_candidate_contract
def make(status="ACCEPTED",facts=("domain:finance","risk:constraint","domain:finance")):
    return extract_patterns(normalization_id="norm:1",input_digest="sha256:n",facts=facts,status=status)
def test_deterministic_and_deduplicated(): assert make().patterns==("domain:finance","risk:constraint") and extraction_is_deterministic(result=make()) and make()==make()
def test_relations_are_canonical(): assert make().relations==(("domain","contains","domain:finance"),("risk","contains","risk:constraint"))
def test_rejected_cannot_generate_candidate(): assert not may_generate_candidate_contract(result=make("REJECTED"))
def test_accepted_can_generate_candidate(): assert may_generate_candidate_contract(result=make())
