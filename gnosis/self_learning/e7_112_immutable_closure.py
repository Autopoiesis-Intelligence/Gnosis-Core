"""E7.112 immutable closure for the verified evidence chain."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

class ClosureState(str, Enum):
    CLOSED="CLOSED"; REJECTED="REJECTED"; BLOCKED="BLOCKED"

@dataclass(frozen=True)
class Closure:
    batch_id: str
    target_commit_sha: str
    chain_digest: str
    state: ClosureState

def create_closure(*, batch_id:str,target_commit_sha:str,chain_digests:tuple[str,...]) -> Closure:
    if not batch_id or not target_commit_sha:
        raise ValueError("closure identity is required")
    if not chain_digests or any(not d for d in chain_digests):
        return Closure(batch_id,target_commit_sha,"",ClosureState.BLOCKED)
    payload="|".join(chain_digests)
    digest=sha256(payload.encode()).hexdigest()
    return Closure(batch_id,target_commit_sha,digest,ClosureState.CLOSED)

def verify_closure(closure:Closure, chain_digests:tuple[str,...]) -> bool:
    if closure.state is not ClosureState.CLOSED or not chain_digests:
        return False
    expected=sha256("|".join(chain_digests).encode()).hexdigest()
    return expected == closure.chain_digest
