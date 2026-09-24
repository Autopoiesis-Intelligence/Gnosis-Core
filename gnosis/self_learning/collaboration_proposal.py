"""Governed collaboration proposals generated from Self-Learning evidence."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass


def _proposal_id(
    *,
    contract_id: str,
    channel: str,
    title: str,
    objective: str,
    scope: str,
    evidence_refs: tuple[str, ...],
    requested_inputs: tuple[str, ...],
    deliverable_contract_refs: tuple[str, ...],
    publication_target: str,
    revision: str,
) -> str:
    canonical = {
        "contract_id": contract_id,
        "channel": channel,
        "title": title,
        "objective": objective,
        "scope": scope,
        "evidence_refs": evidence_refs,
        "requested_inputs": requested_inputs,
        "deliverable_contract_refs": deliverable_contract_refs,
        "publication_target": publication_target,
        "revision": revision,
    }
    return "sha256:" + hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@dataclass(frozen=True)
class CollaborationProposal:
    proposal_id: str
    contract_id: str
    channel: str
    title: str
    objective: str
    scope: str
    evidence_refs: tuple[str, ...]
    requested_inputs: tuple[str, ...]
    deliverable_contract_refs: tuple[str, ...]
    publication_target: str
    revision: str
    status: str = "PROPOSED"
    authority: str = "proposal-only"

    def __post_init__(self) -> None:
        expected = _proposal_id(
            contract_id=self.contract_id,
            channel=self.channel,
            title=self.title,
            objective=self.objective,
            scope=self.scope,
            evidence_refs=self.evidence_refs,
            requested_inputs=self.requested_inputs,
            deliverable_contract_refs=self.deliverable_contract_refs,
            publication_target=self.publication_target,
            revision=self.revision,
        )
        if self.proposal_id != expected:
            raise ValueError("proposal identity does not match canonical content")
        if self.status != "PROPOSED" or self.authority != "proposal-only":
            raise ValueError("proposal record cannot self-promote")


def generate_collaboration_proposal(
    *,
    contract_id: str,
    channel: str,
    title: str,
    objective: str,
    scope: str,
    evidence_refs: tuple[str, ...],
    requested_inputs: tuple[str, ...],
    deliverable_contract_refs: tuple[str, ...],
    publication_target: str,
    revision: str,
) -> CollaborationProposal:
    if channel not in {"COMMERCIAL", "OPEN"}:
        raise ValueError("channel must be COMMERCIAL or OPEN")
    if not all(
        x.strip() for x in
        (contract_id, title, objective, scope, publication_target, revision)
    ):
        raise ValueError("proposal identity fields are required")
    if not evidence_refs or not requested_inputs or not deliverable_contract_refs:
        raise ValueError("proposal evidence, inputs and deliverable contracts are required")

    pid = _proposal_id(
        contract_id=contract_id,
        channel=channel,
        title=title,
        objective=objective,
        scope=scope,
        evidence_refs=evidence_refs,
        requested_inputs=requested_inputs,
        deliverable_contract_refs=deliverable_contract_refs,
        publication_target=publication_target,
        revision=revision,
    )
    return CollaborationProposal(
        pid, contract_id, channel, title, objective, scope,
        evidence_refs, requested_inputs, deliverable_contract_refs,
        publication_target, revision,
    )


def github_publication_eligible(
    *, proposal: CollaborationProposal, reviewed: bool, authorized: bool
) -> bool:
    return (
        proposal.status == "PROPOSED"
        and proposal.authority == "proposal-only"
        and reviewed
        and authorized
    )


def privacy_safe(
    *, proposal: CollaborationProposal, private_data_refs: tuple[str, ...]
) -> bool:
    return not private_data_refs
