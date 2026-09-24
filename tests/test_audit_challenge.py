import pytest
from gnosis.self_learning.audit_challenge import create_challenge,may_mark_resolved,preserves_challenge_history
def make(status="OPEN",digest="sha256:pkg",resolution=()):
    return create_challenge(attestation_id="att:1",package_id="pkg:1",challenger_id="challenger:1",challenged_digest=digest,claim="scope mismatch",evidence_refs=("challenge:e1",),status=status,resolution_refs=resolution)
def test_open_challenge_preserves_history(): assert preserves_challenge_history(challenge=make())
def test_resolved_requires_resolution_evidence():
    with pytest.raises(ValueError): make("RESOLVED")
def test_resolved_matching_digest(): assert may_mark_resolved(challenge=make("RESOLVED",resolution=("resolution:1",)),package_digest="sha256:pkg")
def test_digest_mismatch_not_resolved(): assert not may_mark_resolved(challenge=make("RESOLVED","sha256:other",("resolution:1",)),package_digest="sha256:pkg")
def test_open_not_resolved(): assert not may_mark_resolved(challenge=make(),package_digest="sha256:pkg")
def test_deterministic(): assert make()==make()
