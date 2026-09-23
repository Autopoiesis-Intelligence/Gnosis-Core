#!/usr/bin/env python3
"""Generate the machine-readable partner contract database."""
from __future__ import annotations

import argparse
from pathlib import Path

from gnosis.self_learning import build_contract_database, write_contract_database


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--source-revision", default=None)
    parser.add_argument("--scope-prefix", default="E7.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    database = build_contract_database(root, scope_prefix=args.scope_prefix)
    output, log = write_contract_database(
        database,
        root,
        source_revision=args.source_revision,
    )
    print(f"database={output}")
    print(f"log={log}")
    print(f"contracts={len(database.contracts)}")
    print(f"findings={len(database.findings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
