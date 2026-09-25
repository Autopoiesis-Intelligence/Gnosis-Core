from gnosis.self_learning.feedback_integration import admit_feedback
from gnosis.self_learning.learning_influence_persistence import (
    persist_learning_evidence,
    restart_cycle_from_persisted_evidence,
)


def test_learning_influence_survives_persisted_evidence_boundary():
    admission = admit_feedback(
        feedback_id="feedback:cycle-1",
        contract_id="contract:e806",
        scope="sandbox",
        verdict="FAIL",
        evidence_refs=("evidence:failure-1",),
        learning_class="COUNTEREXAMPLE",
        status="ADMITTED",
    )
    persisted = persist_learning_evidence(admission=admission)
    restarted = restart_cycle_from_persisted_evidence(
        persisted=persisted,
        parent_cycle_id="cycle:1",
        parent_state_digest="sha256:state1",
    )

    assert restarted.input_refs == ("evidence:failure-1",)
    assert restarted.parent_memory_entry_id.startswith("sha256:")
    assert restarted.cycle_id.startswith("sha256:")


def test_unadmitted_evidence_cannot_cross_persistence_boundary():
    admission = admit_feedback(
        feedback_id="feedback:cycle-1",
        contract_id="contract:e806",
        scope="sandbox",
        verdict="FAIL",
        evidence_refs=("evidence:failure-1",),
        learning_class="COUNTEREXAMPLE",
        status="PROPOSED",
    )
    try:
        persist_learning_evidence(admission=admission)
    except ValueError:
        return
    raise AssertionError("unadmitted feedback crossed persistence boundary")
