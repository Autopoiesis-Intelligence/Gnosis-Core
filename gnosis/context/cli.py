"""Machine-readable project snapshot and durable task-context recovery entry point."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from dataclasses import asdict

from .repository import TaskContextRepository
from .snapshot import build_context_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Emit a read-only project snapshot or reconstruct a durable task context"
    )
    parser.add_argument("--root", default=".", help="project checkout root for snapshot mode")
    parser.add_argument(
        "--context-db",
        help="SQLite database containing task_contexts; required with --context-id",
    )
    parser.add_argument(
        "--context-id",
        help="durable context identifier to reconstruct; requires --context-db",
    )
    args = parser.parse_args()

    if bool(args.context_db) != bool(args.context_id):
        parser.error("--context-db and --context-id must be supplied together")

    if args.context_id:
        # Use a plain SQLite connection so recovery does not initialize or migrate
        # Core/Reflection schemas as a side effect of opening the database.
        db_path = Path(args.context_db).resolve()
        if not db_path.is_file():
            raise SystemExit(f"context database file does not exist: {db_path}")
        # Recovery is read-only: do not create missing files or mutate stored state.
        conn = sqlite3.connect(f"{db_path.as_uri()}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        try:
            # Recovery must not create even the Context schema when pointed at
            # an unrelated or empty database.
            context_table = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='task_contexts'"
            ).fetchone()
            if context_table is None:
                raise SystemExit("context database does not contain task_contexts table")
            handoff = TaskContextRepository(conn).reconstruct_context(args.context_id)
            print(json.dumps(asdict(handoff), ensure_ascii=False, indent=2, sort_keys=True))
        finally:
            conn.close()
        return

    print(json.dumps(build_context_snapshot(args.root), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
