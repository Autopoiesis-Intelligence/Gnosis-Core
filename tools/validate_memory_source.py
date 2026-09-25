#!/usr/bin/env python3
"""Deterministic offline bootstrap validator for a Gnozis Memory Source."""
import json
from pathlib import Path

VERSION = "0.1"
REQUIRED = ["protocol_version", "source_id", "domain", "repository", "schema_versions", "license"]
VALID_STATUS = {"discovered", "registered", "authorized", "verified", "active", "quarantined", "revoked"}

def main() -> int:
    errors = []
    manifest = Path("SOURCE.yaml")
    if not manifest.exists():
        errors.append("missing_source_manifest")
    else:
        lines = manifest.read_text(encoding="utf-8").splitlines()
        keys = {line.split(":", 1)[0].strip() for line in lines if line and not line.startswith((" ", "-", "#")) and ":" in line}
        for key in REQUIRED:
            if key not in keys:
                errors.append(f"missing_manifest_field:{key}")
        status = next((line.split(":", 1)[1].strip().strip('"') for line in lines if line.startswith("federation_status:")), None)
        if status and status not in VALID_STATUS:
            errors.append("invalid_federation_status")
    result = {"validator":"gnozis-source-validator","version":VERSION,"result":"FAIL" if errors else "PASS","errors":errors}
    Path("validation-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
