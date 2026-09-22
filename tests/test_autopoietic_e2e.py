import pytest

from gnosis.core import Candidate, State
from gnosis.core.counterexample import ReflectionReassessment, verify_counterexample
from gnosis.core.durable_commit import persist_authorized_transition
from gnosis.core.governance import authorize
from gnosis.core.gap import GapHypothesis
from gnosis.core.investigation import Counterexample
from gnosis.core.rule_proposal import make_rule_proposal, qualify_supported
from gnosis.core.shadow import evaluate_rule_proposal
from gnosis.instances.instance import Instance
from gnosis.storage import connect, recover_instance, save_instance, verify_durable_graph


def test_autopoietic_path_reaches_durable_recovered_state(tmp_path):
    path = tmp_path / "autopoiesis.sqlite"
    conn = connect(path)
    instance = Instance.create_root("u", State(elements={"root": 0}))
    save_instance(conn, instance)

    gap = GapHypothesis("gap:x", ("e1", "e2"), "diagnostic tension", "x")
    counterexample = Counterexample(
        "c:x", "finding:x", "counterexample", ("e1",), "ADMITTED"
    )
    verification = verify_counterexample(
        counterexample, refutes=False, reason="counterexample does not refute gap"
    )
    reassessment = qualify_supported(
        ReflectionReassessment("gap:x", "finding:x", "UNRESOLVED", (), True), gap
    )
    assert reassessment.result == "SUPPORTED"

    proposal = make_rule_proposal(reassessment, gap)
    shadow = evaluate_rule_proposal(
        proposal,
        state_id=instance.engine.state.state_id,
        checks=(("replay", True), ("regression:baseline", True)),
    )
    authorization = authorize(
        proposal,
        shadow,
        evidence_refs=gap.source_records,
        counterexample_refs=(verification.counterexample_id,),
        limitations=("shadow-scope:baseline",),
    )

    proposed = instance.engine.state.with_elements({"root": 0, "evolved": 1})
    candidate = Candidate(instance.engine.state.state_id, proposed, proposal.proposal_id)
    transition = instance.engine.step(candidate)
    assert transition.accepted

    persist_authorized_transition(
        conn,
        authorization,
        proposal,
        instance,
        candidate,
        transition,
        actor="core",
    )
    conn.close()

    reopened = connect(path)
    recovered = recover_instance(reopened, instance.instance_id)
    assert recovered.engine.state.state_id == proposed.state_id
    assert recovered.engine.state.elements["evolved"] == 1
    assert verify_durable_graph(reopened)[0] == 2
