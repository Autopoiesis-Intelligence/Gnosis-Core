"""Validation gate for partner feedback before common Self-Learning promotion."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class FeedbackValidation:
    validation_id:str
    proposal_id:str
    privacy_check_refs:tuple[str,...]
    generalization_check_refs:tuple[str,...]
    scope_check_refs:tuple[str,...]
    exclusion_check_refs:tuple[str,...]
    validation_revision:str
    decision:str="HOLD"

def create_feedback_validation(*,proposal_id:str,privacy_check_refs:tuple[str,...],generalization_check_refs:tuple[str,...],scope_check_refs:tuple[str,...],exclusion_check_refs:tuple[str,...],validation_revision:str,decision:str="HOLD")->FeedbackValidation:
    if not all(x.strip() for x in (proposal_id,validation_revision)): raise ValueError("validation identity is required")
    groups=(privacy_check_refs,generalization_check_refs,scope_check_refs,exclusion_check_refs)
    if any(not g for g in groups): raise ValueError("all validation evidence groups are required")
    if decision not in {"HOLD","PROMOTE","REJECT"}: raise ValueError("invalid validation decision")
    canonical={"proposal_id":proposal_id,"privacy_check_refs":privacy_check_refs,"generalization_check_refs":generalization_check_refs,"scope_check_refs":scope_check_refs,"exclusion_check_refs":exclusion_check_refs,"validation_revision":validation_revision,"decision":decision}
    vid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return FeedbackValidation(vid,proposal_id,privacy_check_refs,generalization_check_refs,scope_check_refs,exclusion_check_refs,validation_revision,decision)

def promotion_valid(*,proposal_eligible:bool,validation:FeedbackValidation)->bool:
    return proposal_eligible and validation.decision=="PROMOTE" and bool(validation.privacy_check_refs) and bool(validation.generalization_check_refs) and bool(validation.scope_check_refs) and bool(validation.exclusion_check_refs)


def validate_feedback_validation_binding(validation: FeedbackValidation, *, expected_proposal_id: str) -> FeedbackValidation:
    canonical={"proposal_id":validation.proposal_id,"privacy_check_refs":validation.privacy_check_refs,"generalization_check_refs":validation.generalization_check_refs,"scope_check_refs":validation.scope_check_refs,"exclusion_check_refs":validation.exclusion_check_refs,"validation_revision":validation.validation_revision,"decision":validation.decision}
    expected_id="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if validation.validation_id != expected_id:
        raise ValueError("feedback validation identity does not match immutable fields")
    if validation.proposal_id != expected_proposal_id:
        raise PermissionError("feedback validation proposal binding mismatch")
    return validation
