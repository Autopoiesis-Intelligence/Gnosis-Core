from gnosis.self_learning.e7_106_candidate_inventory import (
    CandidateInventory,
    CandidateInventoryEntry,
    progress_credit_from_selection,
)


SHA = "beb8463410865bcaff8f4c48440b5311b56e0d6a"


def entry(candidate_id="candidate-observe"):
    return CandidateInventoryEntry(
        candidate_id=candidate_id,
        contract_id="E7.91/E7.92",
        contract_revision="r1",
        current_status="IMPLEMENTED",
        dependency_status="READY",
        implementation_paths=(
            "gnosis/self_learning/candidate_contract.py",
            "gnosis/self_learning/shadow_evaluation.py",
        ),
        mapped_criteria=("candidate-integrity", "shadow-evaluation"),
        test_paths=(
            "tests/test_candidate_contract.py",
            "tests/test_shadow_evaluation.py",
        ),
        runtime_requirements=("python>=3.11", "pytest"),
        evidence_ids=("candidate-tests", "shadow-tests"),
        evidence_commits=(SHA,),
        known_gaps=("system-level E7 execution binding",),
        trust_boundary_relevance="candidate authority boundary",
        execution_prerequisites=("exact commit checkout",),
        execution_mode="OBSERVE_ONLY",
        selection_state="RESERVE",
        selection_rationale="existing implementation and executable tests",
    )


def test_inventory_is_deterministic_and_exact_commit_bound():
    inventory = CandidateInventory.build(
        target_repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        target_ref="beb8463",
        target_commit=SHA,
        entries=(entry(),),
    )
    again = CandidateInventory.build(
        target_repository=inventory.target_repository,
        target_ref=inventory.target_ref,
        target_commit=inventory.target_commit,
        entries=inventory.entries,
    )
    assert inventory.inventory_id == again.inventory_id
    assert inventory.validate_exact_commit()


def test_only_observe_only_candidate_can_be_selected():
    inventory = CandidateInventory.build(
        target_repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        target_ref="beb8463",
        target_commit=SHA,
        entries=(entry(),),
    )
    selected = inventory.select_observe_only(candidate_id="candidate-observe")
    assert [e.candidate_id for e in selected.selected()] == ["candidate-observe"]


def test_mutating_candidate_is_blocked():
    candidate = entry("mutating")
    mutating = CandidateInventoryEntry(
        **{**candidate.__dict__, "execution_mode": "MUTATING"}
    )
    inventory = CandidateInventory.build(
        target_repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        target_ref="beb8463",
        target_commit=SHA,
        entries=(mutating,),
    )
    try:
        inventory.select_observe_only(candidate_id="mutating")
    except ValueError as exc:
        assert str(exc) == "only observe-only candidates may be selected"
    else:
        raise AssertionError("mutating candidate must remain blocked")


def test_selection_grants_no_progress_credit():
    inventory = CandidateInventory.build(
        target_repository="Mikhail-Kucheriavyi-23/Gnozis-Genesis",
        target_ref="beb8463",
        target_commit=SHA,
        entries=(entry(),),
    )
    selected = inventory.select_observe_only(candidate_id="candidate-observe")
    assert progress_credit_from_selection(selected) == 0
