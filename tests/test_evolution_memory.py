import sqlite3
import pytest
from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.storage import append_evolution_memory, connect, load_evolution_memory, save_instance
from gnosis.storage.repositories import StorageCorruptionError, persist_transition
from gnosis.reflection.analyzer import ReflectionReport, RuleProposal
from gnosis.reflection.persistence import load_proposal_evolution, save_proposal_evolution, save_reflection_report, validate_reflection_lineage, load_governance_decision, save_governance_decision, save_invariant_delta, load_invariant_delta
from gnosis.reflection.proposal_lineage import ProposalEvolution, evolve_proposal
from gnosis.reflection.invariant_delta import InvariantDelta
from gnosis.reflection.shadow import ShadowEvaluation


def test_evolution_memory_round_trip_and_digest():
    conn=connect(); instance=Instance.create_root("u", State(elements={"a":1})); save_instance(conn,instance)
    proposed=instance.engine.state.with_elements({"b":2}); candidate=Candidate(instance.engine.state.state_id,proposed,"reflection:endogenous")
    record=instance.engine.step(candidate)
    persist_transition(conn,instance,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]
    proposal = RuleProposal("proposal:1", "finding:1", "test-rule:v1", "hypothesis", (tid,), "effect", "risk", "test")
    report_id = save_reflection_report(conn, ReflectionReport(proposals=(proposal,)), created_at="2026-09-23T00:00:00+00:00")
    mem=append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,transition_id=tid,state_id=proposed.state_id,proposal_id="proposal:1",proposal_report_id=report_id,outcome="accepted",evidence=("finding:1","observation:1"))
    loaded=load_evolution_memory(conn,instance.instance_id)
    assert loaded==(mem,)
    assert mem.digest==mem.memory_id


def test_evolution_memory_is_append_only():
    conn=connect(); instance=Instance.create_root("u", State(elements={"a":1})); save_instance(conn,instance)
    proposed=instance.engine.state.with_elements({"b":2}); candidate=Candidate(instance.engine.state.state_id,proposed,"test")
    record=instance.engine.step(candidate)
    persist_transition(conn,instance,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]
    append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,transition_id=tid,state_id=proposed.state_id,proposal_id=None,outcome="accepted",evidence=("accepted",))
    with pytest.raises(sqlite3.DatabaseError): conn.execute("DELETE FROM evolution_memory")
    with pytest.raises(sqlite3.DatabaseError): conn.execute("UPDATE evolution_memory SET outcome='accepted'")


def test_evolution_memory_rejects_unknown_outcome():
    conn=connect()
    with pytest.raises(ValueError): append_evolution_memory(conn,instance_id="i",candidate_id="c",transition_id="t",state_id="s",proposal_id=None,outcome="accepted-ish",evidence=())


def test_evolution_memory_cannot_lie_about_persisted_transition():
    conn=connect(); instance=Instance.create_root("u", State(elements={"a":1})); save_instance(conn,instance)
    parent_state_id = instance.engine.state.state_id
    proposed=instance.engine.state.with_elements({"b":2}); candidate=Candidate(parent_state_id,proposed,"memory-binding")
    record=instance.engine.step(candidate)
    persist_transition(conn,instance,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]

    with pytest.raises(StorageCorruptionError, match="evolution memory outcome disagrees with transition"):
        append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,
            transition_id=tid,state_id=proposed.state_id,proposal_id=None,outcome="rejected",evidence=("false",))

    with pytest.raises(StorageCorruptionError, match="state mismatch"):
        append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,
            transition_id=tid,state_id=parent_state_id,proposal_id=None,outcome="accepted",evidence=("false",))


def _persist_memory_fixture():
    conn=connect(); instance=Instance.create_root("u", State(elements={"a":1})); save_instance(conn,instance)
    parent_state_id = instance.engine.state.state_id
    proposed=instance.engine.state.with_elements({"b":2}); candidate=Candidate(parent_state_id,proposed,"read-binding")
    record=instance.engine.step(candidate)
    persist_transition(conn,instance,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]
    append_evolution_memory(conn,instance_id=instance.instance_id,candidate_id=candidate.candidate_id,
        transition_id=tid,state_id=proposed.state_id,proposal_id=None,outcome="accepted",evidence=("ok",))
    return conn, instance, tid


@pytest.mark.parametrize(
    "mutation",
    (
        lambda conn, tid, instance: conn.execute(
            "UPDATE transitions SET accepted=0 WHERE transition_id=?", (tid,)
        ),
        lambda conn, tid, instance: conn.execute(
            "UPDATE transitions SET to_state_id=? WHERE transition_id=?",
            (instance.engine.state.state_id, tid),
        ),
    ),
    ids=("accepted", "to_state_id"),
)
def test_load_evolution_memory_rejects_transition_semantic_tamper(mutation):
    conn, instance, tid = _persist_memory_fixture()
    parent_state_id = conn.execute("SELECT parent_state_id FROM candidates WHERE candidate_id=(SELECT candidate_id FROM transitions WHERE transition_id=?)", (tid,)).fetchone()[0]
    mutation(conn, tid, instance)
    with pytest.raises(StorageCorruptionError):
        load_evolution_memory(conn, instance.instance_id)


def test_evolution_memory_rejects_cross_instance_transition_rebinding():
    conn=connect()
    a=Instance.create_root("a", State(elements={"a":1}))
    b=Instance.create_root("b", State(elements={"b":1}))
    save_instance(conn,a); save_instance(conn,b)
    proposed=a.engine.state.with_elements({"x":2})
    candidate=Candidate(a.engine.state.state_id,proposed,"cross-instance")
    record=a.engine.step(candidate)
    persist_transition(conn,a,candidate,record,actor="test")
    tid=conn.execute("SELECT transition_id FROM transitions WHERE candidate_id=?",(candidate.candidate_id,)).fetchone()[0]
    mem=append_evolution_memory(conn,instance_id=a.instance_id,candidate_id=candidate.candidate_id,transition_id=tid,state_id=proposed.state_id,proposal_id=None,outcome="accepted",evidence=("ok",))
    raw={"instance_id":b.instance_id,"candidate_id":mem.candidate_id,"transition_id":mem.transition_id,
         "state_id":mem.state_id,"proposal_id":mem.proposal_id,"outcome":mem.outcome,
         "evidence":mem.evidence,"created_at":mem.created_at,"proposal_report_id":mem.proposal_report_id}
    new_id=__import__("hashlib").sha256(__import__("gnosis.storage.repositories",fromlist=["canonical_json"]).canonical_json(raw).encode()).hexdigest()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE evolution_memory SET instance_id=?, memory_id=? WHERE memory_id=?",
                     (b.instance_id,new_id,mem.memory_id))


def test_evolution_memory_rejects_tampered_transition_identity_on_reload():
    conn = connect()
    instance = Instance.create_root("u", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"next": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "next")
    record = instance.engine.step(candidate)
    persist_transition(conn, instance, candidate, record, actor="test")
    append_evolution_memory(
        conn, instance_id=instance.instance_id, candidate_id=candidate.candidate_id,
        transition_id=record.transition_id, state_id=record.to_state_id,
        proposal_id=None, outcome="accepted", evidence=("ok",),
    )
    conn.execute("UPDATE transitions SET test_rule_id=? WHERE transition_id=?", ("tampered", record.transition_id))
    with pytest.raises(StorageCorruptionError):
        load_evolution_memory(conn, instance.instance_id)


def test_reflection_persistence_round_trip_preserves_report_and_counterexample_identity():
    conn = connect()
    report = ReflectionReport(
        proposals=(
            RuleProposal("proposal:persist", "finding:persist", "test-rule:v1", "hypothesis", (), "effect", "risk", "test"),
        ),
    )
    report_id = save_reflection_report(
        conn, report, created_at="2026-09-23T10:00:00+00:00"
    )
    loaded = __import__("gnosis.reflection.persistence", fromlist=["load_reflection_report"]).load_reflection_report(conn, report_id)
    assert loaded["report_id"] == report_id
    assert loaded["payload"]["proposals"][0]["proposal_id"] == "proposal:persist"


def test_reflection_report_tamper_is_rejected_by_content_identity():
    conn = connect()
    report = ReflectionReport(
        proposals=(
            RuleProposal("proposal:tamper", "finding:tamper", "test-rule:v1", "hypothesis", (), "effect", "risk", "test"),
        ),
    )
    report_id = save_reflection_report(
        conn, report, created_at="2026-09-23T10:01:00+00:00"
    )
    conn.execute(
        "UPDATE reflection_reports SET payload=? WHERE report_id=?",
        ('{"proposals":[],"findings":[],"counterexample_results":[]}', report_id),
    )
    with pytest.raises(RuntimeError, match="reflection persistence integrity mismatch"):
        __import__("gnosis.reflection.persistence", fromlist=["load_reflection_report"]).load_reflection_report(conn, report_id)


def test_shadow_assessment_persistence_rejects_payload_tamper():
    conn = connect()
    report = ReflectionReport(proposals=())
    report_id = save_reflection_report(conn, report, created_at="2026-09-23T10:02:00+00:00")
    assessment = ShadowEvaluation(status="UNCHANGED", cases=())
    assessment_id = save_shadow_assessment(conn, report_id, assessment)
    conn.execute(
        "UPDATE reflection_shadow_assessments SET payload=? WHERE assessment_id=?",
        ('{"status":"CHANGED","cases":[]}', assessment_id),
    )
    with pytest.raises(RuntimeError, match="shadow assessment persistence integrity mismatch"):
        load_shadow_assessment(conn, assessment_id)


def test_shadow_assessment_exact_replay_does_not_replace_payload():
    conn = connect()
    report = ReflectionReport(proposals=())
    report_id = save_reflection_report(conn, report, created_at="2026-09-23T10:03:00+00:00")
    assessment = ShadowEvaluation(status="UNCHANGED", cases=())
    assessment_id = save_shadow_assessment(conn, report_id, assessment)
    assert save_shadow_assessment(conn, report_id, assessment) == assessment_id
    assert conn.execute(
        "SELECT COUNT(*) FROM reflection_shadow_assessments WHERE assessment_id=?",
        (assessment_id,),
    ).fetchone()[0] == 1



def test_proposal_evolution_persistence_round_trip_and_exact_replay():
    conn = connect()
    evolution = evolve_proposal(
        finding_id="f1",
        current_proposal_id="p1",
        prior_proposals=({"finding_id": "f1", "proposal_id": "p0", "status": "REJECTED"},),
        evidence_refs=("e1",),
    )
    evolution_id = save_proposal_evolution(conn, evolution)
    assert save_proposal_evolution(conn, evolution) == evolution_id
    assert load_proposal_evolution(conn, evolution_id) == evolution
    assert conn.execute(
        "SELECT COUNT(*) FROM reflection_proposal_evolutions WHERE evolution_id=?",
        (evolution_id,),
    ).fetchone()[0] == 1


def test_proposal_evolution_persistence_rejects_payload_tamper():
    conn = connect()
    evolution = evolve_proposal(
        finding_id="f2",
        current_proposal_id="p2",
        prior_proposals=(),
    )
    evolution_id = save_proposal_evolution(conn, evolution)
    conn.execute(
        "UPDATE reflection_proposal_evolutions SET rationale=? WHERE evolution_id=?",
        ("tampered", evolution_id),
    )
    with pytest.raises(RuntimeError, match="proposal evolution persistence integrity mismatch"):
        load_proposal_evolution(conn, evolution_id)


def test_persisted_reflection_lineage_accepts_consistent_evolution():
    conn = connect()
    proposal = RuleProposal(
        "p-lineage", "f-lineage", "test-rule:v1", "hypothesis", (), "effect", "risk", "test"
    )
    report_id = save_reflection_report(
        conn,
        ReflectionReport(
            findings=(
                __import__("gnosis.reflection.analyzer", fromlist=["Finding"]).Finding(
                    "f-lineage", "claim", (), (), 1, "condition"
                ),
            ),
            proposals=(proposal,),
        ),
        created_at="2026-09-23T10:04:00+00:00",
    )
    evolution = evolve_proposal(
        finding_id="f-lineage",
        current_proposal_id="p-lineage",
        prior_proposals=(),
    )
    save_proposal_evolution(conn, evolution)
    result = validate_reflection_lineage(conn, report_id)
    assert result["findings"] == 1
    assert result["proposals"] == 1
    assert result["proposal_evolutions"] == 1


def test_persisted_reflection_lineage_rejects_foreign_evolution():
    conn = connect()
    report_id = save_reflection_report(
        conn,
        ReflectionReport(proposals=()),
        created_at="2026-09-23T10:05:00+00:00",
    )
    evolution = evolve_proposal(
        finding_id="foreign-finding",
        current_proposal_id="foreign-proposal",
        prior_proposals=(),
    )
    save_proposal_evolution(conn, evolution)
    with pytest.raises(RuntimeError, match="outside reflection lineage"):
        validate_reflection_lineage(conn, report_id)


def test_governance_persistence_rejects_payload_tamper():
    conn = connect()
    report_id = save_reflection_report(conn, ReflectionReport(), created_at="2026-09-23T10:06:00+00:00")
    decision = GovernanceDecision(
        decision="REVIEW",
        shadow_status="BEHAVIOR_CHANGED",
        invariant_status="IMPROVED",
        rationale=("evidence",),
    )
    decision_id = save_governance_decision(conn, report_id, decision)
    conn.execute(
        "UPDATE reflection_governance_decisions SET payload=? WHERE decision_id=?",
        ('{"decision":"BLOCK","shadow_status":"REGRESSION","invariant_status":"VIOLATED","rationale":["tampered"],"provenance":"reflection-governance"}', decision_id),
    )
    with pytest.raises(RuntimeError, match="governance persistence integrity mismatch"):
        load_governance_decision(conn, decision_id)


def test_shadow_assessment_lineage_binds_proposal_id():
    conn = connect()
    report_id = save_reflection_report(conn, ReflectionReport(), created_at="2026-09-23T10:07:00+00:00")
    assessment = ShadowEvaluation(cases=(), changed_cases=0, accepted_by_active=0, accepted_by_shadow=0, regressions=0, improvements=0, status="NO_INPUT")
    assessment_id = save_shadow_assessment(conn, report_id, assessment, proposal_id="p1")
    assert load_shadow_assessment(conn, assessment_id)["proposal_id"] == "p1"
    with pytest.raises(RuntimeError, match="conflicting shadow assessment replay"):
        save_shadow_assessment(conn, report_id, assessment, proposal_id="p2")


def test_invariant_delta_persistence_rejects_payload_tamper():
    conn = connect()
    report_id = save_reflection_report(conn, ReflectionReport(), created_at="2026-09-23T10:08:00+00:00")
    delta = InvariantDelta(
        preserved=("i1",), violated=(), improved=(), unknown=(),
        active_violations={}, shadow_violations={},
    )
    delta_id = save_invariant_delta(conn, report_id, delta)
    conn.execute(
        "UPDATE reflection_invariant_deltas SET payload=? WHERE delta_id=?",
        ('{"preserved":[],"violated":[],"improved":[],"unknown":[],"active_violations":{},"shadow_violations":{}}', delta_id),
    )
    with pytest.raises(RuntimeError, match="invariant delta persistence integrity mismatch"):
        load_invariant_delta(conn, delta_id)


def test_governance_lineage_rejects_decision_not_derived_from_evidence():
    conn = connect()
    report_id = save_reflection_report(conn, ReflectionReport(), created_at="2026-09-23T10:09:00+00:00")
    shadow = ShadowEvaluation(cases=(), changed_cases=0, accepted_by_active=0, accepted_by_shadow=0, regressions=0, improvements=0, status="NO_INPUT")
    save_shadow_assessment(conn, report_id, shadow)
    delta = InvariantDelta(
        preserved=(), violated=(), improved=(), unknown=(),
        active_violations={}, shadow_violations={},
    )
    save_invariant_delta(conn, report_id, delta)
    dishonest = GovernanceDecision(
        decision="REVIEW", shadow_status="NO_INPUT",
        invariant_status="PRESERVED", rationale=("not-derived",),
    )
    save_governance_decision(conn, report_id, dishonest)
    with pytest.raises(RuntimeError, match="does not match persisted shadow/invariant evidence"):
        validate_reflection_lineage(conn, report_id)
