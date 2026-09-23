"""Partner-specific Core delivery specification."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass

@dataclass(frozen=True)
class SpecializedCoreSpec:
    core_id: str
    base_core_contract: str
    domain: str
    knowledge_scope: str
    constraint_refs: tuple[str, ...]
    evolution_contract_refs: tuple[str, ...]
    delivery_revision: str
    status: str = "PROPOSED"

def create_specialized_core_spec(*, base_core_contract: str, domain: str, knowledge_scope: str, constraint_refs: tuple[str,...], evolution_contract_refs: tuple[str,...], delivery_revision: str) -> SpecializedCoreSpec:
    if not all(x.strip() for x in (base_core_contract,domain,knowledge_scope,delivery_revision)):
        raise ValueError("core specification identity fields are required")
    if not constraint_refs or not evolution_contract_refs:
        raise ValueError("constraints and evolution contracts are required")
    canonical={"base_core_contract":base_core_contract,"domain":domain,"knowledge_scope":knowledge_scope,"constraint_refs":constraint_refs,"evolution_contract_refs":evolution_contract_refs,"delivery_revision":delivery_revision}
    cid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return SpecializedCoreSpec(cid,base_core_contract,domain,knowledge_scope,constraint_refs,evolution_contract_refs,delivery_revision)

def validate_delivery_scope(spec: SpecializedCoreSpec, *, allowed_domains: set[str]) -> SpecializedCoreSpec:
    if spec.domain not in allowed_domains:
        raise PermissionError("specialized Core domain is outside authorized delivery scope")
    return spec
