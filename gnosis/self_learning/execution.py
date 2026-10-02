"""Bounded execution planning for accepted Self-Learning governance records.

This module creates an execution plan only. It never applies mutations.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

from .governance import GovernanceReview
from .scope_lock import ScopeLock, validate_scope_lock
from .environment_attestation import EnvironmentAttestation, validate_environment_attestation


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

def bind_core_proposal(proposal: CoreMutationProposal, request: ExecutionCommitRequest) -> BoundCoreExecution:
    if proposal.status != "APPROVED":
        raise PermissionError("Core mutation proposal is not approved")
    canonical_proposal={"integration_id":proposal.integration_id,"version_id":proposal.version_id,"target":proposal.target,"action":proposal.action}
    expected="sha256:"+hashlib.sha256(json.dumps(canonical_proposal,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if proposal.mutation_id != expected:
        raise ValueError("proposal identity does not match immutable bridge fields")
    if not request.evolution_identity:
        raise ValueError("execution evolution identity is required")
    canonical={"mutation_id":proposal.mutation_id,"integration_id":proposal.integration_id,"version_id":proposal.version_id,"evolution_identity":request.evolution_identity}
    binding="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return BoundCoreExecution(proposal.mutation_id,request.evolution_identity,binding)

@dataclass(frozen=True)
class GovernedExecutionContext:
    """Capability evidence created only after all pre-execution gates pass."""
    scope_lock_id: str
    environment_attestation_id: str


def create_governed_execution_context(
    scope_lock: ScopeLock,
    environment_attestation: EnvironmentAttestation,
    *,
    actual_commit_sha: str,
    available_paths: tuple[str, ...],
    progress_before: object,
    progress_after: object,
    actual_python_version: str,
    actual_platform: str,
    actual_runtime_identity: str,
    actual_dependency_digest: str,
) -> GovernedExecutionContext:
    governed_context = create_governed_execution_context(
        scope_lock, environment_attestation,
        actual_commit_sha=actual_commit_sha,
        available_paths=available_paths,
        progress_before=progress_before,
        progress_after=progress_after,
        actual_python_version=actual_python_version,
        actual_platform=actual_platform,
        actual_runtime_identity=actual_runtime_identity,
        actual_dependency_digest=actual_dependency_digest,
    )
    return GovernedExecutionContext(
        scope_lock_id=scope_lock.scope_lock_id,
        environment_attestation_id=environment_attestation.attestation_id,
    )


def execute_approved_core_proposal(
    proposal: CoreMutationProposal,
    request: ExecutionCommitRequest,
    conn: object,
    instance: object,
    candidate: object,
    record: object,
    *,
    actor: str,
    scope_lock: ScopeLock,
    actual_commit_sha: str,
    available_paths: tuple[str, ...],
    progress_before: object,
    progress_after: object,
    environment_attestation: EnvironmentAttestation,
    actual_python_version: str,
    actual_platform: str,
    actual_runtime_identity: str,
    actual_dependency_digest: str,
) -> ExecutionCommitResult:
    # E7.114 is a pre-execution gate, not an authorization mechanism.
    validate_scope_lock(
        scope_lock,
        actual_commit_sha=actual_commit_sha,
        available_paths=available_paths,
        progress_before=progress_before,
        progress_after=progress_after,
    )
    validate_environment_attestation(
        environment_attestation,
        expected_scope_lock_id=scope_lock.scope_lock_id,
        actual_python_version=actual_python_version,
        actual_platform=actual_platform,
        actual_runtime_identity=actual_runtime_identity,
        actual_dependency_digest=actual_dependency_digest,
    )
    bind_core_proposal(proposal, request)
    return SQLiteExecutionCommitAdapter().commit(conn, instance, candidate, record, request, actor=actor, governed_context=governed_context)
