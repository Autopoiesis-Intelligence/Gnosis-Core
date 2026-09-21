from gnosis.adapters.sqlite_persistence import (
    SQLiteAuditRepository,
    SQLiteEvolutionRepository,
    SQLiteStateRepository,
)
from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.storage import connect


def test_state_repository_contract_preserves_instance_and_candidate_identity():
    conn = connect()
    repo = SQLiteStateRepository(conn)
    instance = Instance.create_root("contract-user", State(elements={"a": 1}))
    repo.save_instance(instance)

    loaded = repo.load_instance(instance.instance_id)
    assert loaded.engine.state.state_id == instance.engine.state.state_id

    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "contract")
    repo.save_candidate(candidate)
    loaded_candidate = repo.load_candidate(candidate.candidate_id)

    assert loaded_candidate.candidate_id == candidate.candidate_id
    assert loaded_candidate.parent_state_id == candidate.parent_state_id
    assert loaded_candidate.proposed_state.state_id == candidate.proposed_state.state_id


def test_evolution_repository_contract_delegates_atomic_transition_semantics():
    conn = connect()
    state_repo = SQLiteStateRepository(conn)
    evolution_repo = SQLiteEvolutionRepository(conn)

    instance = Instance.create_root("contract-user", State(elements={"a": 1}))
    state_repo.save_instance(instance)

    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "contract")
    record = instance.engine.step(candidate)

    evolution_repo.persist_transition(
        instance,
        candidate,
        record,
        actor="contract-test",
    )

    recovered = evolution_repo.recover_instance(instance.instance_id)
    assert recovered.engine.state.state_id == proposed.state_id
    assert evolution_repo.verify_durable_graph()[0] == 2


def test_audit_repository_contract_preserves_append_only_chain():
    conn = connect()
    state_repo = SQLiteStateRepository(conn)
    audit_repo = SQLiteAuditRepository(conn)

    instance = Instance.create_root("contract-user", State(elements={"a": 1}))
    state_repo.save_instance(instance)

    audit_repo.append_audit(
        actor="contract-test",
        action="contract.check",
        resource=instance.instance_id,
        result="ok",
        event_key="contract-check-1",
    )

    assert audit_repo.verify_audit_chain()[0] == 2
