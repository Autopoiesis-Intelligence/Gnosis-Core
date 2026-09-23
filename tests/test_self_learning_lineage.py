import pytest
from gnosis.self_learning.knowledge import KnowledgeUpdate, apply_knowledge_update
from gnosis.self_learning.lineage import record_version, verify_lineage

def u(i):
    return apply_knowledge_update(KnowledgeUpdate(f"u{i}","flow-1","sha256:e",f"sha256:k{i}","common"))

def test_applied_update_gets_version():
    v=record_version(u(1))
    assert v.parent_version_id=="GENESIS"

def test_lineage_is_ordered():
    a=record_version(u(1)); b=record_version(u(2),parent_version_id=a.version_id)
    assert verify_lineage([a,b])==(True,())

def test_lineage_break_is_detected():
    a=record_version(u(1)); b=record_version(u(2),parent_version_id="sha256:wrong")
    ok,errors=verify_lineage([a,b])
    assert not ok
    assert errors


def test_tampered_version_identity_is_rejected() -> None:
    from dataclasses import replace

    original = record_version(u(1))
    tampered = replace(original, version_id="sha256:tampered")
    ok, errors = verify_lineage([tampered])
    assert not ok
    assert any(x.startswith("VERSION_DIGEST_MISMATCH") for x in errors)
