from gnosis.core.types import State, TestResult
from gnosis.core.execution_input import execution_input_from_state
from gnosis.core.execution_identity import (
    ExecutionIdentity,
    execution_identity_from_input,
    verify_execution_identity_from_input,
)
from gnosis.core.check_identity import CheckIdentity


def _check():
    return CheckIdentity("rule:1", "obligation:1", "check:1")


def test_execution_input_round_trip():
    s = State({"x": 1}, (), 1)
    i = execution_input_from_state(s)
    assert i.digest
    assert i.digest == execution_input_from_state(s).digest


def test_state_substitution_detected():
    a = State({"x": 1}, (), 1)
    b = State({"x": 2}, (), 1)
    i = execution_input_from_state(a)
    assert i != execution_input_from_state(b)


def test_context_type_is_bound():
    s = State({"x": 1}, (), 1)
    sandbox = execution_input_from_state(s, "sandbox")
    commit = execution_input_from_state(s, "commit")
    assert sandbox.digest != commit.digest


def test_canonical_digest_binds_all_identity_fields():
    s = State({"x": 1}, (), 1)
    base = execution_input_from_state(s, "sandbox")
    variants = [
        base.__class__("commit", base.state_id, base.state_digest, base.content_digest),
        base.__class__(base.input_type, "other", base.state_digest, base.content_digest),
        base.__class__(base.input_type, base.state_id, "other", base.content_digest),
        base.__class__(base.input_type, base.state_id, base.state_digest, "other"),
    ]
    assert len({base.digest, *(item.digest for item in variants)}) == 5


def test_execution_identity_is_derived_from_execution_input():
    s = State({"x": 1}, (), 1)
    execution_input = execution_input_from_state(s, "sandbox")
    result = TestResult(True, ())
    identity = execution_identity_from_input(
        _check(), execution_input, {"sandbox": True}, result
    )
    assert identity.input_digest == execution_input.digest
    assert verify_execution_identity_from_input(
        identity, _check(), execution_input, {"sandbox": True}, result
    )


def test_execution_identity_rejects_input_substitution():
    s = State({"x": 1}, (), 1)
    original = execution_input_from_state(s, "sandbox")
    replacement = execution_input_from_state(s, "commit")
    result = TestResult(True, ())
    identity = execution_identity_from_input(
        _check(), original, {"sandbox": True}, result
    )
    assert not verify_execution_identity_from_input(
        identity, _check(), replacement, {"sandbox": True}, result
    )
