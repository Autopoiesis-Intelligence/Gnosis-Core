from dataclasses import replace

from gnosis.self_learning.e7_108_execution_record import (
    CriterionEvidence,
    ExecutionRecord,
    ExecutionState,
)
from gnosis.self_learning.e7_109_evidence_acceptance import (
    AcceptanceState,
    EvidenceItem,
    AcceptanceResult,
)
from gnosis.self_learning.e7_110_reconciliation import (
    Metric,
    ReconciliationState,
    ReconciliationSnapshot,
    reconcile,
)
from gnosis.self_learning.e7_111_independent_audit import AuditState, audit_chain
from gnosis.self_learning.e7_114_runtime_attestation import RuntimeAttestation


def evidence_chain():
    criterion = CriterionEvidence("C1", "expected", "observed", "E1", True)
    record = ExecutionRecord(
        batch_id="B",
        target_commit_sha="abc",
        repository_ref="repo@abc",
        environment_identity={"python": "3.12"},
        commands=("echo observed",),
        candidate_selection_id="SEL-1",
        baseline_id="BASE-1",
        evidence_policy_revision="EVID-1",
        verification_matrix_revision="VM-1",
        criteria=(criterion,),
        state=ExecutionState.COMPLETED,
    )
    item = EvidenceItem("C1", "E1", "expected", "observed", True)
    acceptance = AcceptanceResult(
        batch_id="B",
        execution_record_id="EXEC-1",
        items=(item,),
        state=AcceptanceState.ACCEPTED,
        reason="all supplied criteria accepted",
    )
    reconciliation = reconcile(
        batch_id="B",
        acceptance_id="ACC-1",
        metrics=(Metric("M1", 1.0, 1.0),),
    )
    attestation = RuntimeAttestation("/repo", "abc", "abc", "PASS", "ATT-DIGEST")
    return record, acceptance, reconciliation, attestation


def test_all_independent_checks_pass():
    record, acceptance, reconciliation, attestation = evidence_chain()
    result = audit_chain(
        batch_id="B",
        target_commit_sha="abc",
        record_commit_sha="abc",
        execution_record=record,
        acceptance_result=acceptance,
        reconciliation_snapshot=reconciliation,
        runtime_attestation=attestation,
    )
    assert result.state is AuditState.PASSED
    assert len(result.findings) == 8


def test_wrong_commit_rejects():
    record, acceptance, reconciliation = evidence_chain()
    result = audit_chain(
        batch_id="B",
        target_commit_sha="abc",
        record_commit_sha="def",
        execution_record=record,
        acceptance_result=acceptance,
        reconciliation_snapshot=reconciliation,
    )
    assert result.state is AuditState.REJECTED
    assert not next(f for f in result.findings if f.check_id == "exact_commit").passed


def test_tampered_execution_evidence_rejects():
    record, acceptance, reconciliation = evidence_chain()
    tampered = replace(record, criteria=(
        CriterionEvidence("C1", "expected", "", "E1", True),
    ))
    result = audit_chain(
        batch_id="B",
        target_commit_sha="abc",
        record_commit_sha="abc",
        execution_record=tampered,
        acceptance_result=acceptance,
        reconciliation_snapshot=reconciliation,
    )
    assert result.state is AuditState.REJECTED
    assert not next(f for f in result.findings if f.check_id == "evidence_completeness").passed


def test_tampered_acceptance_rejects():
    record, acceptance, reconciliation = evidence_chain()
    tampered = replace(acceptance, state=AcceptanceState.REJECTED)
    result = audit_chain(
        batch_id="B",
        target_commit_sha="abc",
        record_commit_sha="abc",
        execution_record=record,
        acceptance_result=tampered,
        reconciliation_snapshot=reconciliation,
    )
    assert result.state is AuditState.REJECTED
    assert not next(f for f in result.findings if f.check_id == "acceptance_consistency").passed


def test_conflicting_reconciliation_rejects():
    record, acceptance, reconciliation = evidence_chain()
    conflict = reconcile(
        batch_id="B",
        acceptance_id="ACC-1",
        metrics=(Metric("M1", 1.0, 2.0),),
    )
    assert reconciliation.state is ReconciliationState.RECONCILED
    result = audit_chain(
        batch_id="B",
        target_commit_sha="abc",
        record_commit_sha="abc",
        execution_record=record,
        acceptance_result=acceptance,
        reconciliation_snapshot=conflict,
    )
    assert result.state is AuditState.REJECTED
    assert not next(f for f in result.findings if f.check_id == "reconciliation_consistency").passed


def test_missing_runtime_attestation_rejects():
    record, acceptance, reconciliation, _ = evidence_chain()
    result = audit_chain(
        batch_id="B",
        target_commit_sha="abc",
        record_commit_sha="abc",
        execution_record=record,
        acceptance_result=acceptance,
        reconciliation_snapshot=reconciliation,
    )
    assert result.state is AuditState.REJECTED
    assert not next(f for f in result.findings if f.check_id == "runtime_checkout_attestation").passed


def test_tampered_runtime_attestation_rejects():
    record, acceptance, reconciliation, _ = evidence_chain()
    tampered = RuntimeAttestation("/repo", "def", "abc", "PASS", "TAMPER")
    result = audit_chain(
        batch_id="B",
        target_commit_sha="abc",
        record_commit_sha="abc",
        execution_record=record,
        acceptance_result=acceptance,
        reconciliation_snapshot=reconciliation,
        runtime_attestation=tampered,
    )
    assert result.state is AuditState.REJECTED
