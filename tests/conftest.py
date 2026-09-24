import pytest

from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.storage import connect, save_instance


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

from gnosis.storage.repositories import _persist_transition
