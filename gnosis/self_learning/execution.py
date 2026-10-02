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
from gnosis.reflection.authority import ExecutionCommitRequest, ExecutionCommitResult
from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter


@_dataclass(frozen=True)
class BoundCoreExecution:
    proposal_id: str
    evolution_identity: str
    binding_digest: str


def _canonical_binding(proposal: CoreMutationProposal, evolution_identity: str) -> str:
    canonical = {
        "mutation_id": proposal.mutation_id,
        "integration_id": proposal.integration_id,
        "version_id": proposal.version_id,
        "evolution_identity": evolution_identity,
    }
    return "sha256:" + hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def bind_core_proposal(
    proposal: CoreMutationProposal,
    request: ExecutionCommitRequest,
) -> BoundCoreExecution:
    if proposal.status != "APPROVED":
        raise PermissionError("Core mutation proposal is not approved")

    canonical_proposal = {
        "integration_id": proposal.integration_id,
        "version_id": proposal.version_id,
        "target": proposal.target,
        "action": proposal.action,
    }
    expected = "sha256:" + hashlib.sha256(
        json.dumps(canonical_proposal, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if proposal.mutation_id != expected:
        raise ValueError("proposal identity does not match immutable bridge fields")

    if not request.evolution_identity:
        raise ValueError("execution evolution identity is required")

    return BoundCoreExecution(
        proposal.mutation_id,
        request.evolution_identity,
        _canonical_binding(proposal, request.evolution_identity),
    )


def require_bound_core_execution(
    proposal: CoreMutationProposal,
    request: ExecutionCommitRequest,
    bound: BoundCoreExecution,
) -> None:
    """Fail closed unless the exact proposal/request pair produced this binding."""
    if not isinstance(bound, BoundCoreExecution):
        raise PermissionError("bound Core execution is required")
    if bound.proposal_id != proposal.mutation_id:
        raise PermissionError("bound Core execution proposal mismatch")
    if bound.evolution_identity != request.evolution_identity:
        raise PermissionError("bound Core execution evolution mismatch")
    expected = _canonical_binding(proposal, request.evolution_identity)
    if bound.binding_digest != expected:
        raise PermissionError("bound Core execution digest mismatch")


def execute_approved_core_proposal(
    proposal: CoreMutationProposal,
    request: ExecutionCommitRequest,
    conn: object,
    instance: object,
    candidate: object,
    record: object,
    *,
    actor: str,
) -> ExecutionCommitResult:
    bound = bind_core_proposal(proposal, request)
    require_bound_core_execution(proposal, request, bound)
    return SQLiteExecutionCommitAdapter().commit(
        conn, instance, candidate, record, request, actor=actor
    )
