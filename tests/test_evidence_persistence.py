from gnosis.storage.evidence import persist_evidence, load_evidence

def test_evidence_roundtrip(tmp_path):
    import sqlite3, hashlib, json
    conn=sqlite3.connect(":memory:")
    from gnosis.reflection.persistence import ensure_reflection_schema
    ensure_reflection_schema(conn)
    obs={"result":"ok","n":1}
    digest=hashlib.sha256(json.dumps(obs,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()
    persist_evidence(conn,execution_id="e1",transition_id="t1",observations=obs,evidence_digest=digest)
    assert load_evidence(conn,"e1")["observations"]==obs
    assert load_evidence(conn,"e1")["evidence_digest"]==digest

def test_evidence_digest_mismatch_rejected():
    import sqlite3, pytest
    from gnosis.reflection.persistence import ensure_reflection_schema
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    with pytest.raises(ValueError):
        persist_evidence(conn,execution_id="e1",transition_id="t1",observations={"x":1},evidence_digest="wrong")
