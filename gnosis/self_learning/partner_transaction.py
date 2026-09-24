"""E8.25 runtime transaction integration probe."""
from __future__ import annotations
from contextlib import contextmanager
import sqlite3
from gnosis.storage.database import transaction

@contextmanager
def partner_learning_transaction(conn: sqlite3.Connection, *, failure_point: str | None = None):
    """Reuse the canonical SQLite transaction boundary; inject failure before commit."""
    with transaction(conn):
        if failure_point in {"begin", "write", "audit", "head"}:
            raise RuntimeError(f"E8.25 injected failure: {failure_point}")
        yield conn
        if failure_point == "commit":
            raise RuntimeError("E8.25 injected failure: commit")
