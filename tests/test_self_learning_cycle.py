from gnosis.self_learning.cycle import build_verified_cycle

def test_end_to_end_cycle_reaches_controlled_integration():
    result = build_verified_cycle("flow-e2e-1", knowledge={"pattern":"validated"}, reason="generalizable evidence")
    assert result.lifecycle_complete is True
    assert result.knowledge_applied is True
    assert result.version_id.startswith("sha256:")
    assert result.promotion_status == "ACCEPTED"
    assert result.integration_id.startswith("sha256:")
