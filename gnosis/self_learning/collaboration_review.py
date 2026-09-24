"""Governed review records for collaboration proposals (E7.75)."""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass
from .collaboration_proposal import CollaborationProposal, privacy_safe

DECISIONS = {"ACCEPTED", "REJECTED", "DEFERRED", "RETURNED_FOR_REVISION"}

def _digest(payload: dict) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def _review_identity(**fields: object) -> str:
    return _digest(fields)

@dataclass(frozen=True)
class CollaborationReviewRecord:
    review_id: str
    proposal_id: str
    proposal_revision: str
    generator_revision: str
    contract_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    target_scope: str
    privacy_classification: str
    reviewer_id: str
    decision: str
    reason: str
    evidence_id: str
    resulting_revision: str
    status: str
    prior_review_id: str | None = None

    def __post_init__(self) -> None:
        if self.decision not in DECISIONS or self.status != self.decision:
            raise ValueError("invalid review decision/status")
        if not all(x.strip() for x in (self.proposal_id, self.proposal_revision, self.generator_revision, self.target_scope, self.privacy_classification, self.reviewer_id, self.reason, self.evidence_id, self.resulting_revision)):
            raise ValueError("review identity fields are required")
        if not self.contract_refs or not self.evidence_refs:
            raise ValueError("contract and evidence references are required")
        expected = _review_identity(
            proposal_id=self.proposal_id, proposal_revision=self.proposal_revision,
            generator_revision=self.generator_revision, contract_refs=self.contract_refs,
            evidence_refs=self.evidence_refs, target_scope=self.target_scope,
            privacy_classification=self.privacy_classification, reviewer_id=self.reviewer_id,
            decision=self.decision, reason=self.reason, evidence_id=self.evidence_id,
            resulting_revision=self.resulting_revision, status=self.status,
            prior_review_id=self.prior_review_id,
        )
        if self.review_id != expected:
            raise ValueError("review identity does not match canonical content")

def review_collaboration_proposal(
    *, proposal: CollaborationProposal, generator_revision: str,
    contract_refs: tuple[str, ...], reviewer_id: str, review_reason: str,
    evidence_id: str, decision: str, resulting_revision: str,
    target_scope: str | None = None, privacy_classification: str = "SHAREABLE_ABSTRACTION",
    private_data_refs: tuple[str, ...] = (), dependencies_present: bool = True,
    reviewer_authorized: bool = True, stale: bool = False, revoked: bool = False,
    scope_expanding: bool = False, prior_review_id: str | None = None,
) -> CollaborationReviewRecord:
    if decision not in DECISIONS:
        raise ValueError("invalid review decision")
    if not isinstance(proposal, CollaborationProposal):
        raise ValueError("proposal must be a CollaborationProposal")
    if target_scope is None:
        target_scope = proposal.scope
    if not target_scope.strip() or not generator_revision.strip():
        raise ValueError("review scope and generator revision are required")
    if not privacy_safe(proposal=proposal, private_data_refs=private_data_refs):
        raise ValueError("private data is not review-safe")
    if decision == "ACCEPTED" and (not dependencies_present or not reviewer_authorized or stale or revoked or scope_expanding or private_data_refs or privacy_classification != "SHAREABLE_ABSTRACTION"):
        raise ValueError("proposal is not eligible for acceptance")
    if decision == "RETURNED_FOR_REVISION" and resulting_revision == proposal.revision:
        raise ValueError("returned proposal requires a new revision")
    if decision in {"REJECTED", "DEFERRED"} and not review_reason.strip():
        raise ValueError("review reason is required")
    fields = dict(
        proposal_id=proposal.proposal_id, proposal_revision=proposal.revision,
        generator_revision=generator_revision, contract_refs=contract_refs,
        evidence_refs=proposal.evidence_refs, target_scope=target_scope,
        privacy_classification=privacy_classification, reviewer_id=reviewer_id,
        decision=decision, reason=review_reason, evidence_id=evidence_id,
        resulting_revision=resulting_revision, status=decision,
        prior_review_id=prior_review_id,
    )
    return CollaborationReviewRecord(_review_identity(**fields), **fields)

def review_record_valid(*, record: CollaborationReviewRecord, proposal: CollaborationProposal, current_revision: str | None = None) -> bool:
    if record.proposal_id != proposal.proposal_id or record.proposal_revision != proposal.revision:
        return False
    if current_revision is not None and current_revision != record.proposal_revision:
        return False
    try:
        record.__post_init__()
    except ValueError:
        return False
    return True
