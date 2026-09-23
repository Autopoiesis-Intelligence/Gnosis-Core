"""Evidence receipt for governed partner training execution."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass

@dataclass(frozen=True)
class TrainingExecutionReceipt:
    receipt_id:str
    plan_id:str
    input_revision:str
    executed_revision:str
    result_refs:tuple[str,...]
    test_evidence:tuple[str,...]
    invariant_evidence:tuple[str,...]
    boundary_evidence:tuple[str,...]
    status:str
    created_revision:str

def create_execution_receipt(*,plan_id:str,input_revision:str,executed_revision:str,result_refs:tuple[str,...],test_evidence:tuple[str,...],invariant_evidence:tuple[str,...],boundary_evidence:tuple[str,...],status:str,created_revision:str)->TrainingExecutionReceipt:
    if not all(x.strip() for x in (plan_id,input_revision,executed_revision,status,created_revision)):
        raise ValueError("receipt identity fields are required")
    groups=(result_refs,test_evidence,invariant_evidence,boundary_evidence)
    if any(not g for g in groups): raise ValueError("execution evidence groups are required")
    if status not in {"PASSED","FAILED","PARTIAL"}: raise ValueError("invalid execution status")
    canonical={"plan_id":plan_id,"input_revision":input_revision,"executed_revision":executed_revision,"result_refs":result_refs,"test_evidence":test_evidence,"invariant_evidence":invariant_evidence,"boundary_evidence":boundary_evidence,"status":status,"created_revision":created_revision}
    rid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return TrainingExecutionReceipt(rid,plan_id,input_revision,executed_revision,result_refs,test_evidence,invariant_evidence,boundary_evidence,status,created_revision)

def delivery_eligible(receipt:TrainingExecutionReceipt)->bool:
    return receipt.status=="PASSED" and bool(receipt.test_evidence) and bool(receipt.invariant_evidence) and bool(receipt.boundary_evidence)
