"""Machine-readable partner training execution plan."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class TrainingPlan:
    plan_id:str
    intake_id:str
    allowed_data_refs:tuple[str,...]
    learning_objectives:tuple[str,...]
    invariant_refs:tuple[str,...]
    test_requirements:tuple[str,...]
    acceptance_criteria:tuple[str,...]
    revision:str
    status:str="PROPOSED"

def create_training_plan(*,intake_id:str,allowed_data_refs:tuple[str,...],learning_objectives:tuple[str,...],invariant_refs:tuple[str,...],test_requirements:tuple[str,...],acceptance_criteria:tuple[str,...],revision:str)->TrainingPlan:
    fields=(intake_id,revision)
    if any(not x.strip() for x in fields): raise ValueError("plan identity is required")
    groups=(allowed_data_refs,learning_objectives,invariant_refs,test_requirements,acceptance_criteria)
    if any(not g for g in groups): raise ValueError("all training plan groups are required")
    canonical={"intake_id":intake_id,"allowed_data_refs":allowed_data_refs,"learning_objectives":learning_objectives,"invariant_refs":invariant_refs,"test_requirements":test_requirements,"acceptance_criteria":acceptance_criteria,"revision":revision}
    pid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return TrainingPlan(pid,intake_id,allowed_data_refs,learning_objectives,invariant_refs,test_requirements,acceptance_criteria,revision)

def validate_plan_scope(plan:TrainingPlan,*,allowed_data_refs:set[str])->TrainingPlan:
    canonical={"intake_id":plan.intake_id,"allowed_data_refs":plan.allowed_data_refs,"learning_objectives":plan.learning_objectives,"invariant_refs":plan.invariant_refs,"test_requirements":plan.test_requirements,"acceptance_criteria":plan.acceptance_criteria,"revision":plan.revision}
    expected="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if plan.plan_id != expected:
        raise ValueError("training plan identity does not match immutable fields")
    if not set(plan.allowed_data_refs).issubset(allowed_data_refs):
        raise PermissionError("training plan requests data outside authorized scope")
    return plan
