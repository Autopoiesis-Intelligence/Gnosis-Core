from gnosis.self_learning.proposals import propose_from_finding, proposals_from_findings

def test_proposal_is_deterministic_and_non_authoritative():
    a = propose_from_finding("STATUS_DRIFT:E7.01:registry=X:artifact=Y")
    assert a == propose_from_finding("STATUS_DRIFT:E7.01:registry=X:artifact=Y")
    assert a.status == "PROPOSED"
    assert a.provenance == "self-learning-proposal-engine"
    assert a.proposal_type == "STATUS_DRIFT"

def test_proposals_deduplicate_and_sort():
    result = proposals_from_findings(["REGISTRY_MISSING:E7.02","REGISTRY_MISSING:E7.02","DEPENDENCY_MISSING:E7.03->E7.99"])
    assert len(result) == 2
    assert [x.proposal_type for x in result] == sorted([x.proposal_type for x in result])

def test_unknown_finding_is_preserved():
    result = propose_from_finding("CUSTOM_FINDING:E7.01")
    assert result.proposal_type == "UNKNOWN"
    assert result.finding == "CUSTOM_FINDING:E7.01"
