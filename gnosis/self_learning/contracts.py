"""Governed candidate contract generation for Self-Learning and partner delivery."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from typing import Mapping, Sequence

@dataclass(frozen=True)
class ContractCandidate:
    contract_id: str
    title: str
    objective: str
    scope: str
    source_refs: tuple[str, ...]
    source_revisions: tuple[str, ...]
    generator_context: str
    generated_revision: str
    status: str = "PROPOSED"
    validation_requirements: tuple[str, ...] = ()
    authority: str = "candidate-contract-only"

def generate_candidate_contract(*, title: str, objective: str, scope: str, source_refs: Sequence[str], source_revisions: Sequence[str], generator_context: str, generated_revision: str, validation_requirements: Sequence[str]) -> ContractCandidate:
    fields=[title,objective,scope,generator_context,generated_revision]
    if any(not x.strip() for x in fields):
        raise ValueError("contract identity fields must be non-empty")
    if not source_refs or any(not x.strip() for x in source_refs):
        raise ValueError("source references are required")
    if len(source_refs) != len(source_revisions):
        raise ValueError("source refs and revisions must align")
    if not validation_requirements or any(not x.strip() for x in validation_requirements):
        raise ValueError("validation requirements are required")
    canonical={"title":title,"objective":objective,"scope":scope,"source_refs":list(source_refs),"source_revisions":list(source_revisions),"generator_context":generator_context,"generated_revision":generated_revision,"validation_requirements":list(validation_requirements)}
    cid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return ContractCandidate(cid,title,objective,scope,tuple(source_refs),tuple(source_revisions),generator_context,generated_revision,"PROPOSED",tuple(validation_requirements))

def reject_private_sources(candidate: ContractCandidate, *, authorized_scopes: set[str]) -> ContractCandidate:
    if candidate.scope not in authorized_scopes:
        raise PermissionError("candidate scope is not authorized for contract synthesis")
    return candidate

def serialize_candidate(candidate: ContractCandidate) -> str:
    return json.dumps({
        "contract_id":candidate.contract_id,"title":candidate.title,"objective":candidate.objective,"scope":candidate.scope,
        "source_refs":candidate.source_refs,"source_revisions":candidate.source_revisions,"generator_context":candidate.generator_context,
        "generated_revision":candidate.generated_revision,"status":candidate.status,
        "validation_requirements":candidate.validation_requirements,"authority":candidate.authority,
    },sort_keys=True,separators=(",",":"))
