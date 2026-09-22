"""Canonical Core commit boundary for authorized evolution."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping

from .governance import AuthorizationPackage
from .rule_proposal import RuleProposal


@dataclass(frozen=True)
class CommitRecord:
    transition_id: str
    authorization_id: str
    proposal_id: str
    previous_state_id: str
    new_state_id: str
    status: str = "COMMITTED"
    provenance: str = "core-commit"


@dataclass(frozen=True)
class CommitResult:
    record: CommitRecord
    new_state: Mapping[str, Any]


def commit(
    authorization: AuthorizationPackage,
    proposal: RuleProposal,
    *,
    current_state_id: str,
    new_state_id: str,
    new_state: Mapping[str, Any],
) -> CommitResult:
    if authorization.decision != "AUTHORIZED":
        raise ValueError("commit requires explicit authorization")
    if authorization.proposal_id != proposal.proposal_id:
        raise ValueError("authorization/proposal identity mismatch")
    if not current_state_id or not new_state_id:
        raise ValueError("state identity is required")
    if current_state_id == new_state_id:
        raise ValueError("commit must produce a new state identity")
    if not new_state:
        raise ValueError("committed state cannot be empty")
    record = CommitRecord(
        transition_id=f"transition:{authorization.authorization_id.removeprefix('auth:')}:{new_state_id}",
        authorization_id=authorization.authorization_id,
        proposal_id=proposal.proposal_id,
        previous_state_id=current_state_id,
        new_state_id=new_state_id,
    )
    return CommitResult(record, dict(new_state))
