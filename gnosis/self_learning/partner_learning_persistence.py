"""E8.26 canonical partner learning persistence integration."""
from __future__ import annotations
from dataclasses import dataclass
from gnosis.storage.database import transaction
from gnosis.storage.evolution_memory import append_evolution_memory, EvolutionMemoryRecord
from gnosis.storage.repositories import StorageCorruptionError, append_audit, verify_audit_chain, load_state

@dataclass(frozen=True)
class PartnerLearningCommitResult:
    request_id: str
    memory_id: str
    audit_event_hash: str
    outcome: str

def commit_partner_learning(conn, *, request_id, instance_id, candidate_id, transition_id, state_id, provenance_digest, evidence, outcome, actor):
    """Persist an admitted partner result through the canonical memory/audit path."""
    required = (request_id, instance_id, candidate_id, transition_id, state_id, provenance_digest, actor)
    if not all(isinstance(value, str) and value.strip() for value in required):
        raise ValueError("complete partner learning persistence identity is required")
    if not evidence:
        raise ValueError("partner learning evidence is required")
    if outcome not in {"accepted", "rejected", "inconclusive"}:
        raise ValueError("invalid partner learning outcome")
    with transaction(conn):
        row = conn.execute("SELECT candidate_id, from_state_id, to_state_id, accepted FROM transitions WHERE transition_id=? AND instance_id=?", (transition_id, instance_id)).fetchone()
        if row is None:
            raise StorageCorruptionError("partner result references missing transition")
        if row[0] != candidate_id:
            raise StorageCorruptionError("partner result candidate/transition mismatch")
        if row[2] != state_id:
            raise StorageCorruptionError("partner result state/transition mismatch")
        if outcome in {"accepted", "rejected"} and ((outcome == "accepted") != bool(row[3])):
            raise StorageCorruptionError("partner result outcome disagrees with transition")
        load_state(conn, state_id)
        record: EvolutionMemoryRecord = append_evolution_memory(conn, instance_id=instance_id, candidate_id=candidate_id, transition_id=transition_id, state_id=state_id, proposal_id=None, outcome=outcome, evidence=tuple(evidence))
        audit_hash = append_audit(conn, actor=actor, action="partner.learning.commit", resource=candidate_id, result=f"{outcome};request={request_id};provenance={provenance_digest}", event_key=f"partner-learning:{request_id}")
        verify_audit_chain(conn)
        return PartnerLearningCommitResult(request_id, record.memory_id, audit_hash, outcome)
