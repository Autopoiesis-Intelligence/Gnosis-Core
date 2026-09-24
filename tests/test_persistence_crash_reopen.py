import pytest

from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.storage import connect, load_instance, persist_transition, save_instance, verify_durable_graph, load_execution_evidence
from gnosis.self_learning.collaboration_evidence import record_execution_evidence


CHECKPOINTS = [
    "before_begin",
    "after_begin",
    "after_candidate",
    "after_transition",
    "after_audit",
    "after_head",
    "before_commit",
]


def _prepare(path):
    conn = connect(path)
    instance = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(conn, instance)
    old_state_id = instance.engine.state.state_id
    proposed = instance.engine.state.with_elements({"next": 1})
    candidate = Candidate(instance.engine.state.state_id, proposed, "crash-test")
    record = instance.engine.step(candidate)
    return conn, instance, candidate, record, proposed, old_state_id


@pytest.mark.parametrize("point", CHECKPOINTS)
def test_crash_checkpoint_reopen_has_only_old_durable_state(tmp_path, point):
    path = tmp_path / f"{point}.sqlite"
    conn, instance, candidate, record, proposed, old_state_id = _prepare(path)
    with pytest.raises(RuntimeError, match="injected failure"):
        persist_transition(conn, instance, candidate, record, actor="u", failure_at=point)
    conn.close()

    reopened = connect(path)
    recovered = load_instance(reopened, instance.instance_id)
    assert recovered.engine.state.state_id == old_state_id
    assert recovered.engine.state.state_id != proposed.state_id
    assert reopened.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 0
    assert reopened.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL").fetchone()[0] == 0
    assert reopened.execute("SELECT COUNT(*) FROM candidates").fetchone()[0] == 0
    assert reopened.execute("SELECT COUNT(*) FROM states").fetchone()[0] == 1
    assert verify_durable_graph(reopened)[0] == 1


def test_after_commit_reopen_has_complete_new_state(tmp_path):
    path = tmp_path / "after-commit.sqlite"
    conn, instance, candidate, record, proposed, _old_state_id = _prepare(path)
    with pytest.raises(RuntimeError, match="injected failure"):
        persist_transition(conn, instance, candidate, record, actor="u", failure_at="after_commit")
    conn.close()

    reopened = connect(path)
    recovered = load_instance(reopened, instance.instance_id)
    assert recovered.engine.state.state_id == proposed.state_id
    assert reopened.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 1
    assert reopened.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL").fetchone()[0] == 1
    assert reopened.execute("SELECT COUNT(*) FROM candidates").fetchone()[0] == 1
    assert reopened.execute("SELECT COUNT(*) FROM states").fetchone()[0] == 2
    assert verify_durable_graph(reopened)[0] == 2


def _evidence(record):
    return record_execution_evidence(
        authorization_id="auth-crash", authorization_digest="sha256:auth",
        review_id="review-crash", review_digest="sha256:review",
        proposal_id=record.transition_id, proposal_revision="r1",
        action_class="CREATE_PUBLIC_ISSUE_OR_PR", target_resource="repo:public/project",
        authorized_scope="issue:create", executor_id="executor-crash",
        execution_attempt_id=f"attempt:{record.transition_id}", execution_order="1",
        result_status="SUCCEEDED", target_before_revision="before",
        target_after_revision="after", privacy_classification="PUBLIC_APPROVED",
        observed_scope="issue:create", expected_preconditions=("target-current",),
        provenance_refs=("auth-crash", "review-crash", record.transition_id),
    )


def test_transition_and_evidence_rollback_together(tmp_path):
    path = tmp_path / "atomic-evidence.sqlite"
    conn, instance, candidate, record, proposed, old_state_id = _prepare(path)
    evidence = _evidence(record)
    with pytest.raises(RuntimeError, match="injected failure"):
        persist_transition(conn, instance, candidate, record, actor="u", evidence=evidence, failure_at="after_evidence")
    conn.close()
    reopened = connect(path)
    assert load_instance(reopened, instance.instance_id).engine.state.state_id == old_state_id
    assert reopened.execute("SELECT COUNT(*) FROM execution_evidence").fetchone()[0] == 0
    assert reopened.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 0
    assert reopened.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id IS NOT NULL").fetchone()[0] == 0


def test_transition_commit_contains_evidence_atomically(tmp_path):
    path = tmp_path / "atomic-evidence-commit.sqlite"
    conn, instance, candidate, record, proposed, _old_state_id = _prepare(path)
    evidence = _evidence(record)
    persist_transition(conn, instance, candidate, record, actor="u", evidence=evidence)
    assert load_execution_evidence(conn, evidence.evidence_id) == evidence
    assert conn.execute("SELECT COUNT(*) FROM transitions").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM audit_events WHERE transition_id=?", (record.transition_id,)).fetchone()[0] == 1
    conn.close()
