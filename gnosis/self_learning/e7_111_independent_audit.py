"""E7.111 independent audit of the E7.107-E7.110 evidence chain."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class AuditState(str, Enum):
    PASSED="PASSED"; REJECTED="REJECTED"; BLOCKED="BLOCKED"

@dataclass(frozen=True)
class AuditFinding:
    check_id: str
    passed: bool
    detail: str

@dataclass(frozen=True)
class AuditResult:
    batch_id: str
    target_commit_sha: str
    findings: tuple[AuditFinding,...]
    state: AuditState

AUDIT_CHECKS=(
 "exact_commit",
 "execution_identity",
 "evidence_completeness",
 "acceptance_consistency",
 "reconciliation_consistency",
 "no_conflicting_evidence",
 "terminal_state_consistency",
)

def audit_chain(*, batch_id:str,target_commit_sha:str,record_commit_sha:str,checks:dict[str,bool])->AuditResult:
    if not batch_id or not target_commit_sha or not record_commit_sha:
        raise ValueError("audit identity is required")
    findings=tuple(
        AuditFinding(name, bool(checks.get(name,False)), "")
        for name in AUDIT_CHECKS
    )
    exact=record_commit_sha==target_commit_sha
    findings=tuple(AuditFinding(f.check_id, f.passed and exact if f.check_id=="exact_commit" else f.passed, f.detail) for f in findings)
    state=AuditState.PASSED if all(f.passed for f in findings) else AuditState.REJECTED
    return AuditResult(batch_id,target_commit_sha,findings,state)
