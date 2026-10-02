"""Fail-closed orchestration from verified feedback to a shadow candidate."""
from __future__ import annotations

from gnosis.self_learning.feedback_classification import (
    classify_partner_feedback,
    may_form_learning_candidate,
)
from gnosis.self_learning.pattern_extraction import extract_patterns, may_generate_candidate_contract
from gnosis.self_learning.candidate_contract import (
    CandidateContract,
    create_candidate_contract,
    may_enter_shadow_evaluation,
)

def feedback_to_candidate(
    *,
    result_id: str,
    outcome_class: str,
    evidence_refs: tuple[str, ...],
    rationale: str,
    facts: tuple[str, ...],
    normalization_id: str,
    input_digest: str,
    objective: str,
    scope: str,
    extraction_revision: str = "r1",
    contract_revision: str = "r1",
) -> CandidateContract | None:
    classification = classify_partner_feedback(
        result_id=result_id,
        outcome_class=outcome_class,
        evidence_refs=evidence_refs,
        rationale=rationale,
        status="VERIFIED",
    )
    if not may_form_learning_candidate(classification=classification):
        return None

    extraction = extract_patterns(
        normalization_id=normalization_id,
        input_digest=input_digest,
        facts=facts,
        extraction_revision=extraction_revision,
        status="ACCEPTED",
    )
    if not may_generate_candidate_contract(result=extraction):
        return None

    candidate = create_candidate_contract(
        extraction_id=extraction.extraction_id,
        pattern_refs=extraction.patterns,
        relation_refs=tuple(f"{s}:{p}:{o}" for s, p, o in extraction.relations),
        objective=objective,
        scope=scope,
        evidence_refs=classification.evidence_refs,
        contract_revision=contract_revision,
        status="SHADOW",
    )
    if not may_enter_shadow_evaluation(candidate=candidate):
        return None
    return candidate

def candidate_grants_execution_authority(*, candidate: CandidateContract) -> bool:
    return False
