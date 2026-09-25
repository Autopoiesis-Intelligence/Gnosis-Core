#!/usr/bin/env python3
"""Deterministic offline bootstrap validator for a Gnozis Memory Source."""
import json
from pathlib import Path

VERSION = "0.3"
REQUIRED = ["protocol_version", "source_id", "domain", "repository", "schema_versions", "license"]
VALID_STATUS = {"discovered", "registered", "authorized", "verified", "active", "quarantined", "revoked"}

def scalar(value: str) -> str:
    return value.strip().strip('"').strip("'")

def validate_manifest(errors, warnings):
    manifest = Path("SOURCE.yaml")
    if not manifest.exists():
        errors.append("missing_source_manifest")
        return
    lines = manifest.read_text(encoding="utf-8").splitlines()
    keys = {line.split(":", 1)[0].strip() for line in lines if line and not line.startswith((" ", "-", "#")) and ":" in line}
    for key in REQUIRED:
        if key not in keys:
            errors.append(f"missing_manifest_field:{key}")
    status = next((scalar(line.split(":", 1)[1]) for line in lines if line.startswith("federation_status:")), None)
    if status and status not in VALID_STATUS:
        errors.append("invalid_federation_status")
    protocol = next((scalar(line.split(":", 1)[1]) for line in lines if line.startswith("protocol_version:")), None)
    if protocol and protocol != VERSION:
        warnings.append(f"validator_protocol_mismatch:{protocol}")

def validate_declared_schemas(errors):
    schema_dir = Path("schema")
    if not schema_dir.exists():
        errors.append("missing_schema_directory")
        return
    declared = list(schema_dir.glob("*.schema.yaml")) + list(schema_dir.glob("*.schema.yml"))
    if not declared:
        errors.append("no_schema_files")
        return
    for path in declared:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            errors.append(f"empty_schema:{path}")
        if "version:" not in text:
            errors.append(f"schema_missing_version:{path}")
        if "required:" not in text:
            errors.append(f"schema_missing_required:{path}")

def main() -> int:
    errors = []
    warnings = []
    validate_manifest(errors, warnings)
    validate_declared_schemas(errors)
    result = {"validator":"gnozis-source-validator","version":VERSION,"result":"FAIL" if errors else "PASS","errors":errors,"warnings":warnings}
    Path("validation-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
