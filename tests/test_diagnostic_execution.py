import json

from diagnostic_corpus.generate import generate


def test_self_diagnostic_generator_executes_end_to_end(tmp_path):
    root = generate(tmp_path / "SELF-DIAGNOSTIC-0001")
    metadata = json.loads((root / "metadata.json").read_text(encoding="utf-8"))
    transitions = json.loads((root / "transitions.json").read_text(encoding="utf-8"))
    artifact = json.loads((root / "diagnostic.json").read_text(encoding="utf-8"))

    assert metadata["persistence"] == "sqlite_round_trip"
    assert metadata["transition_count"] == 4
    assert metadata["accepted_count"] == 1
    assert metadata["rejected_count"] == 3
    assert len(transitions) == 4
    assert artifact["artifact_id"] == "SELF-DIAGNOSTIC-0001"
    assert "causal_candidates" in artifact
    assert artifact["report"]["observations"]
    assert all("provenance" in observation for observation in artifact["report"]["observations"])
    assert "limitations" in artifact


def test_self_diagnostic_output_boundary_smoke(tmp_path):
    root = generate(tmp_path / "SMOKE")
    assert root.is_dir()
    assert (root / "metadata.json").is_file()
    assert (root / "transitions.json").is_file()
    assert (root / "diagnostic.json").is_file()
