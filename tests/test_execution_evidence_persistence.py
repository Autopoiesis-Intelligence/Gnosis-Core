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
    conn.execute("UPDATE execution_evidence SET observed_scope='issue:update' WHERE evidence_id=?", (item.evidence_id,))
    conn.commit()
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
