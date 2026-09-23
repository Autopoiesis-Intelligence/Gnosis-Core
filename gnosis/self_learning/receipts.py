"""Evidence receipts for externally authorized contract execution."""
from __future__ import annotations
import hashlib, json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable

from .execution import ExecutionPlan


_ALLOWED = frozenset({"APPLIED", "REJECTED", "FAILED", "NOOP_REJECTED"})


@dataclass(frozen=True)
class MutationReceipt:
    receipt_id: str
    plan_id: str
    review_id: str
    proposal_id: str
    result: str
    target: str
    before_digest: str
    after_digest: str
    executor: str
    authorization_reference: str
    created_at: str
    provenance: str = "self-learning-execution-evidence"
    authority: str = "evidence-only"

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def create_mutation_receipt(
    plan: ExecutionPlan,
    *,
    result: str,
    target: str,
    before_digest: str,
    after_digest: str,
    executor: str,
    authorization_reference: str,
    created_at: str | None = None,
) -> MutationReceipt:
    if plan.status != "PLANNED":
        raise ValueError("only PLANNED execution plans may produce receipts")
    if result not in _ALLOWED:
        raise ValueError(f"unsupported execution result: {result}")
    fields = {
        "target": target, "before_digest": before_digest, "after_digest": after_digest,
        "executor": executor, "authorization_reference": authorization_reference,
    }
    if not all(isinstance(v, str) and v.strip() for v in fields.values()):
        raise ValueError("execution evidence fields must be non-empty")
    if result == "APPLIED" and before_digest == after_digest:
        raise ValueError("APPLIED execution must change the target digest")
    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    canonical = {
        "plan_id": plan.plan_id, "review_id": plan.review_id,
        "proposal_id": plan.proposal_id, "result": result, **fields,
        "created_at": timestamp,
    }
    receipt_id = "sha256:" + hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return MutationReceipt(
        receipt_id=receipt_id, plan_id=plan.plan_id, review_id=plan.review_id,
        proposal_id=plan.proposal_id, result=result, target=target,
        before_digest=before_digest, after_digest=after_digest,
        executor=executor.strip(), authorization_reference=authorization_reference.strip(),
        created_at=timestamp,
    )


def receipt_digest(receipts: Iterable[MutationReceipt]) -> str:
    payload = [x.as_dict() for x in sorted(receipts, key=lambda x: x.receipt_id)]
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
