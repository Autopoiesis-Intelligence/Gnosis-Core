#!/usr/bin/env python3
"""Minimal contract runner for CORE-MUTATION-BOUNDARY-01.

This runner is intentionally read-only with respect to repository files and emits
a deterministic JSON report. It must be executed from a checkout containing the
declared Core revision. It does not claim runtime verification until executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


def git_sha() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], text=True
    ).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-revision", required=True)
    parser.add_argument("--execution-id", required=True)
    parser.add_argument("--report", default=None)
    args = parser.parse_args()

    actual = git_sha()
    if actual != args.core_revision:
        result = "BLOCKED"
        reason = "checkout HEAD does not match declared Core revision"
        checks = [{"case": "target_revision_identity", "result": result, "reason": reason}]
    else:
        # The executable cases are deliberately delegated to the repository's
        # test/runtime surface. This bootstrap does not invent a second Core.
        result = "NOT_IMPLEMENTED"
        reason = "runtime case adapter is not yet implemented"
        checks = [{"case": "runtime_adapter", "result": result, "reason": reason}]

    evidence = {
        "execution_id": args.execution_id,
        "contract_id": "CORE-MUTATION-BOUNDARY-01",
        "contract_version": "1.0",
        "core_revision": actual,
        "declared_core_revision": args.core_revision,
        "checks": checks,
    }
    record = {
        **evidence,
        "result": result,
        "input_digest": digest({
            "contract_id": evidence["contract_id"],
            "core_revision": args.core_revision,
            "execution_id": args.execution_id,
        }),
        "evidence_digest": digest(evidence),
    }
    output = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.report:
        Path(args.report).write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result == "NOT_IMPLEMENTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
