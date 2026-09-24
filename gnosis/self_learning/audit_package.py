"""Deterministic collaboration evidence export boundary (E7.85)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class AuditPackage:
    package_id:str
    contract_id:str
    evidence_refs:tuple[str,...]
    included_artifacts:tuple[str,...]
    redacted_artifacts:tuple[str,...]
    scope:str
    privacy_classification:str
    source_digest:str
    export_revision:str
    status:str
def create_audit_package(*,contract_id,evidence_refs,included_artifacts,redacted_artifacts,scope,privacy_classification,source_digest,export_revision,status="PREPARED"):
    if not all(x.strip() for x in (contract_id,scope,privacy_classification,source_digest,export_revision)): raise ValueError("package identity is required")
    if not evidence_refs: raise ValueError("evidence refs are required")
    if not included_artifacts: raise ValueError("included artifacts are required")
    if status not in {"PREPARED","SEALED","REJECTED"}: raise ValueError("invalid package status")
    c={"contract_id":contract_id,"evidence_refs":evidence_refs,"included_artifacts":included_artifacts,"redacted_artifacts":redacted_artifacts,"scope":scope,"privacy_classification":privacy_classification,"source_digest":source_digest,"export_revision":export_revision,"status":status}
    pid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return AuditPackage(pid,contract_id,evidence_refs,included_artifacts,redacted_artifacts,scope,privacy_classification,source_digest,export_revision,status)
def package_is_auditable(*,package):
    return package.status=="SEALED" and bool(package.evidence_refs) and bool(package.source_digest)
def package_is_public_safe(*,package):
    return package.privacy_classification in {"PUBLIC","SHAREABLE_ABSTRACTION","REDACTED"}
