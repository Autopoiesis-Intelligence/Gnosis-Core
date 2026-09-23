"""Protected bridge from accepted Self-Learning integration records to Core mutation proposals."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from .integration import IntegrationRecord

@dataclass(frozen=True)
class CoreMutationProposal:
    mutation_id: str
    integration_id: str
    version_id: str
    target: str
    action: str
    status: str = "PROPOSED"
    authority: str = "core-bridge-proposal-only"

def create_core_mutation_proposal(record: IntegrationRecord) -> CoreMutationProposal:
    if record.status != "PROPOSED":
        raise ValueError("integration record must be PROPOSED before bridge proposal")
    if record.target != "common-self-learning":
        raise ValueError("only common-self-learning target may cross this bridge")
    canonical={"integration_id":record.integration_id,"version_id":record.version_id,"target":record.target,"action":record.action}
    mid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CoreMutationProposal(mid,record.integration_id,record.version_id,record.target,record.action)

def approve_core_mutation(proposal: CoreMutationProposal, *, approver: str) -> CoreMutationProposal:
    if proposal.status != "PROPOSED":
        raise ValueError("only PROPOSED bridge proposals may be approved")
    if not approver.strip():
        raise ValueError("approver is required")
    canonical={"integration_id":proposal.integration_id,"version_id":proposal.version_id,"target":proposal.target,"action":proposal.action}
    expected="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if proposal.mutation_id != expected:
        raise ValueError("proposal identity does not match immutable bridge fields")
    return CoreMutationProposal(proposal.mutation_id,proposal.integration_id,proposal.version_id,proposal.target,proposal.action,"APPROVED",proposal.authority)
