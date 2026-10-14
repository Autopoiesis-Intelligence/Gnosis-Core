"""Real SQLite commit-path rollback proof using valid ephemeral signed authorization."""
from dataclasses import replace

import pytest


def _event(conn, event_id):
    return conn.execute("SELECT event_hash FROM audit_events WHERE event_id=?", (event_id,)).fetchone()


def _commit(fixture, request):
    return fixture.adapter.commit(
        fixture.conn, fixture.instance, fixture.candidate, fixture.record, request,
        actor="trusted-owner",
        production_authorization=fixture.production_authorization,
        trust_context=fixture.trust_context,
        expected_proposal_binding_digest=fixture.proposal_binding_digest,
    )


def test_real_commit_rolls_back_after_persistence_failure(real_commit_fixture):
    conn, instance, candidate, record, request = real_commit_fixture
    request = replace(request, failure_injection="after_audit")
    before_head = instance.engine.state.state_id
    with pytest.raises(RuntimeError, match="after_audit"):
        _commit(real_commit_fixture, request)
    assert _event(conn, f"execution-authorization-nonce:{real_commit_fixture.nonce}") is None
    assert conn.execute("SELECT 1 FROM transitions WHERE transition_id=?", (record.transition_id,)).fetchone() is None
    assert conn.execute("SELECT 1 FROM candidates WHERE candidate_id=?", (record.candidate_id,)).fetchone() is None
    assert instance.engine.state.state_id == before_head


def test_real_commit_failure_injection_is_not_silent(real_commit_fixture):
    _, _, _, _, request = real_commit_fixture
    request = replace(request, failure_injection="after_transition")
    with pytest.raises(RuntimeError, match="after_transition"):
        _commit(real_commit_fixture, request)
