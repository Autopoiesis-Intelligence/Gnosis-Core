from gnosis.self_learning.post_commit_verification import verify_commit,is_verified,must_fail_closed,may_enter_evolution_memory
def make(outcome="VERIFIED",observed="sha256:new"):
    return verify_commit(commit_id="commit:1",expected_state_digest="sha256:new",observed_state_digest=observed,evidence_refs=("verify:e1",),outcome=outcome)
def test_matching_state_is_verified(): assert is_verified(verification=make())
def test_mismatch_fails_closed(): assert must_fail_closed(verification=make(observed="sha256:other")) and not is_verified(verification=make(observed="sha256:other"))
def test_failed_does_not_enter_memory(): assert not may_enter_evolution_memory(verification=make("FAILED"))
def test_verified_can_enter_memory(): assert may_enter_evolution_memory(verification=make())
def test_deterministic(): assert make()==make()
