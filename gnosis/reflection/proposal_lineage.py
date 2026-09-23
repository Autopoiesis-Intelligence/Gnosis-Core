"""Evidence-linked evolution of reflection proposals.

This module never changes Core and never activates a proposal. It records how a
new proposal relates to earlier proposals addressing the same finding.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class ProposalEvolution:
    evolution_id: str
    finding_id: str
    parent_proposal_id: str | None
    relation: str
    rationale: str
    evidence_refs: tuple[str, ...]
    current_proposal_id: str | None = None
    status: str = "PROPOSED"


def proposal_evolution_id(evolution: ProposalEvolution) -> str:
    payload = asdict(evolution)
    payload.pop("evolution_id", None)
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "proposal-evolution:" + hashlib.sha256(raw).hexdigest()[:24]


def evolve_proposal(
    *,
    finding_id: str,
    current_proposal_id: str,
    prior_proposals: Iterable[Mapping[str, object]],
    evidence_refs: tuple[str, ...] = (),
) -> ProposalEvolution:
    """Create a lineage record when prior proposals did not settle a finding."""
    candidates = [
        p for p in prior_proposals
        if str(p.get("finding_id", "")) == finding_id
    ]
    parent = candidates[-1] if candidates else None
    parent_id = str(parent.get("proposal_id")) if parent and parent.get("proposal_id") else None

    if parent is None:
        relation = "INITIAL"
        rationale = "No earlier proposal for this finding is available."
    else:
        status = str(parent.get("status", "PROPOSED"))
        if status == "REJECTED":
            relation = "REFINEMENT_AFTER_REJECTION"
            rationale = "A prior proposal was rejected; the new proposal must narrow or revise the hypothesis."
        elif status == "SUPERSEDED":
            relation = "REFINEMENT_AFTER_SUPERSESSION"
            rationale = "A prior proposal was superseded; the new proposal continues the finding lineage."
        elif status == "ACCEPTED":
            relation = "FOLLOWUP_AFTER_ACCEPTANCE"
            rationale = "The finding has an accepted proposal; this is a separately identified follow-up rather than silent replacement."
        else:
            relation = "REVISION_OF_UNRESOLVED"
            rationale = "A prior proposal remains unresolved; the new proposal must provide additional evidence or a materially revised hypothesis."

    evolution = ProposalEvolution(
        evolution_id="",
        finding_id=finding_id,
        parent_proposal_id=parent_id,
        relation=relation,
        rationale=rationale,
        evidence_refs=evidence_refs,
        current_proposal_id=current_proposal_id,
    )
    return ProposalEvolution(
        evolution_id=proposal_evolution_id(evolution),
        finding_id=evolution.finding_id,
        parent_proposal_id=evolution.parent_proposal_id,
        relation=evolution.relation,
        rationale=evolution.rationale,
        evidence_refs=evolution.evidence_refs,
        current_proposal_id=evolution.current_proposal_id,
        status=evolution.status,
    )
