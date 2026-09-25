#!/usr/bin/env python3
"""Bootstrap deterministic validator for a Gnozis Memory Source.

No network access and no Kernel credentials are required.
"""
import json
from pathlib import Path

VERSION = "0.1"
REQUIRED = ["protocol_version", "source_id", "domain", "repository", "schema_versions", "license"]
VALID_STATUS = {"discovered", "registered", "authorized", "verified", "active", "quarantined", "revoked"}

def main() -> int:
    root = Path(".")
    errors = []
    warnings = []
    manifest = root / "SOURCE.yaml"
    if not manifest.exists():
        errors.append("missing_source_manifest")
    else:
        # Deliberately minimal parser: this validator only checks required YAML keys.
        keys = set()
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith((" ", "-", "#")) and ":" in line:
                keys.add(line.split(":", 1)[0].strip())
        for key in REQUIRED:
            if key not in keys:
                errors.append(f"missing_manifest_field:{key}")
        status = None
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if line.startswith("federation_status:"):
                status = line.split(":", 1)[1].strip().strip('"')
        if status and status not in VALID_STATUS:
            errors.append("invalid_federation_status")

    result = {
        "validator": "gnozis-source-validator",
        "version": VERSION,
        "result": "FAIL" if errors else "PASS",
        "errors": errors,
        "warnings": warnings,
    }
    Path("validation-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
