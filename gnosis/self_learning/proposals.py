"""Deterministic bounded proposals from Self-Learning findings."""
from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class ContractProposal:
    proposal_id: str
    contract_id: str
    proposal_type: str
    finding: str
    rationale: str
    proposed_change: str
    provenance: str = "self-learning-proposal-engine"
    status: str = "PROPOSED"
    def as_dict(self) -> dict[str, str]:
        return asdict(self)

def _classify(finding: str) -> str:
    for kind in ("REGISTRY_MISSING","ARTIFACT_MISSING","STATUS_DRIFT","DEPENDENCY_MISSING"):
        if finding.startswith(kind + ":"):
            return kind
    return "UNKNOWN"

def _contract_id(finding: str) -> str:
    parts = finding.split(":")
    return parts[1] if len(parts) > 1 else "UNKNOWN"

def propose_from_finding(finding: str) -> ContractProposal:
    if not isinstance(finding, str) or not finding.strip():
        raise ValueError("finding must be a non-empty string")
    finding = finding.strip()
    kind = _classify(finding)
    contract_id = _contract_id(finding)
    rationale = {
        "REGISTRY_MISSING": "Contract artifact exists without a registry entry.",
        "ARTIFACT_MISSING": "Registry contains a contract without a matching artifact.",
        "STATUS_DRIFT": "Registry and contract artifact report different statuses.",
        "DEPENDENCY_MISSING": "Contract references a missing dependency.",
        "UNKNOWN": "Finding requires explicit human/governance interpretation.",
    }[kind]
    change = {
        "REGISTRY_MISSING": f"Add or reconcile registry entry for {contract_id}.",
        "ARTIFACT_MISSING": f"Restore, retire, or reconcile artifact for {contract_id}.",
        "STATUS_DRIFT": f"Review and reconcile status for {contract_id}.",
        "DEPENDENCY_MISSING": f"Resolve or explicitly retire dependency referenced by {contract_id}.",
        "UNKNOWN": "Review finding and define an explicit governed change.",
    }[kind]
    canonical = {"contract_id":contract_id,"proposal_type":kind,"finding":finding,"rationale":rationale,"proposed_change":change}
    proposal_id = "sha256:" + hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return ContractProposal(proposal_id,contract_id,kind,finding,rationale,change)

def proposals_from_findings(findings: list[str] | tuple[str, ...]) -> tuple[ContractProposal, ...]:
    return tuple(sorted((propose_from_finding(x) for x in sorted(set(findings))), key=lambda p:p.proposal_id))
