import pytest

from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.storage import connect, save_instance
from gnosis.storage.repositories import _persist_transition
from gnosis.evolution.provenance import build_provenance, canonical_digest


@pytest.fixture
def sqlite_conn():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def provenance():
    observations = {"result": "ok"}
    evidence = canonical_digest(observations)
    return build_provenance(
        candidate_id="c1",
        parent_state_id="s1",
        parent_state_digest="pd",
        proposed_state_digest=canonical_digest({"state": "new"}),
        observations=observations,
        evidence_digest=evidence,
        proposed_state_content_id="content-1",
        candidate_binding_digest="binding-1",
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )


@pytest.fixture
def persisted_transition():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "test")
    record = instance.engine.step(candidate)
    _persist_transition(conn, instance, candidate, record, actor="test")
    return conn, instance, record
