"""Lifecycle retention and controlled data disposal boundary (E7.84)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
POLICIES={"RETAIN","ARCHIVE","DISPOSE","LEGAL_HOLD","MINIMIZE"}
STATUSES={"PROPOSED","APPROVED","HELD","EXECUTED","BLOCKED"}
@dataclass(frozen=True)
class EvidenceRetentionDecision:
    decision_id:str
    contract_id:str
    evidence_refs:tuple[str,...]
    policy:str
    retention_basis:str
    disposal_scope:str
    privacy_classification:str
    status:str
def create_retention_decision(*,contract_id,evidence_refs,policy,retention_basis,disposal_scope,privacy_classification,status="PROPOSED"):
    if policy not in POLICIES: raise ValueError("invalid retention policy")
    if status not in STATUSES: raise ValueError("invalid retention status")
    if not contract_id.strip() or not retention_basis.strip() or not disposal_scope.strip() or not privacy_classification.strip(): raise ValueError("retention identity is required")
    if not evidence_refs: raise ValueError("evidence refs are required")
    if policy=="DISPOSE" and status=="EXECUTED" and "MINIMIZE" not in retention_basis.upper(): raise ValueError("executed disposal requires minimization basis")
    c={"contract_id":contract_id,"evidence_refs":evidence_refs,"policy":policy,"retention_basis":retention_basis,"disposal_scope":disposal_scope,"privacy_classification":privacy_classification,"status":status}
    did="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return EvidenceRetentionDecision(did,contract_id,evidence_refs,policy,retention_basis,disposal_scope,privacy_classification,status)
def may_dispose(*,decision):
    return decision.policy=="DISPOSE" and decision.status=="EXECUTED" and bool(decision.evidence_refs) and "MINIMIZE" in decision.retention_basis.upper()
def preserves_audit_reference(*,decision): return bool(decision.evidence_refs)