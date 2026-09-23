from gnosis.evolution.authorization_verification import verify_authorization_freshness
from gnosis.evolution.commit_authorization import DirectoryCommitAuthorization


def _authorization() -> DirectoryCommitAuthorization:
    return DirectoryCommitAuthorization.issue(
        candidate_id="candidate-A",
        candidate_binding_digest="binding-A",
        provenance_id="prov-A",
        evidence_digest="evidence-A",
        decision_digest="decision-A",
        governance_decision="ACCEPT",
        shadow_accepted=True,
    )


def test_fresh_authorization_is_valid():
    result = verify_authorization_freshness(
        _authorization(),
        current_candidate_id="candidate-A",
        current_candidate_binding_digest="binding-A",
        current_provenance_id="prov-A",
        current_evidence_digest="evidence-A",
        current_decision_digest="decision-A",
    )
    assert result.valid
    assert result.reasons == ()


def test_stale_candidate_is_rejected():
    result = verify_authorization_freshness(
        _authorization(),
        current_candidate_id="candidate-B",
        current_candidate_binding_digest="binding-A",
        current_provenance_id="prov-A",
        current_evidence_digest="evidence-A",
        current_decision_digest="decision-A",
    )
    assert not result.valid
    assert "stale candidate identity" in result.reasons


def test_stale_binding_is_rejected():
    result = verify_authorization_freshness(
        _authorization(),
        current_candidate_id="candidate-A",
        current_candidate_binding_digest="binding-B",
        current_provenance_id="prov-A",
        current_evidence_digest="evidence-A",
        current_decision_digest="decision-A",
    )
    assert not result.valid
    assert "stale candidate binding" in result.reasons


def test_stale_provenance_is_rejected():
    result = verify_authorization_freshness(
        _authorization(),
        current_candidate_id="candidate-A",
        current_candidate_binding_digest="binding-A",
        current_provenance_id="prov-B",
        current_evidence_digest="evidence-A",
        current_decision_digest="decision-A",
    )
    assert not result.valid
    assert "stale provenance identity" in result.reasons


def test_stale_evidence_is_rejected():
    result = verify_authorization_freshness(
        _authorization(),
        current_candidate_id="candidate-A",
        current_candidate_binding_digest="binding-A",
        current_provenance_id="prov-A",
        current_evidence_digest="evidence-B",
        current_decision_digest="decision-A",
    )
    assert not result.valid
    assert "stale evidence identity" in result.reasons


def test_stale_decision_is_rejected():
    result = verify_authorization_freshness(
        _authorization(),
        current_candidate_id="candidate-A",
        current_candidate_binding_digest="binding-A",
        current_provenance_id="prov-A",
        current_evidence_digest="evidence-A",
        current_decision_digest="decision-B",
    )
    assert not result.valid
    assert "stale decision identity" in result.reasons


def test_tampered_authorization_is_rejected():
    auth = _authorization()
    tampered = DirectoryCommitAuthorization(
        candidate_id=auth.candidate_id,
        candidate_binding_digest=auth.candidate_binding_digest,
        provenance_id=auth.provenance_id,
        evidence_digest=auth.evidence_digest,
        decision_digest=auth.decision_digest,
        governance_decision="REJECT",
        shadow_accepted=auth.shadow_accepted,
        authorization_digest=auth.authorization_digest,
    )
    result = verify_authorization_freshness(
        tampered,
        current_candidate_id="candidate-A",
        current_candidate_binding_digest="binding-A",
        current_provenance_id="prov-A",
        current_evidence_digest="evidence-A",
        current_decision_digest="decision-A",
    )
    assert not result.valid
    assert "authorization integrity verification failed" in result.reasons
