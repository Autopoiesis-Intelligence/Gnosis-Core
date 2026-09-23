"""End-to-end integrity checks for a Self-Learning contract lifecycle."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .ledger import EvidenceEvent, verify_chain
from .replay import replay

REQUIRED = ("DATABASE","FINDING","PROPOSAL","VALIDATION","GOVERNANCE","EXECUTION_PLAN","RECEIPT")

@dataclass(frozen=True)
class LifecycleResult:
    complete: bool
    missing: tuple[str,...]
    errors: tuple[str,...]

def verify_lifecycle(events: Iterable[EvidenceEvent], subject_id: str) -> LifecycleResult:
    ordered=tuple(events)
    errors=list(verify_chain(ordered)[1])
    errors.extend(replay(ordered, expected_subject_id=subject_id).errors)
    types={e.event_type for e in ordered}
    counts={stage: sum(1 for e in ordered if e.event_type == stage) for stage in REQUIRED}
    duplicates=tuple(stage for stage in REQUIRED if counts[stage] > 1)
    if duplicates: errors.extend(f"DUPLICATE_STAGE:{stage}" for stage in duplicates)
    missing=tuple(x for x in REQUIRED if x not in types)
    if missing: errors.append("MISSING_STAGES:"+",".join(missing))
    positions={e.event_type:i for i,e in enumerate(ordered)}
    for a,b in zip(REQUIRED,REQUIRED[1:]):
        if a in positions and b in positions and positions[a] >= positions[b]:
            errors.append(f"ORDER_VIOLATION:{a}>{b}")
    return LifecycleResult(not errors, missing, tuple(sorted(set(errors))))
