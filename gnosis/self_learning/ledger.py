"""Append-only hash-chained ledger for Self-Learning evidence."""
from __future__ import annotations
import hashlib, json
from dataclasses import asdict, dataclass
from typing import Iterable

@dataclass(frozen=True)
class EvidenceEvent:
    event_id: str
    event_type: str
    subject_id: str
    payload_digest: str
    previous_event_digest: str
    event_digest: str
    provenance: str = "self-learning-evidence-ledger"
    authority: str = "evidence-only"
    def as_dict(self): return asdict(self)

def _digest(payload: dict) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def create_event(event_type: str, subject_id: str, payload: object, previous_event_digest: str = "GENESIS") -> EvidenceEvent:
    if not event_type.strip() or not subject_id.strip(): raise ValueError("event_type and subject_id must be non-empty")
    payload_digest = _digest({"payload": payload})
    canonical = {"event_type":event_type,"subject_id":subject_id,"payload_digest":payload_digest,"previous_event_digest":previous_event_digest,"provenance":"self-learning-evidence-ledger","authority":"evidence-only"}
    event_digest = _digest(canonical)
    event_id = event_digest
    return EvidenceEvent(event_id,event_type,subject_id,payload_digest,previous_event_digest,event_digest)

def verify_chain(events: Iterable[EvidenceEvent]) -> tuple[bool, tuple[str,...]]:
    ordered=list(events); errors=[]; previous="GENESIS"
    for event in ordered:
        expected=create_event(event.event_type,event.subject_id,{"payload_digest":event.payload_digest},previous)
        # Rebuild digest directly from recorded fields to avoid interpreting payload.
        canonical={"event_type":event.event_type,"subject_id":event.subject_id,"payload_digest":event.payload_digest,"previous_event_digest":event.previous_event_digest,"provenance":event.provenance,"authority":event.authority}
        digest=_digest(canonical)
        if event.previous_event_digest != previous: errors.append(f"PREVIOUS_DIGEST_MISMATCH:{event.event_id}")
        if event.event_digest != digest or event.event_id != digest: errors.append(f"EVENT_DIGEST_MISMATCH:{event.event_id}")
        previous=event.event_digest
    return (not errors,tuple(errors))

def chain_digest(events: Iterable[EvidenceEvent]) -> str:
    ordered=list(events)
    return ordered[-1].event_digest if ordered else "GENESIS"
