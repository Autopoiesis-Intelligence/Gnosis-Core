from gnosis.self_learning.self_analysis import analyze_current_learning_chain
def test_current_analysis_identifies_integration_gap():
    report=analyze_current_learning_chain()
    assert report.status=="PROPOSAL_REQUIRED"
    assert "END_TO_END_ORCHESTRATION" in report.gaps
    assert "PERSISTENT_PROPOSAL_ARTIFACT" in report.gaps
    assert report.next_contract=="E8.03"
    assert not report.execution_authority
