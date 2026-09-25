#!/usr/bin/env python3
"""Read-only runtime adapter for the first canonical Core case."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from gnosis.core.budget import Budget
from gnosis.core.evolution import Engine
from gnosis.core.types import Candidate, State


def sha(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode()
    ).hexdigest()


def core_revision() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--core-revision", required=True)
    p.add_argument("--execution-id", required=True)
    p.add_argument("--report")
    args = p.parse_args()

    actual = core_revision()
    if actual != args.core_revision:
        result = "BLOCKED"
        checks = [{"case": "target_revision_identity", "result": "BLOCKED"}]
    else:
        initial = State()
        engine = Engine(state=initial, budget=Budget(total=1))
        candidate = Candidate(
            parent_state_id=initial.state_id,
            proposed_state=initial.with_elements({"interface_probe": "canonical"}),
            origin="interface-bootstrap",
        )
        before = initial.state_id
        record = engine.step(candidate)
        result = "PASS" if (
            record.accepted
            and engine.state.state_id == candidate.proposed_state.state_id
            and record.from_state_id == before
            and record.to_state_id == engine.state.state_id
        ) else "FAIL"
        checks = [{
            "case": "canonical",
            "result": result,
            "accepted": record.accepted,
            "transition_id": record.transition_id,
            "from_state_id": record.from_state_id,
            "to_state_id": record.to_state_id,
        }]

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
        "input_digest": sha({"execution_id": args.execution_id, "core_revision": args.core_revision}),
        "evidence_digest": sha(evidence),
    }
    output = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.report:
        Path(args.report).write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
