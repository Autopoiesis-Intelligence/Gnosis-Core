"""Learning outcome commit gate (E8.09)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class LearningCommit:
    commit_id:str; closure_digest:str; feedback_id:str; learning_class:str; evidence_refs:tuple[str,...]; status:str

def commit_learning_outcome(*,closure_verified,closure_digest,feedback_id,learning_class,evidence_refs,status="PROPOSED"):
    if not closure_verified: raise ValueError("provenance closure must be verified")
    if not all(x.strip() for x in (closure_digest,feedback_id)): raise ValueError("commit identity is required")
    if not evidence_refs: raise ValueError("learning commit requires evidence")
    if learning_class not in {"LEARNING_SIGNAL","COUNTEREXAMPLE"}: raise ValueError("only admitted learning classes can commit")
    if status not in {"PROPOSED","COMMITTED","REJECTED"}: raise ValueError("invalid status")
    refs=tuple(sorted(set(evidence_refs)))
    c=dict(closure_digest=closure_digest,feedback_id=feedback_id,learning_class=learning_class,evidence_refs=refs,status=status)
    cid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return LearningCommit(cid,**c)

def is_committed(*,commit): return commit.status=="COMMITTED"
def creates_execution_authority(*,commit): return False
