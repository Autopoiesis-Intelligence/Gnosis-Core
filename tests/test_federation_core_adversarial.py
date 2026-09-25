import pytest
from registry.core_handoff import create_handoff


def base():
    return ({"result":"AUTHORIZED","authorization_sha256":"a"*64},
            {"candidate_id":"c1","source_id":"research-math","resource_id":"r1"})


def test_replayed_or_stale_authorization_reference_is_not_upgraded():
    auth,candidate=base()
    out=create_handoff(auth,candidate,"core-evolution","propose",["e1"])
    assert out["handoff"]["status"] == "PENDING_CORE_AUTHORITY"
    assert out["handoff"]["federation_authorization_sha256"] == "a"*64
    assert "COMMITTED" not in out["handoff"].values()


def test_missing_evidence_is_rejected():
    auth,candidate=base()
    out=create_handoff(auth,candidate,"core-evolution","propose",[])
    assert out["result"] == "REJECT"


def test_missing_source_or_resource_identity_is_rejected():
    auth,candidate=base()
    candidate.pop("source_id")
    out=create_handoff(auth,candidate,"core-evolution","propose",["e1"])
    assert out["result"] == "REJECT"
    assert "missing_source_identity" in out["errors"]
