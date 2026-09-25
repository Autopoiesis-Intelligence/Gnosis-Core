"""E7.107 bounded first-verification-batch readiness gate."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping

class ReadinessState(str, Enum):
    PREPARING="PREPARING"; READY="READY"; BLOCKED="BLOCKED"; INVALIDATED="INVALIDATED"; EXECUTING="EXECUTING"; COMPLETED="COMPLETED"; FAILED="FAILED"

CHECK_NAMES=(
 "candidate_selection_frozen","baseline_immutable","target_commit_available",
 "ref_resolves_to_target","implementation_paths_exist","commands_exist",
 "runtime_available","evidence_destination_available","evidence_policy_identified",
 "verification_matrix_identified","no_blocking_dependency","stop_conditions_defined",
 "recovery_retry_defined",
)

@dataclass(frozen=True)
class ReadinessCheck:
    name: str
    passed: bool
    detail: str=""

@dataclass(frozen=True)
class ReadinessRecord:
    batch_id: str
    target_commit_sha: str
    repository_ref: str
    baseline_id: str
    candidate_selection_id: str
    evidence_policy_revision: str
    verification_matrix_revision: str
    environment_identity: Mapping[str,str]
    checks: tuple[ReadinessCheck,...]
    state: ReadinessState

    @property
    def ready(self)->bool:
        return self.state is ReadinessState.READY and all(c.passed for c in self.checks)

def evaluate_readiness(*, batch_id:str,target_commit_sha:str,repository_ref:str,baseline_id:str,candidate_selection_id:str,evidence_policy_revision:str,verification_matrix_revision:str,environment_identity:Mapping[str,str],checks:Mapping[str,bool])->ReadinessRecord:
    if not batch_id or not target_commit_sha or not repository_ref: raise ValueError("batch identity is required")
    records=tuple(ReadinessCheck(n,bool(checks.get(n,False))) for n in CHECK_NAMES)
    state=ReadinessState.READY if all(c.passed for c in records) else ReadinessState.BLOCKED
    return ReadinessRecord(batch_id,target_commit_sha,repository_ref,baseline_id,candidate_selection_id,evidence_policy_revision,verification_matrix_revision,dict(environment_identity),records,state)

def can_execute(record:ReadinessRecord, resolved_commit_sha:str)->bool:
    return record.ready and resolved_commit_sha==record.target_commit_sha

def invalidate_for_commit_change(record:ReadinessRecord,resolved_commit_sha:str)->ReadinessRecord:
    if resolved_commit_sha!=record.target_commit_sha:
        return ReadinessRecord(**{**record.__dict__,"state":ReadinessState.INVALIDATED})
    return record
