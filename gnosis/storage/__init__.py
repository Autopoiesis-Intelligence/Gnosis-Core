from .evolution_memory import EvolutionMemoryRecord, append_evolution_memory, load_evolution_memory
from .database import GENESIS_HASH, SCHEMA_VERSION, close, connect, transaction
from .authorization import RecoveryAuthorization
from .repositories import (
    SecretMaterialError,
    StorageCorruptionError,
    append_audit,
    load_candidate,
    load_instance,
    recover_instance,
    recovery_evidence_digest,
    load_state,
    load_transition_records,
    save_candidate,
    save_instance,
    save_state,
    verify_durable_graph,
    verify_audit_chain,
)

def ensure_reflection_schema(conn):
    """Lazily expose the reflection schema initializer without importing reflection during storage initialization."""
    from gnosis.reflection.persistence import ensure_reflection_schema as _ensure_reflection_schema
    return _ensure_reflection_schema(conn)

__all__ = [
    "GENESIS_HASH", "SCHEMA_VERSION", "connect", "close", "transaction",
    "SecretMaterialError", "StorageCorruptionError",
    "RecoveryAuthorization", "ensure_reflection_schema",
    "append_audit", "load_candidate", "load_instance", "recover_instance", "recovery_evidence_digest", "load_state",
    "load_transition_records", "save_candidate", "save_instance", "save_state",
    "verify_audit_chain", "verify_durable_graph", "EvolutionMemoryRecord", "append_evolution_memory", "load_evolution_memory",
]
