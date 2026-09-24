"""Deterministic provenance closure and replay boundary (E8.08)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class ProvenanceClosure:
    closure_id:str; chain_refs:tuple[str,...]; chain_digests:tuple[str,...]; final_digest:str; status:str

def close_provenance(*,chain_refs,chain_digests,status="PROPOSED"):
    refs=tuple(chain_refs); digs=tuple(chain_digests)
    if not refs or len(refs)!=len(digs): raise ValueError("complete provenance chain is required")
    if any(not x.strip() for x in refs+digs): raise ValueError("provenance values cannot be empty")
    if status not in {"PROPOSED","VERIFIED","REJECTED"}: raise ValueError("invalid status")
    payload={"chain_refs":refs,"chain_digests":digs}
    final="sha256:"+hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    cid="sha256:"+hashlib.sha256((final+"|"+status).encode()).hexdigest()
    return ProvenanceClosure(cid,refs,digs,final,status)

def replay_matches(*,closure,replay_chain_refs,replay_chain_digests):
    return closure.chain_refs==tuple(replay_chain_refs) and closure.chain_digests==tuple(replay_chain_digests) and closure.final_digest==close_provenance(chain_refs=replay_chain_refs,chain_digests=replay_chain_digests,status=closure.status).final_digest

def may_verify(*,closure,replay_chain_refs,replay_chain_digests): return closure.status=="PROPOSED" and replay_matches(closure=closure,replay_chain_refs=replay_chain_refs,replay_chain_digests=replay_chain_digests)
def creates_execution_authority(*,closure): return False
