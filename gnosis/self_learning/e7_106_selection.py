"""E7.106 frozen candidate inventory and selection record.

Selection is an evidence-boundary object. It is not verification and has no
progress side effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json


class SelectionError(ValueError):
    """Raised when an E7.106 selection record is invalid."""


class SelectionStatus(str, Enum):
    SELECTED = "SELECTED"
    RESERVE = "RESERVE"
    EXCLUDED = "EXCLUDED"
    BLOCKED = "BLOCKED"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class CandidateRecord:
    candidate_id: str
    contract_id: str
    revision: str
    current_status: str
    dependency_status: str
    implementation_paths: tuple[str, ...]
    acceptance_criteria_count: int
    mapped_test_count: int
    runtime_proof_requirements: tuple[str, ...]
    existing_evidence_ids: tuple[str, ...]
    evidence_commits: tuple[str, ...]
    known_gaps: tuple[str, ...]
    trust_boundary_relevance: str
    execution_prerequisites: tuple[str, ...]
    selection_status: SelectionStatus
    selection_rationale: str


@dataclass(frozen=True)
class SelectionRecord:
    selection_record_id: str
    batch_id: str
    baseline_id: str
    repository: str
    target_commit_sha: str
    candidates: tuple[CandidateRecord, ...]
    selected_candidate_ids: tuple[str, ...]
    reserve_candidate_ids: tuple[str, ...]
    excluded_candidate_ids: tuple[str, ...]
    blocked_candidate_ids: tuple[str, ...]
    runtime_scenarios: tuple[str, ...]
    evidence_capture_points: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    selection_policy_revision: str
    frozen: bool
    integrity_digest: str


def _sha(value: str) -> None:
    if len(value) != 40 or any(c not in "0123456789abcdef" for c in value.lower()):
        raise SelectionError("target_commit_sha must be a 40-character SHA-1")


def _payload(record: SelectionRecord) -> dict:
    return {
        "selection_record_id": record.selection_record_id,
        "batch_id": record.batch_id,
        "baseline_id": record.baseline_id,
        "repository": record.repository,
        "target_commit_sha": record.target_commit_sha,
        "candidates": [
            {
                "candidate_id": c.candidate_id,
                "contract_id": c.contract_id,
                "revision": c.revision,
                "current_status": c.current_status,
                "dependency_status": c.dependency_status,
                "implementation_paths": list(c.implementation_paths),
                "acceptance_criteria_count": c.acceptance_criteria_count,
                "mapped_test_count": c.mapped_test_count,
                "runtime_proof_requirements": list(c.runtime_proof_requirements),
                "existing_evidence_ids": list(c.existing_evidence_ids),
                "evidence_commits": list(c.evidence_commits),
                "known_gaps": list(c.known_gaps),
                "trust_boundary_relevance": c.trust_boundary_relevance,
                "execution_prerequisites": list(c.execution_prerequisites),
                "selection_status": c.selection_status.value,
                "selection_rationale": c.selection_rationale,
            }
            for c in record.candidates
        ],
        "selected_candidate_ids": list(record.selected_candidate_ids),
        "reserve_candidate_ids": list(record.reserve_candidate_ids),
        "excluded_candidate_ids": list(record.excluded_candidate_ids),
        "blocked_candidate_ids": list(record.blocked_candidate_ids),
        "runtime_scenarios": list(record.runtime_scenarios),
        "evidence_capture_points": list(record.evidence_capture_points),
        "stop_conditions": list(record.stop_conditions),
        "selection_policy_revision": record.selection_policy_revision,
        "frozen": record.frozen,
    }


def _digest(record: SelectionRecord) -> str:
    return sha256(json.dumps(_payload(record), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def create_selection_record(
    *,
    selection_record_id: str,
    batch_id: str,
    baseline_id: str,
    repository: str,
    target_commit_sha: str,
    candidates: tuple[CandidateRecord, ...],
    selected_candidate_ids: tuple[str, ...],
    reserve_candidate_ids: tuple[str, ...],
    excluded_candidate_ids: tuple[str, ...],
    blocked_candidate_ids: tuple[str, ...],
    runtime_scenarios: tuple[str, ...],
    evidence_capture_points: tuple[str, ...],
    stop_conditions: tuple[str, ...],
    selection_policy_revision: str,
) -> SelectionRecord:
    for name, value in (
        ("selection_record_id", selection_record_id),
        ("batch_id", batch_id),
        ("baseline_id", baseline_id),
        ("repository", repository),
        ("selection_policy_revision", selection_policy_revision),
    ):
        if not value or not value.strip():
            raise SelectionError(f"{name} is required")
    _sha(target_commit_sha)

    if not candidates:
        raise SelectionError("candidate inventory is required")
    if not runtime_scenarios or not evidence_capture_points or not stop_conditions:
        raise SelectionError("runtime scope, evidence capture and stop conditions are required")

    ids = tuple(c.candidate_id for c in candidates)
    if len(set(ids)) != len(ids):
        raise SelectionError("candidate_id must be unique")
    candidate_set = set(ids)
    partitions = (
        set(selected_candidate_ids),
        set(reserve_candidate_ids),
        set(excluded_candidate_ids),
        set(blocked_candidate_ids),
    )
    if any(not p <= candidate_set for p in partitions):
        raise SelectionError("selection status references unknown candidate")
    if any(a & b for i, a in enumerate(partitions) for b in partitions[i + 1:]):
        raise SelectionError("candidate selection states must be disjoint")
    if set().union(*partitions) != candidate_set:
        raise SelectionError("every candidate must have an explicit selection state")

    declared = {
        SelectionStatus.SELECTED: set(selected_candidate_ids),
        SelectionStatus.RESERVE: set(reserve_candidate_ids),
        SelectionStatus.EXCLUDED: set(excluded_candidate_ids),
        SelectionStatus.BLOCKED: set(blocked_candidate_ids),
    }
    for candidate in candidates:
        if candidate.selection_status is SelectionStatus.INVALIDATED:
            raise SelectionError("INVALIDATED candidates cannot be part of a frozen selection")
        if candidate.candidate_id not in declared[candidate.selection_status]:
            raise SelectionError("candidate status does not match frozen partition")

    if not selected_candidate_ids:
        raise SelectionError("at least one SELECTED candidate is required")

    record = SelectionRecord(
        selection_record_id=selection_record_id,
        batch_id=batch_id,
        baseline_id=baseline_id,
        repository=repository,
        target_commit_sha=target_commit_sha.lower(),
        candidates=tuple(candidates),
        selected_candidate_ids=tuple(selected_candidate_ids),
        reserve_candidate_ids=tuple(reserve_candidate_ids),
        excluded_candidate_ids=tuple(excluded_candidate_ids),
        blocked_candidate_ids=tuple(blocked_candidate_ids),
        runtime_scenarios=tuple(runtime_scenarios),
        evidence_capture_points=tuple(evidence_capture_points),
        stop_conditions=tuple(stop_conditions),
        selection_policy_revision=selection_policy_revision,
        frozen=True,
        integrity_digest="",
    )
    return SelectionRecord(**{**record.__dict__, "integrity_digest": _digest(record)})


def verify_selection_record(record: SelectionRecord) -> bool:
    return record.frozen and record.integrity_digest == _digest(record)


def assert_selection_frozen(record: SelectionRecord) -> None:
    if not verify_selection_record(record):
        raise SelectionError("selection record is invalid or tampered")


def selection_digest(record: SelectionRecord) -> str:
    assert_selection_frozen(record)
    return record.integrity_digest
