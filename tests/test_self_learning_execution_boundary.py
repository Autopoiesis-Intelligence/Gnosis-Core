import pytest

from gnosis.self_learning.bridge import (
    approve_core_mutation,
    create_core_mutation_proposal,
)
from gnosis.self_learning.integration import create_integration_record
from gnosis.self_learning.knowledge import (
    apply_knowledge_update,
    propose_knowledge_update,
)
from gnosis.self_learning.ledger import create_event
from gnosis.self_learning.lineage import record_version
from gnosis.self_learning.lifecycle import verify_lifecycle
from gnosis.self_learning.promotion import decide_promotion, propose_promotion
from gnosis.self_learning.execution import execute_approved_core_proposal
from gnosis.self_learning.scope_lock import create_scope_lock
from gnosis.reflection.authority import (
    ExecutionAuthorization,
    ExecutionCommitRequest,
    ExecutionIntentSnapshot,
)
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.storage.database import connect


def canonical_proposal():
    subject_id = "subject-test"
    events = []
    previous = "GENESIS"
    for i, event_type in enumerate(
        (
            "DATABASE",
            "FINDING",
            "PROPOSAL",
            "VALIDATION",
            "GOVERNANCE",
            "EXECUTION_PLAN",
            "RECEIPT",
        )
    ):
        event = create_event(event_type, subject_id, {"stage": i}, previous)
        events.append(event)
        previous = event.event_digest

    lifecycle = verify_lifecycle(events, subject_id)
    assert lifecycle.complete

    update = apply_knowledge_update(
        propose_knowledge_update(
            subject_id=subject_id,
            evidence_digest=events[-1].event_digest,
            knowledge={"rule": "bounded"},
            lifecycle=lifecycle,
            scope="common-self-learning",
            shareable=True,
        )
    )
    version = record_version(update)
    promotion = propose_promotion(
        version,
        evidence_refs=(events[-1].event_digest,),
        reason="generalizable",
    )
    accepted = decide_promotion(
        promotion,
        decision="ACCEPTED",
        reviewer="cycle-governance",
    )
    integration = create_integration_record(
        accepted,
        action="controlled-core-learning-integration",
    )
    return approve_core_mutation(
        create_core_mutation_proposal(integration),
        approver="test",
    )


def snapshot_database(conn):
    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]
    snapshot = {}
    for table in tables:
        columns = [
            row[1]
            for row in conn.execute(
                f'PRAGMA table_info("{table}")'
            ).fetchall()
        ]
        quoted = ", ".join(f'"{column}"' for column in columns)
        rows = conn.execute(
            f'SELECT {quoted} FROM "{table}" ORDER BY rowid'
        ).fetchall()
        snapshot[table] = [tuple(row) for row in rows]
    return snapshot


def test_execution_adapter_fails_closed_without_owner_authorization():
    proposal = canonical_proposal()
    auth = ExecutionAuthorization(
        request_provenance="p",
        owner_approved=False,
        evolution_identity="e",
        approval_id="auth-1",
    )
    snapshot = ExecutionIntentSnapshot(
        provenance_id="p",
        execution_id="x",
        parent_state_id="parent",
        parent_state_digest="sha256:p",
        evolution_identity="e",
        candidate_binding_digest="sha256:c",
        proposed_state_content_id="sha256:content",
    )
    validity = AuthorizationValidity("auth-1", "policy-1", "ev-1")
    request = ExecutionCommitRequest(
        auth, snapshot, "p", "e", object(), validity
    )

    scope_lock = create_scope_lock(\n        batch_id="BATCH-001",\n        repository="Autopoiesis-Intelligence/Gnosis-Core",\n        ref="refs/heads/main",\n        target_commit_sha="abc123",\n        selected_contract_ids=("E7.114",),\n        selected_criterion_ids=("C1",),\n        implementation_paths=("gnosis/self_learning/scope_lock.py",),\n        test_runtime_paths=("tests/test_self_learning_execution_boundary.py",),\n        commands=("pytest tests/test_self_learning_execution_boundary.py",),\n        expected_outcomes=("authorization rejects",),\n        evidence_destinations=("artifacts/e7.114/",),\n        environment_prerequisites=("python>=3.11",),\n        stop_conditions=("wrong commit",),\n        evidence_policy_revision="E7.108-r1",\n        verification_matrix_revision="E7.103-r1",\n        progress_calculation_policy_revision="progress-r1",\n    )\n\n    conn = connect()
    try:
        before = snapshot_database(conn)
        with pytest.raises(PermissionError):
            execute_approved_core_proposal(
                proposal,
                request,
                conn=conn,
                instance=object(),
                candidate=object(),
                record=object(),
                actor="test",
            )
        after = snapshot_database(conn)
        assert after == before
    finally:
        conn.close()
