from gnosis.evolution.diagnostic_adapter import sandbox_to_diagnostic_evidence
from gnosis.evolution.diagnostic_corpus import CoreDiagnosticCase, CoreDiagnosticCorpus
from gnosis.evolution.sandbox import SandboxBudget
from gnosis.core.types import State, Candidate

def test_completed_sandbox_becomes_observed_diagnostic_evidence():
    s=State(elements={"x":1})
    c=Candidate(s.state_id,s.with_elements({"x":2}),"d")
    result=CoreDiagnosticCorpus((CoreDiagnosticCase("c","x",lambda *_: {"metric":1},SandboxBudget()),)).run("c",s,c)
    e=sandbox_to_diagnostic_evidence(result,case_id="c",evidence_id="e")
    assert e.lifecycle=="OBSERVED"
    assert any(x.startswith("sandbox-evidence:") for x in e.provenance_refs)

def test_failed_sandbox_remains_ephemeral():
    s=State(elements={"x":1})
    c=Candidate(s.state_id,s.with_elements({"x":2}),"d")
    result=CoreDiagnosticCorpus((CoreDiagnosticCase("c","x",lambda *_: (_ for _ in ()).throw(RuntimeError("x")),SandboxBudget()),)).run("c",s,c)
    e=sandbox_to_diagnostic_evidence(result,case_id="c",evidence_id="e")
    assert e.lifecycle=="EPHEMERAL"
