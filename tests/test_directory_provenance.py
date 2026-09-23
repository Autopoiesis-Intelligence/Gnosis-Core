from gnosis.evolution.directory_candidate import DirectoryUsage, build_duplicate_candidate
from gnosis.evolution.directory_provenance import build_directory_provenance, verify_directory_provenance


def _candidate():
    return build_duplicate_candidate(["a", "b"], "digest", {
        "b": DirectoryUsage("b", provenance_id="p1"),
    })


def test_directory_provenance_binds_candidate() -> None:
    candidate = _candidate()
    provenance = build_directory_provenance(
        candidate=candidate,
        parent_state_id="s0",
        parent_state_digest="parent",
        proposed_state_digest="next",
    )
    assert provenance.candidate_id == candidate.candidate_id
    assert provenance.candidate_binding_digest == candidate.candidate_binding_digest
    assert verify_directory_provenance(
        provenance, candidate,
        parent_state_id="s0",
        parent_state_digest="parent",
        proposed_state_digest="next",
        evaluation_status="PENDING",
        shadow_status="NOT_RUN",
        invariant_status="PENDING",
        governance_decision="PENDING",
    )


def test_directory_provenance_rejects_candidate_tampering() -> None:
    candidate = _candidate()
    provenance = build_directory_provenance(
        candidate=candidate,
        parent_state_id="s0",
        parent_state_digest="parent",
        proposed_state_digest="next",
    )
    tampered = build_duplicate_candidate(["a", "b"], "different", {
        "b": DirectoryUsage("b", provenance_id="p1"),
    })
    assert not verify_directory_provenance(
        provenance, tampered,
        parent_state_id="s0",
        parent_state_digest="parent",
        proposed_state_digest="next",
        evaluation_status="PENDING",
        shadow_status="NOT_RUN",
        invariant_status="PENDING",
        governance_decision="PENDING",
    )
