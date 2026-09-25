"""E7.110 deterministic progress reconciliation gate."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

class ReconciliationState(str, Enum):
    RECONCILED="RECONCILED"; BLOCKED="BLOCKED"; CONFLICT="CONFLICT"

@dataclass(frozen=True)
class Metric:
    metric_id: str
    expected: float
    observed: float

@dataclass(frozen=True)
class ReconciliationSnapshot:
    batch_id: str
    acceptance_id: str
    metrics: tuple[Metric,...]
    snapshot_digest: str
    state: ReconciliationState
    reason: str

def reconcile(*, batch_id:str, acceptance_id:str, metrics:tuple[Metric,...]) -> ReconciliationSnapshot:
    if not batch_id or not acceptance_id:
        raise ValueError("identity is required")
    if not metrics:
        return ReconciliationSnapshot(batch_id,acceptance_id,(), "",ReconciliationState.BLOCKED,"no metrics")
    conflicts=tuple(m for m in metrics if m.expected != m.observed)
    payload="|".join(f"{m.metric_id}:{m.expected}:{m.observed}" for m in metrics)
    digest=sha256(payload.encode()).hexdigest()
    if conflicts:
        return ReconciliationSnapshot(batch_id,acceptance_id,metrics,digest,ReconciliationState.CONFLICT,"metric discrepancy")
    return ReconciliationSnapshot(batch_id,acceptance_id,metrics,digest,ReconciliationState.RECONCILED,"all metrics match")
