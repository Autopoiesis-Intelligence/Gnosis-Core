from gnosis.self_learning.audit_package import create_audit_package,package_is_auditable,package_is_public_safe
def make(status="SEALED",privacy="REDACTED"):
    return create_audit_package(contract_id="E7.84",evidence_refs=("e1",),included_artifacts=("contract.json","evidence.json"),redacted_artifacts=("private.json",),scope="audit:contract",privacy_classification=privacy,source_digest="sha256:src",export_revision="r1",status=status)
def test_sealed_is_auditable(): assert package_is_auditable(package=make())
def test_prepared_is_not_auditable(): assert not package_is_auditable(package=make("PREPARED"))
def test_public_safe_classification(): assert package_is_public_safe(package=make())
def test_private_is_not_public_safe(): assert not package_is_public_safe(package=make("SEALED","PRIVATE"))
def test_deterministic(): assert make()==make()
