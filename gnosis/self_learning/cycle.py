"""End-to-end Self-Learning contract cycle harness.

The harness composes existing bounded stages for deterministic integration
testing. It does not bypass governance or mutate Core by itself.
"""
from __future__ import annotations
from dataclasses import dataclass
from .ledger import EvidenceEvent, create_event
from .lifecycle import verify_lifecycle
from .knowledge import propose_knowledge_update, apply_knowledge_update
from .lineage import record_version
from .promotion import PromotionProposal, propose_promotion, decide_promotion
from .integration import IntegrationRecord, create_integration_record

@dataclass(frozen=True)
class CycleResult:
    lifecycle_complete: bool
    knowledge_applied: bool
    version_id: str
    promotion_status: str
    integration_id: str
    promotion: PromotionProposal
    integration: IntegrationRecord

def build_verified_cycle(subject_id: str, *, knowledge: object, reason: str) -> CycleResult:
    events: list[EvidenceEvent] = []
    previous = "GENESIS"
    for i, event_type in enumerate(("DATABASE","FINDING","PROPOSAL","VALIDATION","GOVERNANCE","EXECUTION_PLAN","RECEIPT")):
        event = create_event(event_type, subject_id, {"stage": i}, previous)
        events.append(event)
        previous = event.event_digest

    lifecycle = verify_lifecycle(events, subject_id)
    if not lifecycle.complete:
        raise ValueError("cannot build cycle from incomplete lifecycle")

    update = apply_knowledge_update(propose_knowledge_update(
        subject_id=subject_id,
        evidence_digest=events[-1].event_digest,
        knowledge=knowledge,
        lifecycle=lifecycle,
        scope="common-self-learning",
        shareable=True,
    ))
    version = record_version(update)
    promotion = propose_promotion(
        version,
        evidence_refs=(events[-1].event_digest,),
        reason=reason,
    )
    accepted = decide_promotion(promotion, decision="ACCEPTED", reviewer="cycle-governance")
    integration = create_integration_record(accepted, action="controlled-core-learning-integration")
    return CycleResult(
        True, True, version.version_id, accepted.status, integration.integration_id,
        accepted, integration,
    )
