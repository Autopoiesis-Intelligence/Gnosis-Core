"""Deterministic reconstruction of a Self-Learning evidence chain."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .ledger import EvidenceEvent, verify_chain

@dataclass(frozen=True)
class ReplayResult:
    complete: bool
    ordered_event_ids: tuple[str, ...]
    errors: tuple[str, ...]

def replay(events: Iterable[EvidenceEvent], expected_subject_id: str | None = None) -> ReplayResult:
    ordered = tuple(events)
    errors = list(verify_chain(ordered)[1])
    if expected_subject_id is not None:
        errors.extend(
            f"SUBJECT_MISMATCH:{e.event_id}" for e in ordered if e.subject_id != expected_subject_id
        )
    if ordered and ordered[0].previous_event_digest != "GENESIS":
        errors.append("MISSING_GENESIS")
    return ReplayResult(not errors, tuple(e.event_id for e in ordered), tuple(sorted(set(errors))))
