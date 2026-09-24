from dataclasses import FrozenInstanceError

import pytest

from gnosis.control.capabilities import Capabilities
from gnosis.control.envelope import EvidenceReceipt, OperationEnvelope
from gnosis.control.validators import authorize_operation, sha256_payload, validate_envelope, validate_task_context
from gnosis.domain.identity.types import Identity
from gnosis.domain.scope.types import Scope
from gnosis.domain.task_context.model import ReflectionBudget, TaskContext

NOW = 1_700_000_000_000

def make_identity():
    return Identity("actor-1", "tenant-1", "issuer-1", ("developer",), NOW - 1000, NOW + 1000)

def make_scope():
    return Scope("scope-1", "tenant-1", ("repo:Gnozis-V2",), (), NOW + 1000)

def make_context():
    return TaskContext("task-1", "root-1", "tenant-1", "actor-1", "scope-1",
                       ReflectionBudget(5, 1, 1000, 10, 3), "seed-1", ("policy-hash",), NOW)

def make_envelope(payload={"x": 1}):
    identity = make_identity()
    context = make_context()
    capabilities = Capabilities(("state:test:execute",))
    receipt = EvidenceReceipt("parent", sha256_payload(payload), NOW)
    return OperationEnvelope("env-1", "2.0.0", NOW, identity, context, capabilities,
                             "state.test.execute", payload, "repo:Gnozis-V2", receipt)

def test_payload_hash_is_deterministic():
    assert sha256_payload({"b": 2, "a": 1}) == sha256_payload({"a": 1, "b": 2})

def test_budget_exceeded_rejected():
    c = make_context()
    bad = TaskContext(c.task_id, c.root_task_id, c.tenant_id, c.actor_id, c.scope_id,
                       ReflectionBudget(1, 2, 1000, 10, 3), c.deterministic_seed, c.policy_bindings, c.created_at_ms)
    assert validate_task_context(bad, make_identity(), make_scope()) == "BUDGET_EXCEEDED"

def test_tenant_mismatch_rejected():
    c = make_context()
    bad = TaskContext(c.task_id, c.root_task_id, "tenant-2", c.actor_id, c.scope_id,
                       c.budget, c.deterministic_seed, c.policy_bindings, c.created_at_ms)
    assert validate_task_context(bad, make_identity(), make_scope()) == "TENANT_MISMATCH"

def test_missing_capability_rejected():
    assert authorize_operation(make_envelope(), "state:commit:apply", NOW) == "UNAUTHORIZED_CAPABILITY"

def test_unknown_capability_rejected():
    assert authorize_operation(make_envelope(), "state:unknown", NOW) == "UNKNOWN_CAPABILITY"

def test_immutability_is_enforced():
    e = make_envelope()
    with pytest.raises(FrozenInstanceError):
        e.action = "state.commit.apply"


def test_expired_scope_rejected_by_envelope():
    e = make_envelope()
    expired = Scope("scope-1", "tenant-1", ("repo:Gnozis-V2",), (), NOW)
    assert validate_envelope(e, expired, NOW) == "SCOPE_EXPIRED"

def test_target_resource_out_of_scope_rejected():
    e = make_envelope()
    bad = OperationEnvelope(e.envelope_id, e.schema_version, e.timestamp_ms, e.identity, e.task_context,
                             e.capabilities, e.action, e.payload, "repo:other", e.evidence)
    assert validate_envelope(bad, make_scope(), NOW) == "RESOURCE_OUT_OF_SCOPE"

def test_restricted_resource_rejected():
    scope = Scope("scope-1", "tenant-1", ("repo:Gnozis-V2",), ("repo:Gnozis-V2/private",), NOW + 1000)
    e = make_envelope()
    bad = OperationEnvelope(e.envelope_id, e.schema_version, e.timestamp_ms, e.identity, e.task_context,
                             e.capabilities, e.action, e.payload, "repo:Gnozis-V2/private/file", e.evidence)
    assert validate_envelope(bad, scope, NOW) == "RESOURCE_OUT_OF_SCOPE"
