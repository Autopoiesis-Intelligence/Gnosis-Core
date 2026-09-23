from gnosis.core import (
    Candidate,
    Relation,
    State,
    all_pass,
    run_invariants,
)


def make_current():
    return State(elements={"a": 1}, version=0)


def test_valid_candidate_passes_all_invariants():
    current = make_current()
    proposed = current.with_elements({"b": 2})
    candidate = Candidate(
        parent_state_id=current.state_id, proposed_state=proposed, origin="test"
    )
    results = run_invariants(current, candidate)
    assert all_pass(results)


def test_candidate_with_wrong_parent_fails_state_integrity():
    current = make_current()
    other = State(elements={"z": 9}, version=0)
    proposed = other.with_elements({"b": 2})
    candidate = Candidate(
        parent_state_id=other.state_id,  # does not match `current`
        proposed_state=proposed,
        origin="test",
    )
    results = run_invariants(current, candidate)
    assert not all_pass(results)
    names = {r.name for r in results if not r.ok}
    assert "state_integrity" in names


def test_candidate_with_dangling_relation_fails_transition_validity():
    current = make_current()
    proposed_state = State(
        elements={"a": 1},
        relations=(Relation(source="a", target="does_not_exist", relation_type="x"),),
        version=1,
    )
    candidate = Candidate(
        parent_state_id=current.state_id, proposed_state=proposed_state, origin="test"
    )
    results = run_invariants(current, candidate)
    assert not all_pass(results)
    names = {r.name for r in results if not r.ok}
    assert "transition_validity" in names


def test_candidate_with_non_increasing_version_fails():
    current = make_current()
    proposed_state = State(elements={"a": 1, "b": 2}, version=0)  # same version
    candidate = Candidate(
        parent_state_id=current.state_id, proposed_state=proposed_state, origin="test"
    )
    results = run_invariants(current, candidate)
    assert not all_pass(results)
    names = {r.name for r in results if not r.ok}
    assert "monotonic_version" in names


def test_state_canonicalizes_relation_set_and_exposes_psi_identity():
    r1 = Relation(source="a", target="b", relation_type="depends")
    r2 = Relation(source="b", target="a", relation_type="depends")
    state_a = State(elements={"a": 1, "b": 2}, relations=(r2, r1, r1), version=7)
    state_b = State(elements={"a": 1, "b": 2}, relations=(r1, r2), version=7)

    assert state_a.relations == state_b.relations
    assert len(state_a.relations) == 2
    assert state_a.content_id == state_b.content_id
    assert state_a.psi_id == state_a.content_id

def test_version_is_lineage_metadata_not_psi_content():
    base = State(elements={"a": 1}, version=0)
    next_version = State(elements={"a": 1}, version=100)

    assert base.content_id == next_version.content_id
    assert base.psi_id == next_version.psi_id
    assert base.state_id != next_version.state_id

def test_negative_version_is_rejected():
    try:
        State(elements={"a": 1}, version=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative State.version must be rejected")
