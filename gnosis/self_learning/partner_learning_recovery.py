"""E8.28 durable recovery verification for partner learning."""
from __future__ import annotations
from pathlib import Path
from gnosis.storage.database import connect
from gnosis.storage.repositories import recover_instance, verify_durable_graph
from gnosis.storage.evolution_memory import load_evolution_memory

def recover_partner_learning(path: str | Path, instance_id: str):
    conn = connect(path)
    try:
        verify_durable_graph(conn)
        instance = recover_instance(conn, instance_id)
        memory = load_evolution_memory(conn, instance_id)
        return instance, memory
    finally:
        conn.close()
