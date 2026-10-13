from gnosis.storage import connect, save_instance
from gnosis.storage.diagnostics import storage_snapshot
from gnosis.core import State
from gnosis.instances.instance import Instance


def test_storage_snapshot_reports_durable_tables_without_mutating_database():
    conn = connect()
    instance = Instance.create_root("diagnostics-test", State(elements={"root": 1}))
    save_instance(conn, instance)
    changes_before = conn.total_changes

    first = storage_snapshot(conn)
    second = storage_snapshot(conn)

    assert first == second
    assert first["database_bytes"] is None
    assert first["page_count"] > 0
    assert first["page_size"] > 0
    assert first["allocated_bytes"] == first["page_count"] * first["page_size"]
    assert first["table_rows"]["states"] == 1
    assert first["table_rows"]["instances"] == 1
    assert first["table_rows"]["audit_events"] == 1
    assert first["total_rows"] == sum(first["table_rows"].values())
    assert conn.total_changes == changes_before
    conn.close()


def test_storage_snapshot_reports_file_size_for_persisted_database(tmp_path):
    path = tmp_path / "diagnostics.sqlite"
    conn = connect(path)
    instance = Instance.create_root("diagnostics-test", State(elements={"root": 1}))
    save_instance(conn, instance)

    snapshot = storage_snapshot(conn)

    assert snapshot["database_bytes"] == path.stat().st_size
    assert snapshot["database_bytes"] > 0
    assert snapshot["table_rows"]["audit_events"] == 1
    conn.close()


def test_storage_snapshot_counts_application_tables_added_after_connection():
    conn = connect()
    conn.execute("CREATE TABLE diagnostics_fixture (id INTEGER PRIMARY KEY)")
    conn.execute("INSERT INTO diagnostics_fixture DEFAULT VALUES")
    before = conn.total_changes

    snapshot = storage_snapshot(conn)

    assert snapshot["table_rows"]["diagnostics_fixture"] == 1
    assert conn.total_changes == before
    conn.close()
