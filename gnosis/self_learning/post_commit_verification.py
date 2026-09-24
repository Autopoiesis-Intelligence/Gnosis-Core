"""Post-commit verification boundary for self-learning (E7.96)."""
from __future__ import annotations
import hashlib,json
from dataclasses import dataclass
@dataclass(frozen=True)
class PostCommitVerification:
    verification_id:str; commit_id:str; expected_state_digest:str; observed_state_digest:str; evidence_refs:tuple[str,...]; verification_revision:str; outcome:str
def verify_commit(*,commit_id,expected_state_digest,observed_state_digest,evidence_refs,verification_revision="r1",outcome="PENDING"):
    if not all(x.strip() for x in (commit_id,expected_state_digest,observed_state_digest,verification_revision)): raise ValueError("verification identity is required")
    if not evidence_refs: raise ValueError("verification evidence is required")
    if outcome not in {"PENDING","VERIFIED","FAILED","BLOCKED"}: raise ValueError("invalid outcome")
    refs=tuple(sorted(set(evidence_refs)))
    c={"commit_id":commit_id,"expected_state_digest":expected_state_digest,"observed_state_digest":observed_state_digest,"evidence_refs":refs,"verification_revision":verification_revision,"outcome":outcome}
    vid="sha256:"+hashlib.sha256(json.dumps(c,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return PostCommitVerification(vid,commit_id,expected_state_digest,observed_state_digest,refs,verification_revision,outcome)
def is_verified(*,verification):
    return verification.outcome=="VERIFIED" and verification.expected_state_digest==verification.observed_state_digest and bool(verification.evidence_refs)
def must_fail_closed(*,verification): return verification.outcome=="FAILED" or verification.expected_state_digest!=verification.observed_state_digest
def may_enter_evolution_memory(*,verification): return is_verified(verification=verification)
