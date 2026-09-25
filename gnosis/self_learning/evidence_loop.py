"""Immutable evidence record for one autonomous learning/evolution cycle.

This module records causal identity only. It does not grant execution authority,
perform mutations, or decide whether a candidate is acceptable.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class CycleEvidence:
    evidence_id: str
    cycle_id: str
    parent_cycle_id: str | None
    input_digest: str
    initial_state_digest: str
    candidate_id: str
    execution_id: str
    verification_id: str
    outcome: str
    resulting_state_digest: str
    commit_id: str | None
    learning_id: str | None
    evidence_refs: tuple[str, ...]
    evidence_digest: str


def record_cycle_evidence(
    *,
    cycle_id: str,
    parent_cycle_id: str | None,
    input_digest: str,
    initial_state_digest: str,
    candidate_id: str,
    execution_id: str,
    verification_id: str,
    outcome: str,
    resulting_state_digest: str,
    commit_id: str | None,
    learning_id: str | None,
    evidence_refs: tuple[str, ...] | list[str],
) -> CycleEvidence:
    required = (
        cycle_id,
        input_digest,
        initial_state_digest,
        candidate_id,
        execution_id,
        verification_id,
        outcome,
        resulting_state_digest,
    )
    if not all(value and value.strip() for value in required):
        raise ValueError("complete cycle evidence identity is required")
    if outcome not in {"ACCEPTED", "REJECTED", "INCONCLUSIVE"}:
        raise ValueError("invalid cycle outcome")
    if outcome == "ACCEPTED" and not commit_id:
        raise ValueError("accepted cycle requires commit identity")
    if outcome != "ACCEPTED" and commit_id is not None:
        raise ValueError("rejected or inconclusive cycle cannot have a commit")
    if not evidence_refs:
        raise ValueError("cycle evidence requires evidence references")

    refs = tuple(sorted(set(evidence_refs)))
    canonical = {
        "cycle_id": cycle_id,
        "parent_cycle_id": parent_cycle_id,
        "input_digest": input_digest,
        "initial_state_digest": initial_state_digest,
        "candidate_id": candidate_id,
        "execution_id": execution_id,
        "verification_id": verification_id,
        "outcome": outcome,
        "resulting_state_digest": resulting_state_digest,
        "commit_id": commit_id,
        "learning_id": learning_id,
        "evidence_refs": refs,
    }
    digest = "sha256:" + hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    evidence_id = "cycle-evidence:" + digest.removeprefix("sha256:")

    return CycleEvidence(
        evidence_id=evidence_id,
        **canonical,
        evidence_digest=digest,
    )


def preserves_causal_binding(
    *,
    evidence: CycleEvidence,
    cycle_id: str,
    initial_state_digest: str,
) -> bool:
    return (
        evidence.cycle_id == cycle_id
        and evidence.initial_state_digest == initial_state_digest
        and bool(evidence.candidate_id)
        and bool(evidence.execution_id)
        and bool(evidence.verification_id)
    )


def is_no_op(*, evidence: CycleEvidence) -> bool:
    return evidence.initial_state_digest == evidence.resulting_state_digest


def influences_next_cycle(*, evidence: CycleEvidence) -> bool:
    return (
        evidence.learning_id is not None
        and bool(evidence.evidence_refs)
        and evidence.outcome in {"ACCEPTED", "REJECTED"}
    )


def creates_execution_authority(*, evidence: CycleEvidence) -> bool:
    return False
