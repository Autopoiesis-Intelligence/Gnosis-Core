"""Governed collaboration proposals generated from Self-Learning evidence."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class CollaborationProposal:
    proposal_id:str
    contract_id:str
    channel:str
    title:str
    objective:str
    scope:str
    evidence_refs:tuple[str,...]
    requested_inputs:tuple[str,...]
    deliverable_contract_refs:tuple[str,...]
    publication_target:str
    revision:str
    status:str="PROPOSED"
    authority:str="proposal-only"

def generate_collaboration_proposal(*,contract_id:str,channel:str,title:str,objective:str,scope:str,evidence_refs:tuple[str,...],requested_inputs:tuple[str,...],deliverable_contract_refs:tuple[str,...],publication_target:str,revision:str)->CollaborationProposal:
    if channel not in {"COMMERCIAL","OPEN"}: raise ValueError("channel must be COMMERCIAL or OPEN")
    if not all(x.strip() for x in (contract_id,title,objective,scope,publication_target,revision)): raise ValueError("proposal identity fields are required")
    if not evidence_refs or not requested_inputs or not deliverable_contract_refs: raise ValueError("proposal evidence, inputs and deliverable contracts are required")
    canonical={"contract_id":contract_id,"channel":channel,"title":title,"objective":objective,"scope":scope,"evidence_refs":evidence_refs,"requested_inputs":requested_inputs,"deliverable_contract_refs":deliverable_contract_refs,"publication_target":publication_target,"revision":revision}
    pid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CollaborationProposal(pid,contract_id,channel,title,objective,scope,evidence_refs,requested_inputs,deliverable_contract_refs,publication_target,revision)

def github_publication_eligible(*,proposal:CollaborationProposal,reviewed:bool,authorized:bool)->bool:
    return proposal.status=="PROPOSED" and proposal.authority=="proposal-only" and reviewed and authorized

def privacy_safe(*,proposal:CollaborationProposal,private_data_refs:tuple[str,...])->bool:
    return not private_data_refs
