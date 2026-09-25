from pathlib import Path

from gnosis.core import Candidate, State, TestResult, TransitionRecord
from gnosis.instances.instance import Instance
from gnosis.storage.database import connect
from gnosis.storage.repositories import save_state, _persist_transition, save_candidate, save_instance
from gnosis.storage.evolution_memory import load_evolution_memory
from gnosis.self_learning.partner_learning_adapter import build_request
from gnosis.self_learning.partner_learning_gate import admit_partner_candidate
from gnosis.self_learning.partner_learning_runtime import commit_admitted_partner_learning
from gnosis.self_learning.recovered_memory_influence import build_influence_from_recovered_memory


def fixture(path):
    conn = connect(path)
    parent = State(elements={"v": 1})
    proposed = parent.with_elements({"v": 2})
    save_state(conn, parent)
    candidate = Candidate(parent.state_id, proposed, "partner:test", 1)
    save_candidate(conn, candidate)
    tr = TransitionRecord(
        parent.state_id, proposed.state_id, candidate.candidate_id,
        TestResult(True, ("ok",)), True, "committed", "test:partner"
    )
    instance = Instance.create_root("o", parent)
    save_instance(conn, instance)
    instance_id = instance.instance_id
    _persist_transition(conn, instance, candidate, tr, actor="test")
    admission = admit_partner_candidate(
        classification_id="class:1", result_id="result:1",
        candidate_digest="prov:1", evidence_refs=("ev:1",),
        classification_verified=True, replay_verified=True,
        receipt_received=True, core_verified=True,
    )
    request = build_request(
        candidate_id=candidate.candidate_id, result_id="result:1",
        contract_id="contract:1", provenance_digest="prov:1",
        evidence_refs=("ev:1",), state_digest=proposed.state_id,
        admission_verified=True,
    )
    commit_admitted_partner_learning(
        conn, admission=admission, request=request,
        instance_id=instance_id, transition_id=tr.transition_id,
        state_id=tr.to_state_id, outcome="accepted", actor="partner", parent_state_digest=tr.from_state_id,
    )
    conn.close()
    return tr, instance_id


def test_r32_full_durable_recovery_to_next_cycle_input(tmp_path: Path):
    path = tmp_path / "gnozis.db"
    transition, instance_id = fixture(str(path))
    conn = connect(str(path))
    recovered = load_evolution_memory(conn, instance_id)
    assert len(recovered) == 1
    conn.close()

    conn = connect(str(path))
    recovered_again = load_evolution_memory(conn, instance_id)
    influence = build_influence_from_recovered_memory(
        memory=recovered_again[0], parent_cycle_id="cycle:next"
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
    conn.execute(
        "UPDATE evolution_memory SET evidence=? WHERE memory_id=?",
        ('["tampered"]', row[0]),
    )
    conn.commit()
    try:
        load_evolution_memory(conn, instance_id)
    except Exception:
        return
    finally:
        conn.close()
    raise AssertionError("tampered durable memory influenced recovery")
