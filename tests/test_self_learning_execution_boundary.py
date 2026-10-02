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
from gnosis.self_learning.execution import (
    BoundCoreExecution,
    create_governed_execution_context,
    execute_approved_core_proposal,
)
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



def environment_attestation_for(scope_lock):
    from gnosis.self_learning.environment_attestation import create_environment_attestation
    return create_environment_attestation(
        scope_lock_id=scope_lock.scope_lock_id,
        observed_at="2026-10-02T03:00:00+02:00",
        python_version="3.11.14",
        platform="Linux-6.x-x86_64",
        runtime_identity="runner:proof-01",
        dependency_digest="sha256:deps",
        environment_facts=("git-clean",),
    )

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

    scope_lock = create_scope_lock(
        batch_id="BATCH-001",
        repository="Autopoiesis-Intelligence/Gnosis-Core",
        ref="refs/heads/main",
        target_commit_sha="abc123",
        selected_contract_ids=("E7.114",),
        selected_criterion_ids=("C1",),
        implementation_paths=("gnosis/self_learning/scope_lock.py",),
        test_runtime_paths=("tests/test_self_learning_execution_boundary.py",),
        commands=("pytest tests/test_self_learning_execution_boundary.py",),
        expected_outcomes=("authorization rejects",),
        evidence_destinations=("artifacts/e7.114/",),
        environment_prerequisites=("python>=3.11",),
        stop_conditions=("wrong commit",),
        evidence_policy_revision="E7.108-r1",
        verification_matrix_revision="E7.103-r1",
        progress_calculation_policy_revision="progress-r1",
    )

    conn = connect()
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
                scope_lock=scope_lock,
                actual_commit_sha="abc123",
                available_paths=("gnosis/self_learning/scope_lock.py", "tests/test_self_learning_execution_boundary.py"),
                progress_before={"E7.114": 0},
                progress_after={"E7.114": 0},
                environment_attestation=environment_attestation_for(scope_lock),
                actual_python_version="3.11.14",
                actual_platform="Linux-6.x-x86_64",
                actual_runtime_identity="runner:proof-01",
                actual_dependency_digest="sha256:deps",
            )
        after = snapshot_database(conn)
        assert after == before
    finally:
        conn.close()


def test_scope_lock_rejects_tampered_runtime_commit_before_execution():
    proposal = canonical_proposal()
    auth = ExecutionAuthorization(
        request_provenance="p",
        owner_approved=True,
        evolution_identity="e",
        approval_id="auth-2",
    )
    snapshot = ExecutionIntentSnapshot(
        provenance_id="p",
        execution_id="x2",
        parent_state_id="parent",
        parent_state_digest="sha256:p",
        evolution_identity="e",
        candidate_binding_digest="sha256:c",
        proposed_state_content_id="sha256:content",
    )
    validity = AuthorizationValidity("auth-2", "policy-1", "ev-2")
    request = ExecutionCommitRequest(
        auth, snapshot, "p", "e", object(), validity
    )
    scope_lock = create_scope_lock(
        batch_id="BATCH-002",
        repository="Autopoiesis-Intelligence/Gnosis-Core",
        ref="refs/heads/main",
        target_commit_sha="abc123",
        selected_contract_ids=("E7.114",),
        selected_criterion_ids=("C1",),
        implementation_paths=("gnosis/self_learning/scope_lock.py",),
        test_runtime_paths=("tests/test_self_learning_execution_boundary.py",),
        commands=("pytest tests/test_self_learning_execution_boundary.py",),
        expected_outcomes=("tampered runtime is rejected",),
        evidence_destinations=("artifacts/e7.114/",),
        environment_prerequisites=("python>=3.11",),
        stop_conditions=("wrong commit",),
        evidence_policy_revision="E7.108-r1",
        verification_matrix_revision="E7.103-r1",
        progress_calculation_policy_revision="progress-r1",
    )

    conn = connect()
    try:
        before = snapshot_database(conn)
        with pytest.raises(ValueError, match="target commit"):
            execute_approved_core_proposal(
                proposal,
                request,
                conn=conn,
                instance=object(),
                candidate=object(),
                record=object(),
                actor="test",
                scope_lock=scope_lock,
                actual_commit_sha="tampered-sha",
                available_paths=(
                    "gnosis/self_learning/scope_lock.py",
                    "tests/test_self_learning_execution_boundary.py",
                ),
                progress_before={"E7.114": 0},
                progress_after={"E7.114": 0},
                environment_attestation=environment_attestation_for(scope_lock),
                actual_python_version="3.11.14",
                actual_platform="Linux-6.x-x86_64",
                actual_runtime_identity="runner:proof-01",
                actual_dependency_digest="sha256:deps",
            )
        after = snapshot_database(conn)
        assert after == before
    finally:
        conn.close()


def test_environment_attestation_is_required_before_commit():
    proposal = canonical_proposal()
    auth = ExecutionAuthorization(request_provenance="p", owner_approved=True, evolution_identity="e", approval_id="auth-3")
    snapshot = ExecutionIntentSnapshot(
        provenance_id="p", execution_id="x3", parent_state_id="parent",
        parent_state_digest="sha256:p", evolution_identity="e",
        candidate_binding_digest="sha256:c", proposed_state_content_id="sha256:content",
    )
    validity = AuthorizationValidity("auth-3", "policy-1", "ev-3")
    request = ExecutionCommitRequest(auth, snapshot, "p", "e", object(), validity)
    scope_lock = create_scope_lock(
        batch_id="BATCH-003", repository="Autopoiesis-Intelligence/Gnosis-Core",
        ref="refs/heads/main", target_commit_sha="abc123",
        selected_contract_ids=("E7.115",), selected_criterion_ids=("C1",),
        implementation_paths=("gnosis/self_learning/environment_attestation.py",),
        test_runtime_paths=("tests/test_self_learning_execution_boundary.py",),
        commands=("pytest tests/test_self_learning_execution_boundary.py",),
        expected_outcomes=("runtime identity substitution is rejected",),
        evidence_destinations=("artifacts/e7.115/",),
        environment_prerequisites=("python>=3.11",),
        stop_conditions=("wrong runtime identity",),
        evidence_policy_revision="E7.108-r1",
        verification_matrix_revision="E7.103-r1",
        progress_calculation_policy_revision="progress-r1",
    )
    attestation = environment_attestation_for(scope_lock)
    conn = connect()
    try:
        before = snapshot_database(conn)
        with pytest.raises(ValueError, match="runtime identity"):
            execute_approved_core_proposal(
                proposal, request, conn=conn, instance=object(),
                candidate=object(), record=object(), actor="test",
                scope_lock=scope_lock, actual_commit_sha="abc123",
                available_paths=("gnosis/self_learning/environment_attestation.py",),
                progress_before={"E7.115": 0}, progress_after={"E7.115": 0},
                environment_attestation=attestation,
                actual_python_version="3.11.14",
                actual_platform="Linux-6.x-x86_64",
                actual_runtime_identity="runner:tampered",
                actual_dependency_digest="sha256:deps",
            )
        assert snapshot_database(conn) == before
    finally:
        conn.close()



def test_governed_context_binds_execution_identity_and_provenance():
    from types import SimpleNamespace

    scope_lock = create_scope_lock(
        batch_id="BATCH-CONTEXT",
        repository="Autopoiesis-Intelligence/Gnosis-Core",
        ref="refs/heads/main", target_commit_sha="abc123",
        selected_contract_ids=("E7.114", "E7.115"),
        selected_criterion_ids=("C1",),
        implementation_paths=("gnosis/self_learning/environment_attestation.py",),
        test_runtime_paths=("tests/test_self_learning_execution_boundary.py",),
        commands=("pytest tests/test_self_learning_execution_boundary.py",),
        expected_outcomes=("context identity remains bound",),
        evidence_destinations=("artifacts/e7.115/",),
        environment_prerequisites=("python>=3.11",),
        stop_conditions=("identity substitution",),
        evidence_policy_revision="E7.108-r1",
        verification_matrix_revision="E7.103-r1",
        progress_calculation_policy_revision="progress-r1",
    )
    attestation = environment_attestation_for(scope_lock)
    provenance = SimpleNamespace(provenance_id="prov-1")
    request = SimpleNamespace(evolution_identity="evo-1", provenance=provenance)
    bound = BoundCoreExecution("proposal-1", "evo-1", "sha256:binding")
    context = create_governed_execution_context(
        scope_lock, attestation,
        actual_commit_sha="abc123",
        available_paths=("gnosis/self_learning/environment_attestation.py",),
        progress_before={"E7.115": 0}, progress_after={"E7.115": 0},
        actual_python_version="3.11.14", actual_platform="Linux-6.x-x86_64",
        actual_runtime_identity="runner:proof-01", actual_dependency_digest="sha256:deps",
        bound_execution=bound, request=request,
    )
    assert context.scope_lock_id == scope_lock.scope_lock_id
    assert context.environment_attestation_id == attestation.attestation_id
    assert context.evolution_identity == "evo-1"
    assert context.provenance_id == "prov-1"
    assert context.proposal_binding_digest == "sha256:binding"


def test_governed_context_rejects_evolution_identity_substitution():
    from types import SimpleNamespace

    scope_lock = create_scope_lock(
        batch_id="BATCH-CONTEXT-2", repository="Autopoiesis-Intelligence/Gnosis-Core",
        ref="refs/heads/main", target_commit_sha="abc123",
        selected_contract_ids=("E7.115",), selected_criterion_ids=("C1",),
        implementation_paths=("gnosis/self_learning/environment_attestation.py",),
        test_runtime_paths=("tests/test_self_learning_execution_boundary.py",),
        commands=("pytest tests/test_self_learning_execution_boundary.py",),
        expected_outcomes=("identity mismatch rejected",),
        evidence_destinations=("artifacts/e7.115/",), environment_prerequisites=("python>=3.11",),
        stop_conditions=("identity mismatch",), evidence_policy_revision="E7.108-r1",
        verification_matrix_revision="E7.103-r1", progress_calculation_policy_revision="progress-r1",
    )
    attestation = environment_attestation_for(scope_lock)
    request = SimpleNamespace(evolution_identity="evo-request", provenance=SimpleNamespace(provenance_id="prov-2"))
    bound = BoundCoreExecution("proposal-2", "evo-bound", "sha256:binding-2")
    with pytest.raises(PermissionError, match="evolution identity mismatch"):
        create_governed_execution_context(
            scope_lock, attestation, actual_commit_sha="abc123",
            available_paths=("gnosis/self_learning/environment_attestation.py",),
            progress_before={"E7.115": 0}, progress_after={"E7.115": 0},
            actual_python_version="3.11.14", actual_platform="Linux-6.x-x86_64",
            actual_runtime_identity="runner:proof-01", actual_dependency_digest="sha256:deps",
            bound_execution=bound, request=request,
        )


def test_governed_context_rejects_provenance_substitution():
    from types import SimpleNamespace
    scope_lock = create_scope_lock(
        batch_id="BATCH-CONTEXT-3", repository="Autopoiesis-Intelligence/Gnosis-Core",
        ref="refs/heads/main", target_commit_sha="abc123",
        selected_contract_ids=("E7.115",), selected_criterion_ids=("C1",),
        implementation_paths=("gnosis/self_learning/environment_attestation.py",),
        test_runtime_paths=("tests/test_self_learning_execution_boundary.py",),
        commands=("pytest tests/test_self_learning_execution_boundary.py",),
        expected_outcomes=("provenance substitution rejected",),
        evidence_destinations=("artifacts/e7.115/",), environment_prerequisites=("python>=3.11",),
        stop_conditions=("provenance mismatch",), evidence_policy_revision="E7.108-r1",
        verification_matrix_revision="E7.103-r1", progress_calculation_policy_revision="progress-r1",
    )
    attestation = environment_attestation_for(scope_lock)
    request = SimpleNamespace(evolution_identity="evo-1", provenance=SimpleNamespace(provenance_id="prov-request"))
    bound = BoundCoreExecution("proposal-3", "evo-1", "sha256:binding-3")
    context = create_governed_execution_context(
        scope_lock, attestation, actual_commit_sha="abc123",
        available_paths=("gnosis/self_learning/environment_attestation.py",),
        progress_before={"E7.115": 0}, progress_after={"E7.115": 0},
        actual_python_version="3.11.14", actual_platform="Linux-6.x-x86_64",
        actual_runtime_identity="runner:proof-01", actual_dependency_digest="sha256:deps",
        bound_execution=bound, request=request,
    )
    assert context.provenance_id == "prov-request"
