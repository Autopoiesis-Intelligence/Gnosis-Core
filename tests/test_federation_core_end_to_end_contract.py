"""Contract-level E2E boundary checks without invoking a real state mutation."""
from registry.core_handoff import create_handoff


def test_full_federation_boundary_stops_before_core_commit():
    authorization={"result":"AUTHORIZED","authorization_sha256":"a"*64}
    candidate={"candidate_id":"candidate-1","source_id":"science-math","resource_id":"math-001"}
    out=create_handoff(authorization,candidate,"core-evolution","propose",["evidence-1"])
    assert out["result"] == "HANDOFF_READY"
    handoff=out["handoff"]
    assert handoff["status"] == "PENDING_CORE_AUTHORITY"
    assert handoff["candidate_id"] == candidate["candidate_id"]
    assert handoff["source_id"] == candidate["source_id"]
    assert handoff["resource_id"] == candidate["resource_id"]
    assert "commit_capability" not in handoff
    assert "mutation_capability" not in handoff


def test_federation_cannot_forge_core_commit_state():
    authorization={"result":"AUTHORIZED","authorization_sha256":"b"*64}
    candidate={"candidate_id":"candidate-2","source_id":"science-physics","resource_id":"physics-001"}
    out=create_handoff(authorization,candidate,"core-evolution","propose",["evidence-2"])
    assert out["handoff"]["status"] != "COMMITTED"
