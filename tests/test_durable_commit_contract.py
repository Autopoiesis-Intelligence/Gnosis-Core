from gnosis.core.durable_commit import durable_commit

class Port:
    def __init__(self): self.called=None
    def persist_evolution(self, provenance, *, event_type, payload):
        self.called=(provenance,event_type,payload)
        return "ok"

def test_core_commit_delegates_to_port():
    p=Port()
    assert durable_commit(p,"prov",event_type="COMMIT",payload={"x":1})=="ok"
    assert p.called==("prov","COMMIT",{"x":1})

def test_core_commit_rejects_empty_event():
    import pytest
    with pytest.raises(ValueError): durable_commit(Port(),"p",event_type="",payload={})
