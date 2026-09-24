"""External audit challenge, dispute, and evidence reconciliation boundary (E7.87)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
STATUSES={"OPEN","SUBSTANTIATED","REJECTED","RESOLVED","ESCALATED"}
@dataclass(frozen=True)
class AuditChallenge:
    challenge_id:str; attestation_id:str; package_id:str; challenger_id:str; challenged_digest:str; claim:str; evidence_refs:tuple[str,...]; status:str; resolution_refs:tuple[str,...]
def create_challenge(*,attestation_id,package_id,challenger_id,challenged_digest,claim,evidence_refs,status="OPEN",resolution_refs=()):
    if status not in STATUSES: raise ValueError("invalid challenge status")
    if not all(x.strip() for x in (attestation_id,package_id,challenger_id,challenged_digest,claim)): raise ValueError("challenge identity is required")
    if not evidence_refs: raise ValueError("challenge evidence is required")
    if status=="RESOLVED" and not resolution_refs: raise ValueError("resolved challenge requires resolution evidence")
    c={"attestation_id":attestation_id,"package_id":package_id,"challenger_id":challenger_id,"challenged_digest":challenged_digest,"claim":claim,"evidence_refs":evidence_refs,"status":status,"resolution_refs":resolution_refs}
    cid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return AuditChallenge(cid,attestation_id,package_id,challenger_id,challenged_digest,claim,evidence_refs,status,resolution_refs)
def may_mark_resolved(*,challenge,package_digest):
    return challenge.status=="RESOLVED" and challenge.challenged_digest==package_digest and bool(challenge.resolution_refs)
def preserves_challenge_history(*,challenge): return bool(challenge.evidence_refs)
