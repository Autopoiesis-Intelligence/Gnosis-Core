from pathlib import Path
from gnosis.storage.database import connect
from gnosis.storage.evolution_memory import load_evolution_memory
from gnosis.self_learning.recovered_memory_influence import (
    build_influence_from_recovered_memory,
)
from tests.test_partner_learning_recovery import fixture


def test_r32_full_durable_recovery_to_next_cycle_input(tmp_path: Path):
    path = tmp_path / "gnozis.db"
    transition, instance_id = fixture(str(path))

    # Simulate the process boundary: close before recovery.
    conn = connect(str(path))
    recovered = load_evolution_memory(conn, instance_id)
    assert len(recovered) == 1
    conn.close()

    # Reopen through the same durable database and consume recovered memory.
    conn = connect(str(path))
    recovered_again = load_evolution_memory(conn, instance_id)
    influence = build_influence_from_recovered_memory(
        memory=recovered_again[0],
        parent_cycle_id="cycle:next",
    )
    conn.close()

    assert influence.source_transition_id == transition.transition_id
    assert influence.source_memory_id == recovered_again[0].memory_id
    assert influence.evidence_refs == ("ev:1",)
    assert "ev:1" in influence.next_cycle_input


def test_r32_tampered_recovered_memory_cannot_influence_next_cycle(tmp_path: Path):
    path = tmp_path / "gnozis.db"
    _, instance_id = fixture(str(path))
    conn = connect(str(path))
    row = conn.execute("SELECT memory_id FROM evolution_memory LIMIT 1").fetchone()
    conn.execute("DROP TRIGGER evolution_memory_no_update")
    conn.execute("UPDATE evolution_memory SET evidence=? WHERE memory_id=?", ('["tampered"]', row[0]))
    conn.commit()
    try:
        load_evolution_memory(conn, instance_id)
    except Exception:
        return
    finally:
        conn.close()
    raise AssertionError("tampered durable memory influenced recovery")
