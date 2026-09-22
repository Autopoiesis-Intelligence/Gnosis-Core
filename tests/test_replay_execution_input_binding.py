from gnosis.core.sandbox import SandboxExecution
from gnosis.core.execution_input import execution_input_from_state
from gnosis.core.replay import replay_evidence
from gnosis.core.types import State

def test_replay_rejects_execution_input_state_substitution():
    state=State({"x":1},(),1); other=State({"x":2},(),1)
    inp=execution_input_from_state(state,"sandbox")
    execution=SandboxExecution("c",state.state_id,state.content_id,other.content_id,1,"COMPLETED","e",{},inp.digest)
    result=replay_evidence(execution,{},state=other)
    assert not result.reproducible
    assert "execution input binding mismatch" in result.reasons
