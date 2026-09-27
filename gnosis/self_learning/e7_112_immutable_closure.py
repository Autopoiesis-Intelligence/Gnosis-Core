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

def _chain_digest(*, batch_id: str, target_commit_sha: str, chain_digests: tuple[str, ...]) -> str:
    payload = "|".join((batch_id, target_commit_sha, *chain_digests))
    return sha256(payload.encode()).hexdigest()


def create_closure(*, batch_id:str,target_commit_sha:str,chain_digests:tuple[str,...]) -> Closure:
    if not batch_id or not target_commit_sha:
        raise ValueError("closure identity is required")
    if not chain_digests or any(not d for d in chain_digests):
        return Closure(batch_id,target_commit_sha,"",ClosureState.BLOCKED)
    digest = _chain_digest(
        batch_id=batch_id,
        target_commit_sha=target_commit_sha,
        chain_digests=chain_digests,
    )
    return Closure(batch_id,target_commit_sha,digest,ClosureState.CLOSED)


def verify_closure(
    closure: Closure,
    chain_digests: tuple[str,...],
    *,
    batch_id: str | None = None,
    target_commit_sha: str | None = None,
) -> bool:
    if closure.state is not ClosureState.CLOSED or not chain_digests:
        return False
    if batch_id is not None and batch_id != closure.batch_id:
        return False
    if target_commit_sha is not None and target_commit_sha != closure.target_commit_sha:
        return False
    expected = _chain_digest(
        batch_id=closure.batch_id,
        target_commit_sha=closure.target_commit_sha,
        chain_digests=chain_digests,
    )
    return expected == closure.chain_digest
