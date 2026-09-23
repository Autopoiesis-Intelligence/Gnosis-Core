"""Versioned lineage for governed Self-Learning knowledge updates."""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from .knowledge import KnowledgeUpdate

@dataclass(frozen=True)
class KnowledgeVersion:
    version_id: str
    update_id: str
    subject_id: str
    scope: str
    knowledge_digest: str
    parent_version_id: str
    status: str = "RECORDED"
    provenance: str = "self-learning-knowledge-lineage"

def record_version(update: KnowledgeUpdate, *, parent_version_id: str = "GENESIS") -> KnowledgeVersion:
    if update.status != "APPLIED":
        raise ValueError("only APPLIED knowledge updates can be versioned")
    canonical={"update_id":update.update_id,"subject_id":update.subject_id,"scope":update.scope,"knowledge_digest":update.knowledge_digest,"parent_version_id":parent_version_id}
    vid="sha256:"+hashlib.sha256(json.dumps(canonical,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return KnowledgeVersion(vid,update.update_id,update.subject_id,update.scope,update.knowledge_digest,parent_version_id)

def verify_lineage(versions: list[KnowledgeVersion]) -> tuple[bool, tuple[str,...]]:
    errors=[]
    previous="GENESIS"
    for v in versions:
        if v.parent_version_id != previous:
            errors.append(f"PARENT_MISMATCH:{v.version_id}")
        previous=v.version_id
    return (not errors,tuple(errors))
