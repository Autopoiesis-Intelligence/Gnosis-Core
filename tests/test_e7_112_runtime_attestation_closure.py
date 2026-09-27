from dataclasses import replace

from gnosis.self_learning.e7_112_immutable_closure import create_closure, verify_closure, ClosureState
from gnosis.self_learning.e7_114_runtime_attestation import compute_attestation_digest, RuntimeAttestation
from gnosis.self_learning.e7_113_execute_bounded_proof import _object_digest


def _attestation():
    payload = {
        "repository_root": "/repo",
        "actual_head_sha": "abc",
        "expected_commit_sha": "abc",
        "status": "PASS",
    }
    return RuntimeAttestation(
        "/repo", "abc", "abc", "PASS", compute_attestation_digest(payload)
    )


def test_attestation_tamper_breaks_existing_closure():
    attestation = _attestation()
    chain = ("D107", "D108", "D109", "D110", "D111", _object_digest(attestation))
    closure = create_closure(
        batch_id="B",
        target_commit_sha="abc",
        chain_digests=chain,
    )
    assert closure.state is ClosureState.CLOSED
    assert verify_closure(closure, chain, batch_id="B", target_commit_sha="abc")

    tampered = replace(attestation, actual_head_sha="def")
    tampered_chain = ("D107", "D108", "D109", "D110", "D111", _object_digest(tampered))
    assert not verify_closure(
        closure, tampered_chain, batch_id="B", target_commit_sha="abc"
    )


def test_attestation_digest_tamper_breaks_existing_closure():
    attestation = _attestation()
    chain = ("D107", "D108", "D109", "D110", "D111", _object_digest(attestation))
    closure = create_closure(batch_id="B", target_commit_sha="abc", chain_digests=chain)

    tampered = replace(attestation, evidence_digest="0" * 64)
    tampered_chain = ("D107", "D108", "D109", "D110", "D111", _object_digest(tampered))
    assert not verify_closure(closure, tampered_chain, batch_id="B", target_commit_sha="abc")
