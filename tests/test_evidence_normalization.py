from gnosis.self_learning.evidence_normalization import normalize_evidence,normalization_is_deterministic,may_enter_pattern_extraction
def make(status="ACCEPTED",facts=("relation:a","fact:b"),redactions=("private:x",)):
    return normalize_evidence(admission_id="admission:1",source_digest="sha256:src",facts=facts,schema_version="1",redactions=redactions,status=status)
def test_normalization_is_deterministic(): assert make().normalized_facts==("fact:b","relation:a") and make()==make()
def test_duplicates_are_canonicalized(): assert make(facts=("fact:b","fact:b","relation:a")).normalized_facts==("fact:b","relation:a")
def test_rejected_cannot_enter_patterns(): assert not may_enter_pattern_extraction(evidence=make("REJECTED"))
def test_accepted_can_enter_patterns(): assert may_enter_pattern_extraction(evidence=make())
def test_redactions_are_preserved(): assert make().redactions==("private:x",)
