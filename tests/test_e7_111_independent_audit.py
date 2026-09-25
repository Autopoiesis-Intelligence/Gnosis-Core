from gnosis.self_learning.e7_111_independent_audit import AUDIT_CHECKS, AuditState, audit_chain

def all_checks(value=True): return {k:value for k in AUDIT_CHECKS}

def test_all_independent_checks_pass():
    r=audit_chain(batch_id="B",target_commit_sha="abc",record_commit_sha="abc",checks=all_checks())
    assert r.state is AuditState.PASSED
    assert len(r.findings)==7

def test_wrong_commit_rejects():
    r=audit_chain(batch_id="B",target_commit_sha="abc",record_commit_sha="def",checks=all_checks())
    assert r.state is AuditState.REJECTED

def test_missing_evidence_check_rejects():
    c=all_checks(); c["evidence_completeness"]=False
    r=audit_chain(batch_id="B",target_commit_sha="abc",record_commit_sha="abc",checks=c)
    assert r.state is AuditState.REJECTED
