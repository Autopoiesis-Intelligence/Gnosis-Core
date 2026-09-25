from gnosis.self_learning.vertical_slice import run_vertical_slice


def test_e7_15_vertical_slice_is_replayable_and_non_authoritative():
    first = run_vertical_slice()
    second = run_vertical_slice()

    assert first["status"] == "PASS"
    assert first["core_mutation"] == "NOT_EXECUTED"
    assert first["authority"] == "none"
    assert first == second
