from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate
from gnosis.evolution.directory_shadow import shadow_directory_optimization


def _candidate():
    return build_duplicate_candidate(["a", "b"], "digest", {
        "b": DirectoryUsage("b", provenance_id="p1"),
    })


def test_shadow_is_read_only_and_reports_delta() -> None:
    candidate = _candidate()
    result = shadow_directory_optimization(
        candidate,
        {"b": DirectoryUsage("b", provenance_id="p1")},
        observed_file_count=10,
    )
    assert result.accepted
    assert result.before_count == 10
    assert result.after_count == 9
    assert result.removed_count == 1


def test_shadow_fails_closed_on_evidence_tampering() -> None:
    candidate = _candidate()
    result = shadow_directory_optimization(
        candidate,
        {"b": DirectoryUsage("b", protected=True, provenance_id="p1")},
        observed_file_count=10,
    )
    assert not result.accepted
    assert result.removed_count == 0
    assert result.after_count == 9
