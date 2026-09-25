import hashlib
import json
from pathlib import Path


def _git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def test_canonical_core_source_manifest_matches_exact_blobs():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (root / "contracts" / "core_source_integrity_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    for relative, expected in manifest["artifacts"].items():
        path = root / relative
        assert path.is_file(), f"missing canonical artifact: {relative}"
        actual = _git_blob_sha1(path.read_bytes())
        assert actual == expected, f"canonical source mismatch: {relative}"


def test_manifest_is_bound_to_a_specific_source_commit():
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (root / "contracts" / "core_source_integrity_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert len(manifest["source_commit"]) == 40
    assert manifest["basis"] == "git-blob-sha1"
