"""Read-only diagnostics for durable SQLite state.

These helpers report storage footprint and row counts. They do not create
schemas, run migrations, compact databases, or affect evolution decisions.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def storage_snapshot(conn: sqlite3.Connection) -> dict[str, Any]:
    """Return a reproducible, read-only snapshot of SQLite storage usage.

    Table counts include all application tables currently present in the
    database, so newly added durable record classes are measured automatically.
    database_bytes is None for in-memory databases or unavailable files.
    """
    changes_before = conn.total_changes
    database_row = conn.execute("PRAGMA database_list").fetchone()
    filename = str(database_row[2]) if database_row is not None else ""
    page_count = int(conn.execute("PRAGMA page_count").fetchone()[0])
    page_size = int(conn.execute("PRAGMA page_size").fetchone()[0])
    freelist_count = int(conn.execute("PRAGMA freelist_count").fetchone()[0])

    table_names = tuple(
        str(row[0])
        for row in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    )
    row_counts: dict[str, int] = {}
    for table_name in table_names:
        # Names originate from sqlite_master, not from caller input.
        quoted_name = '"' + table_name.replace('"', '""') + '"'
        row_counts[table_name] = int(
            conn.execute(f"SELECT COUNT(*) FROM {quoted_name}").fetchone()[0]
        )

    database_bytes: int | None = None
    if filename and filename != ":memory:":
        try:
            database_bytes = Path(filename).stat().st_size
        except OSError:
            database_bytes = None

    if conn.total_changes != changes_before:
        raise RuntimeError("storage diagnostics unexpectedly changed database rows")

    return {
        "database_bytes": database_bytes,
        "page_count": page_count,
        "page_size": page_size,
        "allocated_bytes": page_count * page_size,
        "freelist_pages": freelist_count,
        "table_rows": row_counts,
        "total_rows": sum(row_counts.values()),
    }
