"""E7.109 criterion-level evidence acceptance gate."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class AcceptanceState(str, Enum):
    ACCEPTED="ACCEPTED"; REJECTED="REJECTED"; BLOCKED="BLOCKED"

@dataclass(frozen=True)
class EvidenceItem:
    criterion_id: str
    evidence_id: str
    expected: str
    observed: str
    passed: bool

@dataclass(frozen=True)
class AcceptanceResult:
    batch_id: str
    execution_record_id: str
    items: tuple[EvidenceItem,...]
    state: AcceptanceState
    reason: str

def accept_evidence(*, batch_id:str, execution_record_id:str, items:tuple[EvidenceItem,...]) -> AcceptanceResult:
    if not batch_id or not execution_record_id:
        raise ValueError("batch and execution record identity are required")
    if not items:
        return AcceptanceResult(batch_id,execution_record_id,items,AcceptanceState.BLOCKED,"no evidence")
    if any(not i.criterion_id or not i.evidence_id for i in items):
        return AcceptanceResult(batch_id,execution_record_id,items,AcceptanceState.REJECTED,"missing criterion/evidence identity")
    if any(i.expected == "" or i.observed == "" for i in items):
        return AcceptanceResult(batch_id,execution_record_id,items,AcceptanceState.REJECTED,"incomplete criterion evidence")
    if not all(i.passed for i in items):
        return AcceptanceResult(batch_id,execution_record_id,items,AcceptanceState.REJECTED,"one or more criteria failed")
    return AcceptanceResult(batch_id,execution_record_id,items,AcceptanceState.ACCEPTED,"all supplied criteria accepted")
