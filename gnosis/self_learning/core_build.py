"""Provenance record linking a passed training execution to a specialized Core build."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class SpecializedCoreBuildRecord:
    record_id:str
    receipt_id:str
    core_spec_id:str
    source_revisions:tuple[str,...]
    invariant_refs:tuple[str,...]
    validation_refs:tuple[str,...]
    build_revision:str
    status:str="PROPOSED"

def create_build_record(*,receipt_id:str,core_spec_id:str,source_revisions:tuple[str,...],invariant_refs:tuple[str,...],validation_refs:tuple[str,...],build_revision:str,status:str="PROPOSED")->SpecializedCoreBuildRecord:
    if not all(x.strip() for x in (receipt_id,core_spec_id,build_revision)): raise ValueError("build identity fields are required")
    if not source_revisions or not invariant_refs or not validation_refs: raise ValueError("build provenance and validation refs are required")
    if status not in {"PROPOSED","BUILT","REJECTED"}: raise ValueError("invalid build status")
    canonical={"receipt_id":receipt_id,"core_spec_id":core_spec_id,"source_revisions":source_revisions,"invariant_refs":invariant_refs,"validation_refs":validation_refs,"build_revision":build_revision,"status":status}
    rid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return SpecializedCoreBuildRecord(rid,receipt_id,core_spec_id,source_revisions,invariant_refs,validation_refs,build_revision,status)

def build_eligible(*,receipt_status:str,record:SpecializedCoreBuildRecord)->bool:
    return receipt_status=="PASSED" and record.status=="BUILT" and bool(record.validation_refs) and bool(record.invariant_refs)


def validate_build_record_identity(record: SpecializedCoreBuildRecord) -> SpecializedCoreBuildRecord:
    canonical={"receipt_id":record.receipt_id,"core_spec_id":record.core_spec_id,"source_revisions":record.source_revisions,"invariant_refs":record.invariant_refs,"validation_refs":record.validation_refs,"build_revision":record.build_revision,"status":record.status}
    expected="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if record.record_id != expected:
        raise ValueError("build record identity does not match immutable fields")
    return record

def validate_build_receipt_binding(record: SpecializedCoreBuildRecord, *, expected_receipt_id: str) -> SpecializedCoreBuildRecord:
    validate_build_record_identity(record)
    if record.receipt_id != expected_receipt_id:
        raise PermissionError("build receipt identity mismatch")
    return record
