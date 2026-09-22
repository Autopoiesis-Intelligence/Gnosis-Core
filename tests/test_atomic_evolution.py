def test_atomic_evolution_rolls_back_on_failure():
    import sqlite3, json, hashlib, pytest
    from gnosis.reflection.persistence import ensure_reflection_schema
    from gnosis.storage.atomic_evolution import persist_evolution_with_evidence
    from gnosis.core.provenance import EvidenceProvenance, canonical_digest
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    obs={"x":1}; digest=canonical_digest(obs)
    p=EvidenceProvenance(provenance_id="p1",execution_id="e1",candidate_id="c1",parent_state_id="s1",
      parent_state_digest="pd",proposed_state_digest="sd",evidence_digest=digest,evaluation_status="PASS",
      shadow_status="PASS",invariant_status="PRESERVED",governance_decision="COMMIT",status="RECORDED",
      evolution_identity="ei",proposed_state_content_id="state",candidate_binding_digest="bind")
    with pytest.raises(Exception):
        persist_evolution_with_evidence(conn,p,event_type="COMMIT",payload={},transition_id="t1",observations={"x":2})
    assert conn.execute("SELECT count(*) FROM evolution_evidence").fetchone()[0]==0
