from gnosis.self_learning.shadow_evaluation import evaluate_candidate,shadow_passes,may_enter_governance,creates_execution_authority
def make(outcome="PASS",base="sha256:base",projected="sha256:new"):
    return evaluate_candidate(candidate_id="cand:1",base_state_digest=base,projected_state_digest=projected,invariant_results=("PASS:invariant-1",),regression_results=("PASS:regression-1",),evidence_refs=("shadow:e1",),outcome=outcome)
def test_pass_requires_all_evidence(): assert shadow_passes(evaluation=make())
def test_same_state_is_not_evolution(): assert not shadow_passes(evaluation=make(projected="sha256:base"))
def test_fail_cannot_enter_governance(): assert not may_enter_governance(evaluation=make("FAIL"))
def test_blocked_cannot_enter_governance(): assert not may_enter_governance(evaluation=make("BLOCKED"))
def test_shadow_never_grants_authority(): assert not creates_execution_authority(evaluation=make())
def test_deterministic(): assert make()==make()
