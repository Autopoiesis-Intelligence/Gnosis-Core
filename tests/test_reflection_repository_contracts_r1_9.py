from gnosis.adapters.sqlite_persistence import SQLiteEvolutionMemoryRepository, SQLiteReflectionRepository
from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.reflection.analyzer import ReflectionReport
from gnosis.storage import connect, save_instance
from gnosis.storage.repositories import persist_transition


def test_evolution_memory_adapter_preserves_existing_contract():
    conn = connect()
    instance = Instance.create_root("contract-user", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "reflection:endogenous")
    record = instance.engine.step(candidate)
    persist_transition(conn, instance, candidate, record, actor="contract-test")
    tid = conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?", (candidate.candidate_id,)).fetchone()[0]

    repo = SQLiteEvolutionMemoryRepository(conn)
    mem = repo.append_evolution_memory(
        instance_id=instance.instance_id, candidate_id=candidate.candidate_id,
        transition_id=tid, state_id=proposed.state_id, proposal_id="proposal:1",
        outcome="accepted", evidence=("finding:1",),
    )
    assert repo.load_evolution_memory(instance.instance_id) == (mem,)
    assert mem.digest == mem.memory_id


def test_reflection_adapter_preserves_deterministic_report_identity():
    conn = connect(":memory:")
    repo = SQLiteReflectionRepository(conn)
    report = ReflectionReport()
    first = repo.save_reflection_report(report, created_at="2026-09-21T00:00:00Z")
    second = repo.save_reflection_report(report, created_at="2026-09-21T00:00:00Z")
    assert first == second
    loaded = repo.load_reflection_report(first)
    assert loaded["report_id"] == first
    assert len(repo.list_reflection_reports()) == 1
