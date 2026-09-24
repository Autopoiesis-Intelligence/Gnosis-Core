import pytest
from gnosis.self_learning.transfer_boundary import create_transfer_manifest,may_transfer,includes_internal_memory,grants_execution_authority
def make(status="APPROVED"): return create_transfer_manifest(contract_id="c:1",partner_scope="partner:a",core_artifacts=("core/minimal.zip",),evidence_artifacts=("evidence/report.json",),excluded_artifacts=("AI_CONTEXT","Research-Memory"),transfer_policy="minimum contracted artifacts",status=status)
def test_approved_transfer_requires_ready_contract(): assert may_transfer(manifest=make(),contract_ready=True)
def test_not_ready_blocks(): assert not may_transfer(manifest=make(),contract_ready=False)
def test_memory_excluded(): assert not includes_internal_memory(manifest=make())
def test_memory_cannot_be_core():
 with pytest.raises(ValueError): create_transfer_manifest(contract_id="c",partner_scope="partner:a",core_artifacts=("Research-Memory/context.json",),evidence_artifacts=("e",),excluded_artifacts=("AI_CONTEXT",),transfer_policy="p")
def test_explicit_exclusion_required():
 with pytest.raises(ValueError): create_transfer_manifest(contract_id="c",partner_scope="partner:a",core_artifacts=("core.zip",),evidence_artifacts=(),excluded_artifacts=(),transfer_policy="p")
def test_no_authority(): assert not grants_execution_authority(manifest=make())
def test_deterministic(): assert make()==make()
