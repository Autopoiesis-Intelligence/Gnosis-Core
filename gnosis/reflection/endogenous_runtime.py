"""Read-only orchestration from cumulative Reflection evidence to endogenous candidates.

This layer connects durable Reflection evidence to the existing endogenous
candidate generator. It does not mutate Engine state, persist transitions,
or grant execution authority.
"""
from __future__ import annotations

from typing import Any

from .analyzer import ReflectionReport
from .endogenous import EndogenousGeneration, generate_endogenous_candidates
from .runtime import CumulativeReflectionReport


def generate_from_cumulative_reflection(
    engine: Any,
    cumulative: CumulativeReflectionReport,
    *,
    max_candidates: int | None = None,
) -> EndogenousGeneration:
    """Generate endogenous candidates using the same durable evidence seen by Reflection."""
    return generate_endogenous_candidates(
        engine.state,
        cumulative.current,
        memory_evidence=cumulative.evolution_evidence,
        max_candidates=max_candidates,
        budget=getattr(engine, "budget", None),
    )


def generate_from_reflection_report(
    engine: Any,
    report: ReflectionReport,
    *,
    memory_evidence: tuple[object, ...] = (),
    max_candidates: int | None = None,
) -> EndogenousGeneration:
    """Explicit low-level adapter for callers that already hold a reflection report."""
    return generate_endogenous_candidates(
        engine.state,
        report,
        memory_evidence=memory_evidence,
        max_candidates=max_candidates,
        budget=getattr(engine, "budget", None),
    )


from gnosis.evolution.sandbox import SandboxBudget, SandboxResult, run_sandbox
from gnosis.evolution.evaluator import EvaluationResult, evaluate_observation


def evaluate_candidate_in_sandbox(
    engine: Any,
    candidate: Any,
    observe: Any,
    *,
    predicate: str = "observations_present",
    budget: SandboxBudget = SandboxBudget(),
) -> tuple[SandboxResult, EvaluationResult]:
    """Evaluate an endogenous candidate through the canonical read-only sandbox."""
    result = run_sandbox(engine.state, candidate, observe, budget=budget)
    evaluation = evaluate_observation(
        result.execution.observations,
        evidence_digest=result.execution.evidence_digest,
        predicate=predicate,
    )
    return result, evaluation


from gnosis.evolution.provenance import EvidenceProvenance, build_provenance
from .governance import GovernanceDecision


def build_endogenous_provenance(
    candidate: Any,
    sandbox: SandboxResult,
    evaluation: EvaluationResult,
    governance: GovernanceDecision,
    *,
    parent_state_digest: str,
) -> EvidenceProvenance:
    """Bind endogenous sandbox evidence to canonical provenance without authority."""
    execution = sandbox.execution
    if execution.candidate_id != candidate.candidate_id:
        raise ValueError("sandbox candidate does not match endogenous candidate")
    if execution.parent_state_id != candidate.parent_state_id:
        raise ValueError("sandbox parent state does not match endogenous candidate")
    if not sandbox.accepted_for_evaluation:
        raise ValueError("sandbox execution is not admissible for provenance")
    if evaluation.evidence_digest != execution.evidence_digest:
        raise ValueError("evaluation evidence digest does not match sandbox evidence")
    if governance.can_activate or governance.can_rollback:
        raise ValueError("governance evidence must not grant authority")
    return build_provenance(
        candidate_id=candidate.candidate_id,
        parent_state_id=candidate.parent_state_id,
        parent_state_digest=parent_state_digest,
        proposed_state_digest=execution.proposed_state_digest,
        proposed_state_content_id=candidate.proposed_state.content_id,
        candidate_binding_digest=candidate.binding_digest(parent_state_digest),
        observations=execution.observations,
        evidence_digest=execution.evidence_digest,
        evaluation_status=evaluation.status,
        shadow_status=governance.shadow_status,
        invariant_status=governance.invariant_status,
        governance_decision=governance.decision,
        evaluator_identity_ref=evaluation.evaluator_identity.implementation_ref,
        evaluator_identity_version=evaluation.evaluator_identity.implementation_version,
    )
