#!/usr/bin/env python3
"""Deterministic offline validator for a Gnozis Memory Source."""
import json
from pathlib import Path
import hashlib

VERSION = "0.4"
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

def validate_provenance(errors, warnings):
    prov_dir = Path("provenance")
    if not prov_dir.exists():
        errors.append("missing_provenance_directory")
        return
    files = sorted([*prov_dir.glob("*.json"), *prov_dir.glob("*.jsonl")])
    if not files:
        errors.append("no_provenance_files")
        return
    for path in files:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"invalid_provenance_json:{path}:{n}")
                continue
            for key in ("source_id", "source_revision", "record_id"):
                if not item.get(key):
                    errors.append(f"missing_provenance_field:{path}:{n}:{key}")
            digest = item.get("content_sha256")
            if digest and (len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest)):
                errors.append(f"invalid_content_sha256:{path}:{n}")
            if item.get("source_revision", "").startswith(("refs/heads/", "refs/tags/")):
                warnings.append(f"mutable_or_symbolic_revision:{path}:{n}")

def main() -> int:
    errors = []
    warnings = []
    validate_manifest(errors, warnings)
    validate_declared_schemas(errors)
    validate_provenance(errors, warnings)
    result = {"validator":"gnozis-source-validator","version":VERSION,"result":"FAIL" if errors else "PASS","errors":errors,"warnings":warnings}
    Path("validation-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
