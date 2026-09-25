from gnosis.self_learning.e7_112_immutable_closure import ClosureState, create_closure, verify_closure

def test_empty_chain_is_blocked():
    c=create_closure(batch_id="B",target_commit_sha="abc",chain_digests=())
    assert c.state is ClosureState.BLOCKED

def test_closure_is_created_and_verifiable():
    d=("D107","D108","D109","D110","D111")
    c=create_closure(batch_id="B",target_commit_sha="abc",chain_digests=d)
    assert c.state is ClosureState.CLOSED
    assert verify_closure(c,d)

def test_modified_chain_fails_verification():
    d=("D107","D108","D109","D110","D111")
    c=create_closure(batch_id="B",target_commit_sha="abc",chain_digests=d)
    assert not verify_closure(c,("D107","D108","D109","D110","TAMPER"))

def test_empty_or_nonclosed_cannot_verify():
    c=create_closure(batch_id="B",target_commit_sha="abc",chain_digests=())
    assert not verify_closure(c,())
