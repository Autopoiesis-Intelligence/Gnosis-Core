"""Deterministic validation gate for Self-Learning contract proposals."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Iterable

from .proposals import ContractProposal


@dataclass(frozen=True)
class ValidationResult:
    proposal_id: str
    valid: bool
    reasons: tuple[str, ...]
    checked_dependencies: tuple[str, ...]
    provenance: str = "self-learning-proposal-validation"

    def as_dict(self) -> dict[str, object]:
        return {
            "proposal_id": self.proposal_id,
            "valid": self.valid,
            "reasons": list(self.reasons),
            "checked_dependencies": list(self.checked_dependencies),
            "provenance": self.provenance,
        }


def validate_proposal(
    proposal: ContractProposal,
    *,
    known_contract_ids: Iterable[str] = (),
    known_findings: Iterable[str] = (),
) -> ValidationResult:
    known_ids = frozenset(known_contract_ids)
    findings = frozenset(known_findings)
    reasons: list[str] = []

    if proposal.status != "PROPOSED":
        reasons.append("INVALID_STATUS")
    if not proposal.proposal_id.startswith("sha256:"):
        reasons.append("INVALID_PROPOSAL_ID")
    if not proposal.finding:
        reasons.append("EMPTY_FINDING")
    if proposal.proposal_type == "UNKNOWN":
        reasons.append("UNKNOWN_FINDING_TYPE")
    if proposal.contract_id != "UNKNOWN" and known_ids and proposal.contract_id not in known_ids:
        reasons.append("CONTRACT_NOT_KNOWN")
    if proposal.finding not in findings and findings:
        reasons.append("SOURCE_FINDING_NOT_PRESENT")

    # Recompute the canonical identity through the public constructor.
    from .proposals import propose_from_finding
    try:
        expected = propose_from_finding(proposal.finding)
        if expected.proposal_id != proposal.proposal_id:
            reasons.append("PROPOSAL_ID_MISMATCH")
    except ValueError:
        reasons.append("UNRECONSTRUCTABLE_FINDING")

    return ValidationResult(
        proposal_id=proposal.proposal_id,
        valid=not reasons,
        reasons=tuple(sorted(set(reasons))),
        checked_dependencies=tuple(sorted(known_ids)),
    )


def validate_proposals(
    proposals: Iterable[ContractProposal],
    *,
    known_contract_ids: Iterable[str] = (),
    known_findings: Iterable[str] = (),
) -> tuple[ValidationResult, ...]:
    return tuple(
        sorted(
            (
                validate_proposal(
                    proposal,
                    known_contract_ids=known_contract_ids,
                    known_findings=known_findings,
                )
                for proposal in proposals
            ),
            key=lambda result: result.proposal_id,
        )
    )


def validation_digest(results: Iterable[ValidationResult]) -> str:
    payload = [result.as_dict() for result in sorted(results, key=lambda x: x.proposal_id)]
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()
