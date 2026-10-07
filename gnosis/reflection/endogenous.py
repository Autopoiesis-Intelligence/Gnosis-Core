"""Bounded endogenous candidate generation from canonical reflection proposals.

This module generates Core Candidates from evidence-backed RuleProposals. It does
not activate rules, mutate an Engine, or bypass Core Test/Select. The generated
state records the proposal as a relation in X/R, making the hypothesis itself a
bounded endogenous state transition rather than an external callback.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Sequence
from gnosis.core.evolution import Engine
from gnosis.core.types import Candidate, Relation, State
from gnosis.core.budget import Budget
from .analyzer import ReflectionReport, RuleProposal

MAX_ENDOGENOUS_CANDIDATES = 20  # default; bounded by caller-provided evolution budget
REFLECTION_NODE = "__gnozis_reflection__"

@dataclass(frozen=True)
class EndogenousGeneration:
    candidates: tuple[Candidate, ...]
    proposal_ids: tuple[str, ...]
    bounded: bool = True


def _proposal_relation(proposal: RuleProposal, memory_outcomes: tuple[str, ...] = ()) -> Relation:
    return Relation(
        source=REFLECTION_NODE,
        target=proposal.proposal_id,
        relation_type="proposed_rule",
        value={
            "finding_id": proposal.finding_id,
            "rule_id": proposal.rule_id,
            "current_version": proposal.current_version,
            "proposed_version": proposal.proposed_version,
            "hypothesis": proposal.hypothesis,
            "evidence_refs": proposal.evidence_refs,
            "historical_memory_outcomes": memory_outcomes,
        },
    )


def generate_endogenous_candidates(
    state: State,
    report: ReflectionReport,
    *,
    memory_evidence: Sequence[object] = (),
    max_candidates: int | None = None,
    budget: Budget | None = None,
) -> EndogenousGeneration:
    """Generate at most 20 proposal-backed candidates deterministically.

    Candidates are hypotheses encoded as ordinary Core state transitions. No
    proposal is activated and no Engine state is mutated by this function.
    """
    if budget is not None and budget.remaining < 1:
        return EndogenousGeneration(candidates=(), proposal_ids=())
    requested = MAX_ENDOGENOUS_CANDIDATES if max_candidates is None else max_candidates
    if not 1 <= requested <= MAX_ENDOGENOUS_CANDIDATES:
        raise ValueError("max_candidates must be in range 1..20")
    limit = requested if budget is None else min(requested, budget.remaining)
    proposals = tuple(report.proposals[:limit])
    candidates: list[Candidate] = []
    memory_refs = tuple(str(getattr(item, "memory_id")) for item in memory_evidence if getattr(item, "memory_id", None))
    memory_outcomes = tuple(sorted(str(getattr(item, "outcome")) for item in memory_evidence if getattr(item, "outcome", None)))
    memory_signature = tuple(sorted(memory_refs))
    for proposal in proposals:
        proposed_state = state.with_elements({
            REFLECTION_NODE: {"kind": "reflection"},
            proposal.proposal_id: {
                "kind": "rule_proposal",
                "finding_id": proposal.finding_id,
                "rule_id": proposal.rule_id,
                "current_version": proposal.current_version,
                "proposed_version": proposal.proposed_version,
                "hypothesis": proposal.hypothesis,
                "evidence_refs": proposal.evidence_refs,
                "memory_evidence_refs": memory_refs,
                "historical_memory_outcomes": memory_outcomes,
                "memory_signature": memory_signature,
            },
        }).with_relations((_proposal_relation(proposal, memory_outcomes),))
        candidates.append(
            Candidate(
                parent_state_id=state.state_id,
                proposed_state=proposed_state,
                origin="reflection:endogenous",
            )
        )
    return EndogenousGeneration(
        candidates=tuple(candidates),
        proposal_ids=tuple(p.proposal_id for p in proposals),
    )


def candidate_binds_proposal(candidate: Candidate, proposal: RuleProposal) -> bool:
    """Return True only when an endogenous Candidate is deterministically bound to its RuleProposal."""
    if candidate.origin != "reflection:endogenous":
        return False
    node = candidate.proposed_state.elements.get(proposal.proposal_id)
    if not isinstance(node, Mapping):
        return False
    if node.get("kind") != "rule_proposal":
        return False
    if node.get("finding_id") != proposal.finding_id:
        return False
    if node.get("rule_id") != proposal.rule_id:
        return False
    if node.get("current_version") != proposal.current_version:
        return False
    if node.get("proposed_version") != proposal.proposed_version:
        return False
    if tuple(node.get("evidence_refs", ())) != tuple(proposal.evidence_refs):
        return False
    relations = tuple(
        relation for relation in candidate.proposed_state.relations
        if relation.source == REFLECTION_NODE and relation.target == proposal.proposal_id
    )
    return len(relations) == 1 and relations[0].relation_type == "proposed_rule"


def commit_endogenous_candidates(
    engine: Engine,
    report: ReflectionReport,
    candidates: Sequence[Candidate],
) -> object:
    """Commit endogenous candidates only after exact proposal provenance validation."""
    proposals = {proposal.proposal_id: proposal for proposal in report.proposals}
    for candidate in candidates:
        proposal_id = next(
            (relation.target for relation in candidate.proposed_state.relations
             if relation.source == REFLECTION_NODE and relation.relation_type == "proposed_rule"),
            None,
        )
        proposal = proposals.get(proposal_id)
        if proposal is None or not candidate_binds_proposal(candidate, proposal):
            raise ValueError("endogenous candidate is not bound to the supplied reflection proposal")
    return engine.step_select(candidates)
