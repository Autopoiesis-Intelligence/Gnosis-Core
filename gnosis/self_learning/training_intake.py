"""Governed partner training intake specification."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class TrainingIntake:
    intake_id:str
    partner_id:str
    contract_id:str
    domain:str
    knowledge_scope:str
    source_refs:tuple[str,...]
    constraints:tuple[str,...]
    requested_revision:str
    status:str="PROPOSED"

def create_training_intake(*,partner_id:str,contract_id:str,domain:str,knowledge_scope:str,source_refs:tuple[str,...],constraints:tuple[str,...],requested_revision:str)->TrainingIntake:
    if not all(x.strip() for x in (partner_id,contract_id,domain,knowledge_scope,requested_revision)):
        raise ValueError("training intake identity fields are required")
    if not source_refs or not constraints: raise ValueError("training sources and constraints are required")
    canonical={"partner_id":partner_id,"contract_id":contract_id,"domain":domain,"knowledge_scope":knowledge_scope,"source_refs":source_refs,"constraints":constraints,"requested_revision":requested_revision}
    iid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return TrainingIntake(iid,partner_id,contract_id,domain,knowledge_scope,source_refs,constraints,requested_revision)

def authorize_training_intake(intake:TrainingIntake,*,allowed_partner_ids:set[str],allowed_scopes:set[str])->TrainingIntake:
    canonical={"partner_id":intake.partner_id,"contract_id":intake.contract_id,"domain":intake.domain,"knowledge_scope":intake.knowledge_scope,"source_refs":intake.source_refs,"constraints":intake.constraints,"requested_revision":intake.requested_revision}
    expected="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if intake.intake_id != expected:
        raise ValueError("training intake identity does not match immutable fields")
    if intake.partner_id not in allowed_partner_ids: raise PermissionError("partner is not authorized")
    if intake.knowledge_scope not in allowed_scopes: raise PermissionError("knowledge scope is not authorized")
    return intake
