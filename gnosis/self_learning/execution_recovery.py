"""Crash/restart reconciliation for external execution evidence (E7.78)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .collaboration_evidence import ExecutionEvidence

RecoveryDisposition = Literal["PRESERVE", "RECONCILE_WITH_NEW_EVIDENCE", "REJECT_RETRY"]


@dataclass(frozen=True)
class RecoveryDecision:
    attempt_id: str
    prior_status: str
    prior_reconciliation: str
    disposition: RecoveryDisposition
    reason: str


def reconcile_after_restart(
    evidence: ExecutionEvidence,
    *,
    new_result_status: str | None = None,
    new_target_after_revision: str | None = None,
    new_evidence_present: bool = False,
    retry_authorized: bool = False,
    new_attempt_id: str | None = None,
) -> RecoveryDecision:
    """Recover facts only; never retry or inflate an uncertain result.

    A restart preserves the prior observation. A new successful observation may
    produce a new evidence record through the normal evidence factory, but this
    function itself has no execution authority and cannot mutate the evidence.
    """
    if new_result_status is None and new_target_after_revision is None:
        return RecoveryDecision(
            evidence.execution_attempt_id,
            evidence.result_status,
            evidence.reconciliation_status,
            "PRESERVE",
            "restart without new external evidence",
        )
    if not new_evidence_present:
        return RecoveryDecision(
            evidence.execution_attempt_id,
            evidence.result_status,
            evidence.reconciliation_status,
            "REJECT_RETRY",
            "new result claims require independently captured evidence",
        )
    if retry_authorized and new_attempt_id and new_attempt_id != evidence.execution_attempt_id:
        return RecoveryDecision(
            new_attempt_id,
            evidence.result_status,
            evidence.reconciliation_status,
            "RECONCILE_WITH_NEW_EVIDENCE",
            "new evidence must be persisted under a distinct authorized attempt",
        )
    return RecoveryDecision(
        evidence.execution_attempt_id,
        evidence.result_status,
        evidence.reconciliation_status,
        "REJECT_RETRY",
        "recovery has no authority to retry external actions",
    )
