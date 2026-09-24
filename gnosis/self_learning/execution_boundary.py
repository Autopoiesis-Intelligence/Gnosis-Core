"""Execution boundary for accepted contracts (E8.05)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class ExecutionAuthorization:
    authorization_id:str; contract_id:str; contract_digest:str; scope:str; task_ref:str; expected_result:str; status:str

def authorize_execution(*,contract_id,contract_digest,scope,task_ref,expected_result,accepted=True):
    if not all(x.strip() for x in (contract_id,contract_digest,scope,task_ref,expected_result)): raise ValueError("complete execution boundary fields are required")
    if not accepted: raise ValueError("contract is not accepted")
    c=dict(contract_id=contract_id,contract_digest=contract_digest,scope=scope.strip(),task_ref=task_ref.strip(),expected_result=expected_result.strip(),status="AUTHORIZED")
    aid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return ExecutionAuthorization(aid,**c)

def scope_matches(*,authorization,scope): return authorization.scope==scope
def may_execute(*,authorization,contract_id,contract_digest,scope): return authorization.status=="AUTHORIZED" and authorization.contract_id==contract_id and authorization.contract_digest==contract_digest and authorization.scope==scope
def creates_new_contract(*,authorization): return False
