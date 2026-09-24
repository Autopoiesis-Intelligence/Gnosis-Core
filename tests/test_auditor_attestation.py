from gnosis.self_learning.auditor_attestation import create_attestation,attestation_is_valid,attestation_grants_authority
def make(status="VERIFIED",digest="sha256:pkg"):
    return create_attestation(package_id="pkg:1",auditor_id="auditor:1",verified_digest=digest,verification_scope="package:integrity",evidence_refs=("audit:e1",),finding_refs=(),status=status)
def test_verified_matching_digest(): assert attestation_is_valid(attestation=make(),package_digest="sha256:pkg")
def test_mismatched_digest_invalid(): assert not attestation_is_valid(attestation=make(),package_digest="sha256:other")
def test_pending_invalid(): assert not attestation_is_valid(attestation=make("PENDING"),package_digest="sha256:pkg")
def test_rejected_invalid(): assert not attestation_is_valid(attestation=make("REJECTED"),package_digest="sha256:pkg")
def test_attestation_never_grants_authority(): assert not attestation_grants_authority(attestation=make())
def test_deterministic(): assert make()==make()
