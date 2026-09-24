import pytest

from gnosis.self_learning.collaboration_evidence import record_execution_evidence
from gnosis.storage.database import connect
from gnosis.storage.repositories import (
    StorageCorruptionError,
    load_execution_evidence,
    save_execution_evidence,
    verify_execution_evidence,
)


def evidence():
    return record_execution_evidence(
        authorization_id="auth-1", authorization_digest="sha256:auth",
        review_id="review-1", review_digest="sha256:review",
        proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR", target_resource="repo:public/project",
        authorized_scope="issue:create", executor_id="executor-1",
        execution_attempt_id="attempt-1", execution_order="order-1",
        result_status="SUCCEEDED", target_before_revision="target-r1",
        target_after_revision="target-r2", privacy_classification="PUBLIC_APPROVED",
        observed_scope="issue:create", expected_preconditions=("target-current",),
        provenance_refs=("auth-1", "review-1", "proposal-1"),
    )


def test_evidence_survives_close_and_reopen(tmp_path):
    path = tmp_path / "evidence.db"
    conn = connect(path)
    item = evidence()
    save_execution_evidence(conn, item)
    conn.close()
    conn = connect(path)
    recovered = load_execution_evidence(conn, item.evidence_id)
    assert recovered == item
    assert verify_execution_evidence(conn) == 1
    conn.close()


def test_exact_replay_is_idempotent(tmp_path):
    conn = connect(tmp_path / "evidence.db")
    item = evidence()
    assert save_execution_evidence(conn, item) == item.evidence_id
    assert save_execution_evidence(conn, item) == item.evidence_id
    assert conn.execute("SELECT COUNT(*) FROM execution_evidence").fetchone()[0] == 1
    conn.close()


def test_conflicting_replay_fails_closed(tmp_path):
    conn = connect(tmp_path / "evidence.db")
    item = evidence()
    save_execution_evidence(conn, item)
    conflict = record_execution_evidence(
        authorization_id="auth-1", authorization_digest="sha256:auth",
        review_id="review-1", review_digest="sha256:review",
        proposal_id="proposal-1", proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR", target_resource="repo:public/project",
        authorized_scope="issue:create", executor_id="executor-1",
        execution_attempt_id="attempt-1", execution_order="order-1",
        result_status="SUCCEEDED", target_before_revision="target-r1",
        target_after_revision="target-r3", privacy_classification="PUBLIC_APPROVED",
        observed_scope="issue:create", expected_preconditions=("target-current",),
        provenance_refs=("auth-1", "review-1", "proposal-1"),
    )
    with pytest.raises((StorageCorruptionError, ValueError)):
        save_execution_evidence(conn, conflict)
    conn.close()


def test_tamper_fails_recovery(tmp_path):
    path = tmp_path / "evidence.db"
    conn = connect(path)
    item = evidence()
    save_execution_evidence(conn, item)
    conn.execute("DROP TRIGGER execution_evidence_no_update")
    conn.execute("UPDATE execution_evidence SET observed_scope='issue:update' WHERE evidence_id=?", (item.evidence_id,))
    with pytest.raises((StorageCorruptionError, ValueError)):
        load_execution_evidence(conn, item.evidence_id)
    conn.close()


def test_append_only_triggers_block_delete_and_update(tmp_path):
    conn = connect(tmp_path / "evidence.db")
    item = evidence()
    save_execution_evidence(conn, item)
    with pytest.raises(Exception):
        conn.execute("UPDATE execution_evidence SET result_status='FAILED' WHERE evidence_id=?", (item.evidence_id,))
    with pytest.raises(Exception):
        conn.execute("DELETE FROM execution_evidence WHERE evidence_id=?", (item.evidence_id,))
    conn.close()


def test_same_attempt_cannot_store_conflicting_second_result(tmp_path):
    conn = connect(tmp_path / "evidence.db")
    item = evidence()
    save_execution_evidence(conn, item)
    conflict = record_execution_evidence(
        authorization_id=item.authorization_id, authorization_digest=item.authorization_digest,
        review_id=item.review_id, review_digest=item.review_digest,
        proposal_id=item.proposal_id, proposal_revision=item.proposal_revision,
        action_class=item.action_class, target_resource=item.target_resource,
        authorized_scope=item.authorized_scope, executor_id=item.executor_id,
        execution_attempt_id=item.execution_attempt_id, execution_order="order-2",
        result_status="FAILED", target_before_revision=item.target_before_revision,
        target_after_revision=item.target_after_revision, privacy_classification=item.privacy_classification,
        observed_scope=item.observed_scope, expected_preconditions=item.expected_preconditions,
        provenance_refs=item.provenance_refs,
    )
    with pytest.raises(StorageCorruptionError):
        save_execution_evidence(conn, conflict)
    assert conn.execute("SELECT COUNT(*) FROM execution_evidence WHERE execution_attempt_id=?", (item.execution_attempt_id,)).fetchone()[0] == 1
    conn.close()


def test_new_attempt_can_store_new_result(tmp_path):
    conn = connect(tmp_path / "evidence.db")
    item = evidence()
    save_execution_evidence(conn, item)
    retry = record_execution_evidence(
        authorization_id=item.authorization_id, authorization_digest=item.authorization_digest,
        review_id=item.review_id, review_digest=item.review_digest,
        proposal_id=item.proposal_id, proposal_revision=item.proposal_revision,
        action_class=item.action_class, target_resource=item.target_resource,
        authorized_scope=item.authorized_scope, executor_id=item.executor_id,
        execution_attempt_id="attempt-2", execution_order="order-1",
        result_status="SUCCEEDED", target_before_revision=item.target_after_revision,
        target_after_revision="target-r3", privacy_classification=item.privacy_classification,
        observed_scope=item.observed_scope, expected_preconditions=item.expected_preconditions,
        provenance_refs=item.provenance_refs,
    )
    save_execution_evidence(conn, retry)
    assert verify_execution_evidence(conn) == 2
    conn.close()


def test_conflicting_attempt_observation_becomes_self_learning_counterexample():
    from gnosis.self_learning.collaboration_evidence import extract_evidence_counterexample
    item = evidence()
    counterexample = extract_evidence_counterexample(item, "attempt-1", "FAILED")
    assert counterexample.invariant == "ONE_IMMUTABLE_EVIDENCE_PER_EXECUTION_ATTEMPT"
    assert counterexample.learning_scope == "SELF_LEARNING_ONLY"
    assert counterexample.prior_evidence_id == item.evidence_id
    assert counterexample.observed_conflicting_status == "FAILED"


def test_different_attempt_is_not_counterexample():
    from gnosis.self_learning.collaboration_evidence import extract_evidence_counterexample
    with pytest.raises(ValueError):
        extract_evidence_counterexample(evidence(), "attempt-2", "FAILED")


def test_counterexample_generates_shadow_only_rule_proposal():
    from gnosis.self_learning.collaboration_evidence import extract_evidence_counterexample
    from gnosis.self_learning.rule_proposals import propose_rule
    item = evidence()
    ce = extract_evidence_counterexample(item, item.execution_attempt_id, "FAILED")
    proposal = propose_rule(ce)
    assert proposal.source_counterexample_id == ce.counterexample_id
    assert proposal.scope == "SELF_LEARNING_ONLY"
    assert proposal.mode == "SHADOW"
    assert proposal.status == "PROPOSED"
    assert proposal.proposal_id.endswith(ce.fingerprint.split(":", 1)[1])
