"""Deterministic shadow evaluation boundary for candidate contracts (E7.92)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class ShadowEvaluation:
    evaluation_id:str; candidate_id:str; base_state_digest:str; projected_state_digest:str; invariant_results:tuple[str,...]; regression_results:tuple[str,...]; evidence_refs:tuple[str,...]; evaluator_revision:str; outcome:str
def evaluate_candidate(*,candidate_id,base_state_digest,projected_state_digest,invariant_results,regression_results,evidence_refs,evaluator_revision="r1",outcome="PENDING"):
    if not all(x.strip() for x in (candidate_id,base_state_digest,projected_state_digest,evaluator_revision)): raise ValueError("evaluation identity is required")
    if not invariant_results or not regression_results or not evidence_refs: raise ValueError("evaluation evidence is required")
    if outcome not in {"PENDING","PASS","FAIL","BLOCKED"}: raise ValueError("invalid evaluation outcome")
    inv=tuple(sorted(set(invariant_results))); reg=tuple(sorted(set(regression_results))); ev=tuple(sorted(set(evidence_refs)))
    c={"candidate_id":candidate_id,"base_state_digest":base_state_digest,"projected_state_digest":projected_state_digest,"invariant_results":inv,"regression_results":reg,"evidence_refs":ev,"evaluator_revision":evaluator_revision,"outcome":outcome}
    eid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return ShadowEvaluation(eid,candidate_id,base_state_digest,projected_state_digest,inv,reg,ev,evaluator_revision,outcome)
def shadow_passes(*,evaluation):
    return evaluation.outcome=="PASS" and all(x.startswith("PASS:") for x in evaluation.invariant_results) and all(x.startswith("PASS:") for x in evaluation.regression_results) and evaluation.base_state_digest!=evaluation.projected_state_digest
def may_enter_governance(*,evaluation): return shadow_passes(evaluation=evaluation)
def creates_execution_authority(*,evaluation): return False
