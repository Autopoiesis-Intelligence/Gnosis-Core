import pytest
from gnosis.core.types import Candidate, State
from gnosis.reflection.analyzer import RuleProposal
from gnosis.reflection.rules import RuleMetadata, RuleRegistry
from gnosis.reflection.shadow_adapter import evaluate_proposal_shadow


def _candidate(value: int) -> Candidate:
    state = State(elements={"value": value})
    return Candidate(parent_state_id=state.state_id, proposed_state=state, origin="test", seed=value)


def test_rule_proposal_is_evaluated_without_activation() -> None:
    registry = RuleRegistry()
    registry.register(
        RuleMetadata(
            rule_id="test-rule:diagnostic-policy",
            rule_version=1,
            rule_type="test_policy",
            scope="test",
            implementation_ref="test:active",
            spec_ref="test:spec",
        )
    )
    proposal = RuleProposal(
        proposal_id="proposal:shadow:1",
        finding_id="finding:shadow:1",
        target="test-rule:diagnostic-policy",
        hypothesis="accept positive values",
        evidence_refs=("transition:"+_candidate(1).candidate_id,),
        expected_effect="one additional accepted candidate",
        regression_risk="negative values must remain rejected",
        required_test="shadow evaluation",
        rule_id="test-rule:diagnostic-policy",
        current_version=1,
        proposed_version=2,
    )

    candidates = (_candidate(-1), _candidate(1))

    def active_test(state, candidate):
        return state.elements["value"] > 1

    def shadow_test(state, candidate):
        return state.elements["value"] >= 1

    assessment = evaluate_proposal_shadow(
        proposal,
        candidates,
        active_test,
        shadow_test,
        registry,
    )

    assert assessment.proposal_id == proposal.proposal_id
    assert assessment.rule_id == proposal.rule_id
    assert assessment.current_version == 1
    assert assessment.proposed_version == 2
    assert len(assessment.candidate_ids) == 2
    assert assessment.evaluation.status == "BEHAVIOR_CHANGED"
    assert assessment.evaluation.improvements == 1
    assert assessment.evaluation.regressions == 0

    # The adapter only evaluates; it must not register or activate v2.
    assert registry.versions(proposal.rule_id) == (1,)


def test_shadow_adapter_rejects_duplicate_candidate_identity():
    registry = RuleRegistry()
    registry.register(RuleMetadata(
        rule_id="test-rule:diagnostic-policy", rule_version=1,
        rule_type="test_policy", scope="test",
        implementation_ref="test:active", spec_ref="test:spec",
    ))
    proposal = RuleProposal(
        proposal_id="proposal:dup", finding_id="finding:dup",
        target="test-rule:diagnostic-policy", hypothesis="h",
        evidence_refs=("transition:1",), expected_effect="e",
        regression_risk="r", required_test="shadow",
        rule_id="test-rule:diagnostic-policy", current_version=1, proposed_version=2,
    )
    candidate = _candidate(1)
    with pytest.raises(ValueError, match="unique candidate_ids"):
        evaluate_proposal_shadow(
            proposal, (candidate, candidate),
            lambda state, candidate: True,
            lambda state, candidate: True,
            registry,
        )


def test_shadow_adapter_rejects_unbound_transition_evidence_ref():
    registry = RuleRegistry()
    registry.register(RuleMetadata(
        rule_id="test-rule:diagnostic-policy", rule_version=1,
        rule_type="test_policy", scope="test",
        implementation_ref="test:active", spec_ref="test:spec",
    ))
    proposal = RuleProposal(
        proposal_id="proposal:unbound", finding_id="finding:unbound",
        target="test-rule:diagnostic-policy", hypothesis="h",
        evidence_refs=("transition:9:missing",), expected_effect="e",
        regression_risk="r", required_test="shadow",
        rule_id="test-rule:diagnostic-policy", current_version=1, proposed_version=2,
    )
    with pytest.raises(ValueError, match="do not match supplied candidates"):
        evaluate_proposal_shadow(
            proposal, (_candidate(1),),
            lambda state, candidate: True,
            lambda state, candidate: True,
            registry,
        )

def test_shadow_adapter_rejects_empty_candidate_evidence():
    registry = RuleRegistry()
    registry.register(RuleMetadata(
        rule_id="test-rule:diagnostic-policy", rule_version=1,
        rule_type="test_policy", scope="test",
        implementation_ref="test:active", spec_ref="test:spec",
    ))
    proposal = RuleProposal(
        proposal_id="proposal:empty", finding_id="finding:empty",
        target="test-rule:diagnostic-policy", hypothesis="h",
        evidence_refs=(), expected_effect="e", regression_risk="r",
        required_test="shadow", rule_id="test-rule:diagnostic-policy",
        current_version=1, proposed_version=2,
    )
    with pytest.raises(ValueError, match="at least one candidate"):
        evaluate_proposal_shadow(
            proposal, (),
            lambda state, candidate: True,
            lambda state, candidate: True,
            registry,
        )


def test_learning_proposal_requires_verified_shadow_before_authority():
    proposal = RuleProposal(
        proposal_id="proposal:learning:unverified",
        finding_id="finding:1",
        target="rule:test",
        hypothesis="learned change",
        evidence_refs=("transition:c1",),
        expected_effect="improve",
        regression_risk="unknown",
        required_test="shadow",
        rule_id="test-rule:v1",
        current_version=1,
        proposed_version=2,
    )
    candidate = Candidate(
        parent_state_id="parent",
        proposed_state=State(elements={"x": 2}),
        origin="self-learning",
        seed=1,
    )
    registry = RuleRegistry()
    registry.register(RuleMetadata(
        rule_id="test-rule:v1",
        rule_version=1,
        rule_type="test_policy",
        scope="test",
        implementation_ref="test",
        spec_ref="test",
        provenance="test",
    ))
    assessment = evaluate_proposal_shadow(
        proposal,
        (candidate,),
        lambda _: False,
        lambda _: False,
        registry,
    )
    assert assessment.evaluation.active_outcome is False
    assert assessment.evaluation.shadow_outcome is False
    assert not hasattr(assessment, "authorization")
