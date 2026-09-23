"""Bounded execution planning for accepted Self-Learning governance records.

This module creates an execution plan only. It never applies mutations.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from .governance import GovernanceReview


@dataclass(frozen=True)
class ExecutionPlan:
    plan_id: str
    review_id: str
    proposal_id: str
    action: str
    preconditions: tuple[str, ...]
    authority: str = "execution-plan-only"
    status: str = "PLANNED"
    provenance: str = "self-learning-governed-execution-plan"

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def create_execution_plan(
    review: GovernanceReview,
    *,
    expected_authority: str = "governance-record-only",
) -> ExecutionPlan:
    if review.authority != expected_authority:
        raise ValueError("review authority is not eligible for planning")
    if review.decision != "ACCEPTED":
        raise ValueError("only ACCEPTED governance records may produce execution plans")

    preconditions = (
        "governance_record_identity_verified",
        "proposal_identity_verified",
        "validation_digest_present",
        "execution_target_explicit",
        "external_execution_authority_required",
    )
    action = "APPLY_GOVERNED_PROPOSAL_AFTER_EXTERNAL_AUTHORIZATION"
    canonical = {
        "review_id": review.review_id,
        "proposal_id": review.proposal_id,
        "action": action,
        "preconditions": preconditions,
    }
    plan_id = "sha256:" + hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return ExecutionPlan(
        plan_id=plan_id,
        review_id=review.review_id,
        proposal_id=review.proposal_id,
        action=action,
        preconditions=preconditions,
    )


def serialize_plan(plan: ExecutionPlan) -> str:
    return json.dumps(plan.as_dict(), sort_keys=True, separators=(",", ":"))


# E7.57 bridge-to-Core adapter
from dataclasses import dataclass as _dataclass
from gnosis.self_learning.bridge import CoreMutationProposal
from gnosis.reflection.authority import ExecutionCommitRequest, ExecutionCommitResult, SQLiteExecutionCommitAdapter

@_dataclass(frozen=True)
class BoundCoreExecution:
    proposal_id: str
    evolution_identity: str
    binding_digest: str

def bind_core_proposal(proposal: CoreMutationProposal, request: ExecutionCommitRequest) -> BoundCoreExecution:
    if proposal.status != "APPROVED":
        raise PermissionError("Core mutation proposal is not approved")
    if not request.evolution_identity:
        raise ValueError("execution evolution identity is required")
    canonical={"mutation_id":proposal.mutation_id,"integration_id":proposal.integration_id,"version_id":proposal.version_id,"evolution_identity":request.evolution_identity}
    binding="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return BoundCoreExecution(proposal.mutation_id,request.evolution_identity,binding)

def execute_approved_core_proposal(proposal: CoreMutationProposal, request: ExecutionCommitRequest, conn: object, instance: object, candidate: object, record: object, *, actor: str) -> ExecutionCommitResult:
    bind_core_proposal(proposal, request)
    return SQLiteExecutionCommitAdapter().commit(conn, instance, candidate, record, request, actor=actor)


# E7.57 bridge-to-Core adapter
from dataclasses import dataclass as _dataclass
from gnosis.self_learning.bridge import CoreMutationProposal
from gnosis.reflection.authority import ExecutionCommitRequest, ExecutionCommitResult, SQLiteExecutionCommitAdapter

@_dataclass(frozen=True)
class BoundCoreExecution:
    proposal_id: str
    evolution_identity: str
    binding_digest: str

def bind_core_proposal(proposal: CoreMutationProposal, request: ExecutionCommitRequest) -> BoundCoreExecution:
    if proposal.status != "APPROVED":
        raise PermissionError("Core mutation proposal is not approved")
    if not request.evolution_identity:
        raise ValueError("execution evolution identity is required")
    canonical={"mutation_id":proposal.mutation_id,"integration_id":proposal.integration_id,"version_id":proposal.version_id,"evolution_identity":request.evolution_identity}
    binding="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return BoundCoreExecution(proposal.mutation_id,request.evolution_identity,binding)

def execute_approved_core_proposal(proposal: CoreMutationProposal, request: ExecutionCommitRequest, conn: object, instance: object, candidate: object, record: object, *, actor: str) -> ExecutionCommitResult:
    bind_core_proposal(proposal, request)
    return SQLiteExecutionCommitAdapter().commit(conn, instance, candidate, record, request, actor=actor)
