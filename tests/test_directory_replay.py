from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate
from gnosis.evolution.directory_provenance import build_directory_provenance
from gnosis.evolution.directory_replay import verify_directory_replay


def _candidate():
    return build_duplicate_candidate(["a", "b"], "digest", {
        "b": DirectoryUsage("b", provenance_id="p1"),
    })


def _provenance(candidate):
    return build_directory_provenance(
        candidate=candidate,
        parent_state_id="s0",
        parent_state_digest="parent",
        proposed_state_digest="next",
    )


def _kwargs():
    return dict(
        parent_state_id="s0",
        parent_state_digest="parent",
        proposed_state_digest="next",
        evaluation_status="PENDING",
        shadow_status="NOT_RUN",
        invariant_status="PENDING",
        governance_decision="PENDING",
    )


def test_directory_replay_accepts_same_identity() -> None:
    candidate = _candidate()
    assert verify_directory_replay(candidate, _provenance(candidate), **_kwargs()).reproducible


def test_directory_replay_rejects_new_parent_state() -> None:
    candidate = _candidate()
    result = verify_directory_replay(
        candidate, _provenance(candidate),
        **{**_kwargs(), "parent_state_id": "new-state"},
    )
    assert not result.reproducible


def test_directory_replay_rejects_changed_proposed_state() -> None:
    candidate = _candidate()
    result = verify_directory_replay(
        candidate, _provenance(candidate),
        **{**_kwargs(), "proposed_state_digest": "tampered"},
    )
    assert not result.reproducible
