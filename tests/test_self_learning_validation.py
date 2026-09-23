from gnosis.self_learning.proposals import propose_from_finding
from gnosis.self_learning.validation import validate_proposal, validate_proposals, validation_digest


def test_valid_proposal_passes():
    finding = "STATUS_DRIFT:E7.01:registry=X:artifact=Y"
    proposal = propose_from_finding(finding)
    result = validate_proposal(proposal, known_contract_ids=["E7.01"], known_findings=[finding])
    assert result.valid is True
    assert result.reasons == ()


def test_validation_rejects_tampered_identity_and_unknown_type():
    proposal = propose_from_finding("CUSTOM_FINDING:E7.01")
    result = validate_proposal(proposal, known_contract_ids=["E7.01"], known_findings=[proposal.finding])
    assert result.valid is False
    assert "UNKNOWN_FINDING_TYPE" in result.reasons


def test_validation_rejects_unknown_contract_and_missing_source():
    proposal = propose_from_finding("REGISTRY_MISSING:E7.99")
    result = validate_proposal(proposal, known_contract_ids=["E7.01"], known_findings=[])
    assert result.valid is False
    assert "CONTRACT_NOT_KNOWN" in result.reasons
    assert "SOURCE_FINDING_NOT_PRESENT" in result.reasons


def test_batch_validation_and_digest_are_deterministic():
    findings = ["REGISTRY_MISSING:E7.01", "DEPENDENCY_MISSING:E7.02->E7.03"]
    proposals = [propose_from_finding(x) for x in findings]
    a = validate_proposals(proposals, known_contract_ids=["E7.01", "E7.02"], known_findings=findings)
    b = validate_proposals(list(reversed(proposals)), known_contract_ids=["E7.01", "E7.02"], known_findings=findings)
    assert a == b
    assert validation_digest(a) == validation_digest(b)
