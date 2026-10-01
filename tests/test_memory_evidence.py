from gnosis.reflection.memory_evidence import project_evolution_memory
from gnosis.storage.evolution_memory import EvolutionMemoryRecord


def test_memory_projects_to_read_only_reflection_evidence():
    r=EvolutionMemoryRecord("m","i","c","t","s",None,"rejected",("e1",),"2026-09-18T00:00:00+00:00")
    out=project_evolution_memory((r,))
    assert out[0].memory_id == "m"
    assert out[0].outcome == "rejected"
    assert out[0].evidence == ("e1",)


def test_memory_projection_is_bounded():
    records=tuple(EvolutionMemoryRecord(str(i),"i","c","t","s",None,"inconclusive",(),"2026-09-18T00:00:00+00:00") for i in range(5))
    assert len(project_evolution_memory(records, limit=2)) == 2


def test_cumulative_reflection_reads_instance_scoped_evolution_memory():
    from gnosis.core import Candidate, State
    from gnosis.instances.instance import Instance
    from gnosis.reflection.runtime import reflect_with_history
    from gnosis.storage import append_evolution_memory, connect, save_instance
    conn=connect(); instance=Instance.create_root("u", State(elements={"a":1})); save_instance(conn, instance)
    result=reflect_with_history(instance.engine, conn, instance_id=instance.instance_id)
    assert result.evolution_evidence == ()
    assert result.current.evolution_evidence == ()


def test_evolution_memory_survives_database_restart_and_returns_to_reflection():
    from pathlib import Path
    from gnosis.core import Candidate, State
    from gnosis.instances.instance import Instance
    from gnosis.reflection.runtime import reflect_with_history
    from gnosis.storage import append_evolution_memory, close, connect, load_evolution_memory, save_instance

    db = Path("/tmp/gnozis-e8b-restart.sqlite")
    if db.exists():
        db.unlink()
    conn = connect(db)
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "restart-proof")
    record = instance.engine.step(candidate)
    memory = append_evolution_memory(
        conn,
        instance_id=instance.instance_id,
        candidate_id=record.candidate_id,
        transition_id=record.transition_id,
        state_id=record.to_state_id,
        proposal_id=None,
        outcome="accepted" if record.accepted else "rejected",
        evidence=("restart-proof",),
        created_at="2026-09-25T12:00:00+00:00",
    )
    close(conn)

    conn = connect(db)
    restored = load_evolution_memory(conn, instance.instance_id)
    assert len(restored) == 1
    assert restored[0].memory_id == memory.memory_id
    assert restored[0].candidate_id == memory.candidate_id
    assert restored[0].transition_id == memory.transition_id
    assert restored[0].state_id == memory.state_id
    result = reflect_with_history(instance.engine, conn, instance_id=instance.instance_id)
    assert any(item.memory_id == memory.memory_id for item in result.evolution_evidence)
    close(conn)
    db.unlink()
