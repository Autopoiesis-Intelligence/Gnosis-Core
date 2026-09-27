"""Deterministic E7.106 candidate inventory and selection boundary.

This module is selection-only. It does not execute candidates, mutate Core,
change progress metrics, or grant execution authority.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


SELECTION_STATES = frozenset(
    {"SELECTED", "RESERVE", "EXCLUDED", "BLOCKED", "INVALIDATED"}
)


@dataclass(frozen=True)
class CandidateInventoryEntry:
    candidate_id: str
    contract_id: str
    contract_revision: str
    current_status: str
    dependency_status: str
    implementation_paths: tuple[str, ...]
    mapped_criteria: tuple[str, ...]
    test_paths: tuple[str, ...]
    runtime_requirements: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    evidence_commits: tuple[str, ...]
    known_gaps: tuple[str, ...]
    trust_boundary_relevance: str
    execution_prerequisites: tuple[str, ...]
    execution_mode: str
    selection_state: str
    selection_rationale: str

    def __post_init__(self) -> None:
        if not self.candidate_id.strip() or not self.contract_id.strip():
            raise ValueError("candidate identity is required")
        if not self.contract_revision.strip():
            raise ValueError("contract revision is required")
        if self.selection_state not in SELECTION_STATES:
            raise ValueError("invalid selection state")
        if self.execution_mode not in {"OBSERVE_ONLY", "MUTATING", "UNKNOWN"}:
            raise ValueError("invalid execution mode")
        if not self.implementation_paths or not self.test_paths:
            raise ValueError("implementation and test paths are required")
        if not self.evidence_ids or not self.evidence_commits:
            raise ValueError("evidence and evidence commit are required")
        if not self.selection_rationale.strip():
            raise ValueError("selection rationale is required")


@dataclass(frozen=True)
class CandidateInventory:
    inventory_id: str
    target_repository: str
    target_ref: str
    target_commit: str
    entries: tuple[CandidateInventoryEntry, ...]

    @staticmethod
    def build(
        *,
        target_repository: str,
        target_ref: str,
        target_commit: str,
        entries: tuple[CandidateInventoryEntry, ...],
    ) -> "CandidateInventory":
        if not target_repository.strip() or not target_ref.strip() or not target_commit.strip():
            raise ValueError("target repository, ref and commit are required")
        if not entries:
            raise ValueError("candidate inventory cannot be empty")
        ids = [entry.candidate_id for entry in entries]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate ids must be unique")
        payload = {
            "target_repository": target_repository,
            "target_ref": target_ref,
            "target_commit": target_commit,
            "entries": [
                {
                    "candidate_id": e.candidate_id,
                    "contract_id": e.contract_id,
                    "contract_revision": e.contract_revision,
                    "selection_state": e.selection_state,
                }
                for e in sorted(entries, key=lambda item: item.candidate_id)
            ],
        }
        inventory_id = "sha256:" + hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return CandidateInventory(
            inventory_id,
            target_repository,
            target_ref,
            target_commit,
            tuple(sorted(entries, key=lambda item: item.candidate_id)),
        )

    def selected(self) -> tuple[CandidateInventoryEntry, ...]:
        return tuple(e for e in self.entries if e.selection_state == "SELECTED")

    def validate_exact_commit(self) -> bool:
        return all(
            commit == self.target_commit
            for entry in self.entries
            for commit in entry.evidence_commits
        )

    def select_observe_only(
        self, *, candidate_id: str
    ) -> "CandidateInventory":
        matches = [e for e in self.entries if e.candidate_id == candidate_id]
        if len(matches) != 1:
            raise ValueError("candidate must exist exactly once")
        candidate = matches[0]
        if candidate.execution_mode != "OBSERVE_ONLY":
            raise ValueError("only observe-only candidates may be selected")
        if not self.validate_exact_commit():
            raise ValueError("evidence is not bound to target commit")
        if any(e.selection_state == "SELECTED" for e in self.entries):
            raise ValueError("inventory already has a selected candidate")

        updated = tuple(
            CandidateInventoryEntry(
                **{
                    **e.__dict__,
                    "selection_state": (
                        "SELECTED"
                        if e.candidate_id == candidate_id
                        else e.selection_state
                    ),
                }
            )
            for e in self.entries
        )
        return CandidateInventory.build(
            target_repository=self.target_repository,
            target_ref=self.target_ref,
            target_commit=self.target_commit,
            entries=updated,
        )


def progress_credit_from_selection(_: CandidateInventory) -> int:
    """Selection never grants verification/progress credit."""
    return 0
