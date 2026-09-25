import pytest

from gnosis.evolution.federation_admission import admit_federation_evidence, build_core_provenance
from registry.core_handoff import create_handoff


def handoff():
    return create_handoff({"result":"AUTHORIZED","authorization_sha256":"a" * 64},{"candidate_id":"c1","source_id":"s1","resource_id":"r1"},"core-evolution","propose",["e1"])["handoff"]


def test_admission_accepts_verified_evidence_only():
    env = admit_federation_evidence(handoff(), {"observation":"value"})
    assert env.candidate_id == "c1"
    assert env.handoff_sha256


def test_admission_rejects_tampered_handoff():
    h = handoff(); h["source_id"] = "forged"
    with pytest.raises(PermissionError):
        admit_federation_evidence(h, {"observation":"value"})


def test_admission_builds_canonical_provenance_without_commit_authority():
    env = admit_federation_evidence(handoff(), {"observation":"value"})
    p = build_core_provenance(env, parent_state_id="p1", parent_state_digest="pd", proposed_state_digest="qd", proposed_state_content_id="content", candidate_binding_digest="binding", evaluation_status="PASS", shadow_status="PASS", invariant_status="PASS", governance_decision="ALLOW")
    assert p.candidate_id == "c1"
    assert p.provenance_id.startswith("provenance:")
    assert not hasattr(env, "commit")
