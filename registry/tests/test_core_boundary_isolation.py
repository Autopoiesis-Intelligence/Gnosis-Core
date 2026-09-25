#!/usr/bin/env python3
"""Regression contract: Federation authorization never becomes Core mutation authority."""
from registry.core_handoff import create_handoff


def test_authorized_federation_creates_only_pending_handoff():
    authorization = {"result": "AUTHORIZED", "authorization_sha256": "a" * 64}
    candidate = {"candidate_id": "candidate-1", "source_id": "research-math", "resource_id": "r-1"}
    out = create_handoff(authorization, candidate, "core-evolution", "propose", ["evidence-1"])
    assert out["result"] == "HANDOFF_READY"
    assert out["handoff"]["status"] == "PENDING_CORE_AUTHORITY"
    assert "commit_capability" not in out["handoff"]
    assert "mutation_capability" not in out["handoff"]


def test_unauthorized_federation_cannot_create_handoff():
    authorization = {"result": "REJECTED", "authorization_sha256": "a" * 64}
    candidate = {"candidate_id": "candidate-1", "source_id": "research-math", "resource_id": "r-1"}
    out = create_handoff(authorization, candidate, "core-evolution", "propose", ["evidence-1"])
    assert out["result"] == "REJECT"
    assert "federation_not_authorized" in out["errors"]
