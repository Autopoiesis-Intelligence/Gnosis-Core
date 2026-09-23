#!/usr/bin/env python3
"""Build the continuously refreshed partner-facing current contract block."""
from __future__ import annotations
import argparse, hashlib, re
from datetime import datetime, timezone
from pathlib import Path

ROW = re.compile(r"^\|\s*(E[0-9A-Za-z.\-]+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")

def read_registry(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ROW.match(line)
        if m and m.group(1).startswith("E"):
            rows.append({"contract_id": m.group(1), "status": m.group(2).strip(), "title": m.group(3).strip()})
    return sorted({x["contract_id"]: x for x in rows}.values(), key=lambda x: x["contract_id"])

def build(registry: Path, source_revision: str | None) -> str:
    contracts = read_registry(registry)
    generated = datetime.now(timezone.utc).isoformat()
    body = "\n".join(f"| {x['contract_id']} | {x['status']} | {x['title']} |" for x in contracts)
    digest = hashlib.sha256(body.encode()).hexdigest()
    revision = source_revision or "UNSPECIFIED"
    return f"""# Current Partner Contract Block

> GENERATED FILE — update with scripts/update_partner_contract_block.py.
> This block is the current machine-readable partner contract index. It is not an authority root and does not grant access or execution rights.

- Generated at (UTC): {generated}
- Source revision: {revision}
- Contract index digest: sha256:{digest}
- Authority: index_only
- Provenance: partner-contract-current-block

## Active Contract Index

| Contract ID | Status | Contract |
|---|---|---|
{body}

## Partner Boundary

Partner repositories/databases are external learning and evidence surfaces. They do not become a second Ψ-Core, authority root, or direct state writer.

Current flow:

Partner Repository -> Partner DB -> Provenance/Audit -> Quarantine -> Evidence -> Candidate -> Core Verification -> Governed Evolution

This generated block intentionally contains contract metadata rather than private partner/user payloads.
"""

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--source-revision", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    registry = root / "docs/partners/PARTNER_CONTRACT_REGISTRY.md"
    target = root / "docs/partners/CURRENT_PARTNER_CONTRACT_BLOCK.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(build(registry, args.source_revision), encoding="utf-8")
    print(target)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
