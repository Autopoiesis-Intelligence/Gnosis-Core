"""Governed knowledge-state updates derived from verified learning lifecycles."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from .lifecycle import LifecycleResult

@dataclass(frozen=True)
class KnowledgeUpdate:
    update_id: str
    subject_id: str
    evidence_digest: str
    knowledge_digest: str
    scope: str
    status: str = "PROPOSED"
    authority: str = "knowledge-update-only"

def propose_knowledge_update(*, subject_id: str, evidence_digest: str, knowledge: object, lifecycle: LifecycleResult, scope: str, shareable: bool) -> KnowledgeUpdate:
    if not lifecycle.complete:
        raise ValueError("knowledge updates require a complete verified lifecycle")
    if subject_id != lifecycle.subject_id:
        raise ValueError("knowledge update subject does not match verified lifecycle subject")
    if not shareable:
        raise PermissionError("non-shareable evidence cannot enter common knowledge")
    if not subject_id.strip() or not evidence_digest.strip() or not scope.strip():
        raise ValueError("subject_id, evidence_digest and scope must be non-empty")
    kd="sha256:"+hashlib.sha256(json.dumps(knowledge,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    uid="sha256:"+hashlib.sha256(json.dumps({"subject_id":subject_id,"evidence_digest":evidence_digest,"knowledge_digest":kd,"scope":scope},sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return KnowledgeUpdate(uid,subject_id,evidence_digest,kd,scope)

def apply_knowledge_update(update: KnowledgeUpdate) -> KnowledgeUpdate:
    if update.status != "PROPOSED":
        raise ValueError("only PROPOSED knowledge updates may be applied")
    return KnowledgeUpdate(update.update_id,update.subject_id,update.evidence_digest,update.knowledge_digest,update.scope,"APPLIED",update.authority)
