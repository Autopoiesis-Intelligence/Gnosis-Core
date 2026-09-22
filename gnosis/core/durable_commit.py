"""Durable adapter connecting Core authorization to existing persistence."""
from __future__ import annotations

import sqlite3

from .governance import AuthorizationPackage
from .rule_proposal import RuleProposal
from .commit import CommitRecord
from gnosis.core import Candidate, Instance, TransitionRecord
from gnosis.storage.repositories import persist_transition


def persist_authorized_transition(
    conn: sqlite3.Connection,
    authorization: AuthorizationPackage,
    proposal: RuleProposal,
    instance: Instance,
    candidate: Candidate,
    transition: TransitionRecord,
    *,
    actor: str,
    failure_at: str | None = None,
) -> CommitRecord:
    if authorization.decision != "AUTHORIZED":
        raise ValueError("durable commit requires explicit authorization")
    if authorization.proposal_id != proposal.proposal_id:
        raise ValueError("authorization/proposal identity mismatch")
    if candidate.parent_state_id != transition.from_state_id:
        raise ValueError("candidate/transition source mismatch")
    if candidate.proposed_state.state_id != transition.to_state_id:
        raise ValueError("candidate/transition target mismatch")
    if instance.engine.state.state_id != transition.from_state_id:
        raise ValueError("stale instance head")
    if not transition.accepted:
        raise ValueError("durable evolution commit requires accepted transition")

    persist_transition(
        conn,
        instance,
        candidate,
        transition,
        actor=actor,
        failure_at=failure_at,
    )
    return CommitRecord(
        transition_id=transition_id_for(transition),
        authorization_id=authorization.authorization_id,
        proposal_id=proposal.proposal_id,
        previous_state_id=transition.from_state_id,
        new_state_id=transition.to_state_id,
    )


def transition_id_for(record: TransitionRecord) -> str:
    from gnosis.storage.repositories import transition_id
    return transition_id(record)
