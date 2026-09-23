"""Release gate for a specialized Core build."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class CoreReleaseGate:
    gate_id:str
    build_record_id:str
    receipt_id:str
    required_contracts:tuple[str,...]
    validation_refs:tuple[str,...]
    security_refs:tuple[str,...]
    scope_refs:tuple[str,...]
    release_revision:str
    decision:str="HOLD"

def create_release_gate(*,build_record_id:str,receipt_id:str,required_contracts:tuple[str,...],validation_refs:tuple[str,...],security_refs:tuple[str,...],scope_refs:tuple[str,...],release_revision:str,decision:str="HOLD")->CoreReleaseGate:
    if not all(x.strip() for x in (build_record_id,receipt_id,release_revision)): raise ValueError("release identity is required")
    if not required_contracts or not validation_refs or not security_refs or not scope_refs: raise ValueError("release evidence groups are required")
    if decision not in {"HOLD","RELEASE","REJECT"}: raise ValueError("invalid release decision")
    canonical={"build_record_id":build_record_id,"receipt_id":receipt_id,"required_contracts":required_contracts,"validation_refs":validation_refs,"security_refs":security_refs,"scope_refs":scope_refs,"release_revision":release_revision,"decision":decision}
    gid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return CoreReleaseGate(gid,build_record_id,receipt_id,required_contracts,validation_refs,security_refs,scope_refs,release_revision,decision)

def release_eligible(*,receipt_status:str,build_status:str,gate:CoreReleaseGate)->bool:
    return receipt_status=="PASSED" and build_status=="BUILT" and gate.decision=="RELEASE" and bool(gate.validation_refs) and bool(gate.security_refs) and bool(gate.scope_refs)
