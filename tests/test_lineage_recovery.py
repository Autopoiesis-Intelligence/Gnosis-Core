import sqlite3, pytest
from gnosis.reflection.persistence import ensure_reflection_schema
from gnosis.storage.lineage_recovery import reconstruct_lineage

def setup(rows):
    conn=sqlite3.connect(":memory:"); ensure_reflection_schema(conn)
    for tid,fr,to in rows:
        conn.execute("INSERT INTO evolution_transitions VALUES(?,?,?,?,?,?,?,?)",(tid,"c",fr,to,"p","a","e","{}"))
    return conn

def test_lineage_is_reconstructed_by_state_links_not_rowid():
    conn=setup([("t2","s1","s2"),("t1","s0","s1")])
    assert [x.transition_id for x in reconstruct_lineage(conn)]==["t1","t2"]

def test_lineage_rejects_cycle():
    conn=setup([("t1","s0","s1"),("t2","s1","s0")])
    with pytest.raises(ValueError,match="root|cycle"):
        reconstruct_lineage(conn)

def test_lineage_rejects_disconnected_history():
    conn=setup([("t1","s0","s1"),("t2","s9","s10")])
    with pytest.raises(ValueError,match="root|disconnected"):
        reconstruct_lineage(conn)
