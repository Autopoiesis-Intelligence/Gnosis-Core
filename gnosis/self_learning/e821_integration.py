"""E8.21 end-to-end adversarial integration contract."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class E821Trace:
    stages:tuple[str,...]; rejected_tamper_points:tuple[str,...]; final_admitted:bool
REQUIRED=("commercial_evidence","partnership_proposal","collaboration_boundary","contract_generation","transfer_manifest","delivery_receipt","partner_result","provenance_replay","feedback_classification","learning_admission","durable_commit")
TAMPERS=("commercial_evidence","proposal_digest","contract_binding","transfer_manifest","delivery_core_digest","receipt_status","result_binding","provenance_replay","feedback_classification","learning_admission")
def evaluate_e821(*,completed_stages,tamper_points,commit_verified):
    stages=tuple(completed_stages); tamper=tuple(tamper_points)
    if not all(s in stages for s in REQUIRED): raise ValueError("complete E8.21 chain is required")
    unknown=[x for x in tamper if x not in TAMPERS]
    if unknown: raise ValueError("unknown tamper point")
    admitted=commit_verified and not tamper
    return E821Trace(stages,tamper,admitted)

def fail_closed_on_tamper(*,trace): return not trace.final_admitted if trace.rejected_tamper_points else True
