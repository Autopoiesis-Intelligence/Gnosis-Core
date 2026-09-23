from gnosis.core import TestResult, TransitionRecord
from gnosis.reflection.analyzer import Finding, RuleProposal
from gnosis.reflection.causal import attribute_finding, refine_proposal_target


def _record(i: int, rule: str) -> TransitionRecord:
    return TransitionRecord(
        from_state_id=f"s{i}",
        to_state_id=f"s{i}",
        candidate_id=f"c{i}",
        test_result=TestResult(False, ("rejected",)),
        accepted=False,
        reason="rejected",
        test_rule_id=rule,
    )


def test_finding_gets_exact_rule_attribution():
    finding = Finding(
        finding_id="finding:1",
        claim="repeat",
        observation_ids=(),
        evidence_refs=(_record(0, "rule:nonnegative").transition_id, _record(1, "rule:nonnegative").transition_id),
        reproducibility=2,
        falsification_condition="replay differs",
    )
    causal = attribute_finding(finding, (_record(0, "rule:nonnegative"), _record(1, "rule:nonnegative")))
    assert causal.target_rule_ids == ("rule:nonnegative",)
    assert causal.confidence == "EXACT_RECORDED_PROVENANCE"


def test_proposal_target_is_refined_only_from_exact_provenance():
    proposal = RuleProposal("p1", "finding:1", "unknown", "investigate", (), "effect", "risk", "test")
    finding = Finding("finding:1", "repeat", (), (_record(0, "rule:budget").transition_id,), 2, "replay")
    causal = attribute_finding(finding, (_record(0, "rule:budget"),))
    refined = refine_proposal_target(proposal, causal)
    assert refined.target == "test-rule:rule:budget"


def test_refine_proposal_target_preserves_lineage_and_versions():
    proposal = RuleProposal(
        proposal_id="p2", finding_id="finding:2", target="unknown", hypothesis="h",
        evidence_refs=("transition:0:c0",), expected_effect="e", regression_risk="r",
        required_test="t", status="PROPOSED", rule_id="rule:budget",
        current_version=3, proposed_version=4,
        finding_refs=("finding:2",), counterexample_refs=("counterexample:finding:2",),
        expected_effects=("effect",), possible_regressions=("regression",),
        test_plan="replay", provenance="test-provenance",
    )
    finding = Finding("finding:2", "repeat", (), (_record(0, "rule:budget").transition_id,), 2, "replay")
    causal = attribute_finding(finding, (_record(0, "rule:budget"),))
    refined = refine_proposal_target(proposal, causal)
    assert refined.target == "test-rule:rule:budget"
    assert refined.rule_id == proposal.rule_id
    assert refined.current_version == proposal.current_version
    assert refined.proposed_version == proposal.proposed_version
    assert refined.finding_refs == proposal.finding_refs
    assert refined.counterexample_refs == proposal.counterexample_refs
    assert refined.expected_effects == proposal.expected_effects
    assert refined.possible_regressions == proposal.possible_regressions
    assert refined.test_plan == proposal.test_plan
    assert refined.provenance == proposal.provenance
