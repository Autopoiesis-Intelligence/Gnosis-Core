#!/usr/bin/env python3
"""Deterministic offline validator for a Gnozis Memory Source."""
import hashlib
import json
from pathlib import Path

VERSION = "0.7"
REQUIRED = ["protocol_version", "source_id", "domain", "repository", "schema_versions", "license"]
VALID_STATUS = {"discovered", "registered", "authorized", "verified", "active", "quarantined", "revoked"}
VALID_RELATION_STATES = {"unverified", "source_validated", "independently_verified", "disputed", "rejected", "withdrawn"}
REQUIRED_RELATION = ["relation_id", "subject", "predicate", "object", "source_id", "source_revision", "provenance", "verification_state", "schema_version"]
VALID_LICENSE_MARKERS = {"MIT", "Apache-2.0", "GPL-2.0", "GPL-3.0", "LGPL-2.1", "LGPL-3.0", "MPL-2.0", "BSD-2-Clause", "BSD-3-Clause", "CC-BY-4.0", "CC-BY-SA-4.0", "CC0-1.0", "Unlicense"}

def scalar(value: str) -> str:
    return value.strip().strip('"').strip("'")

def validate_manifest(errors):
    manifest = Path("SOURCE.yaml")
    if not manifest.exists(): errors.append("missing_source_manifest"); return
    lines = manifest.read_text(encoding="utf-8").splitlines()
    keys = {line.split(":", 1)[0].strip() for line in lines if line and not line.startswith((" ", "-", "#")) and ":" in line}
    for key in REQUIRED:
        if key not in keys: errors.append(f"missing_manifest_field:{key}")
    status = next((scalar(line.split(":", 1)[1]) for line in lines if line.startswith("federation_status:")), None)
    if status and status not in VALID_STATUS: errors.append("invalid_federation_status")

def validate_declared_schemas(errors):
    schema_dir = Path("schema")
    if not schema_dir.exists(): errors.append("missing_schema_directory"); return
    declared = list(schema_dir.glob("*.schema.yaml")) + list(schema_dir.glob("*.schema.yml"))
    if not declared: errors.append("no_schema_files"); return
    for path in declared:
        text = path.read_text(encoding="utf-8").strip()
        if not text: errors.append(f"empty_schema:{path}")
        if "version:" not in text: errors.append(f"schema_missing_version:{path}")
        if "required:" not in text: errors.append(f"schema_missing_required:{path}")

def load_json_records(directory, errors, prefix):
    files = sorted([*directory.glob("*.json"), *directory.glob("*.jsonl")]) if directory.exists() else []
    if not directory.exists(): errors.append(f"missing_{prefix}_directory")
    elif not files: errors.append(f"no_{prefix}_files")
    for path in files:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip(): continue
            try: yield path, n, json.loads(line)
            except json.JSONDecodeError: errors.append(f"invalid_{prefix}_json:{path}:{n}")

def validate_provenance(errors, warnings):
    for path, n, item in load_json_records(Path("provenance"), errors, "provenance") or []:
        for key in ("source_id", "source_revision", "record_id"):
            if not item.get(key): errors.append(f"missing_provenance_field:{path}:{n}:{key}")
        digest = item.get("content_sha256")
        if digest and (len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest)): errors.append(f"invalid_content_sha256:{path}:{n}")
        if item.get("source_revision", "").startswith(("refs/heads/", "refs/tags/")): warnings.append(f"mutable_or_symbolic_revision:{path}:{n}")

def validate_relations(errors):
    for path, n, item in load_json_records(Path("relations"), errors, "relation") or []:
        for key in REQUIRED_RELATION:
            if key not in item or item[key] in (None, "", []): errors.append(f"missing_relation_field:{path}:{n}:{key}")
        if item.get("verification_state") not in VALID_RELATION_STATES: errors.append(f"invalid_verification_state:{path}:{n}")
        for ref in ("subject", "object"):
            if not isinstance(item.get(ref), dict) or not item[ref].get("source_id") or not item[ref].get("resource_id"): errors.append(f"invalid_relation_reference:{path}:{n}:{ref}")

def validate_integrity(errors):
    for path, n, item in load_json_records(Path("provenance"), errors, "provenance") or []:
        digest, content_path = item.get("content_sha256"), item.get("content_path")
        if digest and content_path:
            target = Path(content_path)
            if not target.is_file(): errors.append(f"missing_integrity_target:{path}:{n}"); continue
            if hashlib.sha256(target.read_bytes()).hexdigest().lower() != digest.lower(): errors.append(f"content_digest_mismatch:{path}:{n}")

def validate_license(errors, warnings):
    manifest = Path("SOURCE.yaml")
    if not manifest.exists(): return
    lines = manifest.read_text(encoding="utf-8").splitlines()
    license_value = next((scalar(line.split(":", 1)[1]) for line in lines if line.startswith("license:")), "")
    if not license_value: errors.append("missing_license_value"); return
    license_file = Path("LICENSE")
    if not license_file.exists(): warnings.append("missing_license_file")
    if license_value.lower() in {"proprietary", "custom", "unknown"}: warnings.append(f"nonstandard_license_marker:{license_value}")
    elif license_value not in VALID_LICENSE_MARKERS: warnings.append(f"unrecognized_license_marker:{license_value}")

def main() -> int:
    errors, warnings = [], []
    validate_manifest(errors); validate_declared_schemas(errors); validate_provenance(errors, warnings); validate_relations(errors); validate_integrity(errors); validate_license(errors, warnings)
    result = {"validator":"gnozis-source-validator","version":VERSION,"result":"FAIL" if errors else "PASS","errors":errors,"warnings":warnings}
    Path("validation-result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2)); return 1 if errors else 0

if __name__ == "__main__": raise SystemExit(main())
