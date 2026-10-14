import pytest

from gnosis.core import Candidate, State
from gnosis.instances.instance import Instance
from gnosis.storage import connect, save_instance
from gnosis.storage.repositories import _persist_transition
from gnosis.evolution.provenance import build_provenance, canonical_digest


@pytest.fixture
def sqlite_conn():
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def provenance():
    observations = {"result": "ok"}
    evidence = canonical_digest(observations)
    return build_provenance(
        candidate_id="c1",
        parent_state_id="s1",
        parent_state_digest="pd",
        proposed_state_digest=canonical_digest({"state": "new"}),
        observations=observations,
        evidence_digest=evidence,
        proposed_state_content_id="content-1",
        candidate_binding_digest="binding-1",
        evaluation_status="PASS",
        shadow_status="UNCHANGED",
        invariant_status="PRESERVED",
        governance_decision="ALLOW",
    )


@pytest.fixture
def persisted_transition():
    conn = connect()
    instance = Instance.create_root("user-1", State(elements={"a": 1}))
    save_instance(conn, instance)
    proposed = instance.engine.state.with_elements({"b": 2})
    candidate = Candidate(instance.engine.state.state_id, proposed, "test")
    record = instance.engine.step(candidate)
    _persist_transition(conn, instance, candidate, record, actor="test")
    return conn, instance, record


# Explicitly test-only signed commit fixture. The ephemeral signing key and static
# trust resolvers below are not production trust roots.
from dataclasses import dataclass
import base64
from nacl.signing import SigningKey

from gnosis.reflection.authority import ExecutionAuthorization, ExecutionCommitRequest, ExecutionIntentSnapshot
from gnosis.reflection.authorization_validity import AuthorizationValidity
from gnosis.reflection.execution_adapter import SQLiteExecutionCommitAdapter
from gnosis.reflection.owner_authorization import ProductionAuthorization, TrustedIssuerKey
from gnosis.reflection.production_trust_context import ProductionTrustContext


@dataclass(frozen=True)
class _FailureInjectedCommitRequest(ExecutionCommitRequest):
    failure_injection: str | None = None


class _FixtureKeyResolver:
    def __init__(self, key):
        self._key = key

    def resolve(self, issuer_id, key_version):
        if (issuer_id, key_version) == (self._key.issuer_id, self._key.key_version):
            return self._key
        return None


@dataclass
class _RealCommitFixture:
    conn: object
    instance: object
    candidate: object
    record: object
    request: object
    adapter: object
    nonce: str

    def __iter__(self):
        yield self.conn
        yield self.instance
        yield self.candidate
        yield self.record
        yield self.request


@pytest.fixture
def real_commit_fixture(pytest_request):
    """Construct one valid, ephemeral signed commit request for rollback tests."""
    from gnosis.core import Candidate, State
    from gnosis.evolution.provenance import build_provenance, canonical_digest
    from gnosis.instances.instance import Instance
    from gnosis.reflection.owner_authorization import ProductionAuthorization, TrustedIssuerKey
    from gnosis.storage import connect, save_instance

    conn = connect()
    try:
        instance = Instance.create_root("test-owner", State(elements={"root": 1}))
        save_instance(conn, instance)
        parent = instance.engine.state
        proposed = parent.with_elements({"committed": True})
        candidate = Candidate(parent.state_id, proposed, "test:signed-commit")
        record = instance.engine.step(candidate)

        observations = {"result": "rollback-fixture"}
        provenance = build_provenance(
            candidate_id=candidate.candidate_id,
            parent_state_id=parent.state_id,
            parent_state_digest=parent.state_id,
            proposed_state_digest=proposed.state_id,
            observations=observations,
            evidence_digest=canonical_digest(observations),
            proposed_state_content_id=proposed.content_id,
            candidate_binding_digest=candidate.binding_digest(parent.state_id),
            evaluation_status="PASS", shadow_status="UNCHANGED",
            invariant_status="PRESERVED", governance_decision="ALLOW",
        )

        signing_key = SigningKey.generate()
        unsigned = ProductionAuthorization(
            authorization_id="", issuer_id="test-owner-issuer", key_version="test-v1",
            authority_scope=("evolution.commit",), policy_version="test-policy-v1",
            evolution_identity=provenance.evolution_identity,
            parent_state_digest=provenance.parent_state_digest,
            request_provenance=provenance.provenance_id,
            valid_from=10, expires_at=200, nonce="test-rollback-nonce", signature="",
        )
        authorization_id = unsigned.expected_authorization_id()
        to_sign = ProductionAuthorization(
            authorization_id=authorization_id, issuer_id=unsigned.issuer_id,
            key_version=unsigned.key_version, authority_scope=unsigned.authority_scope,
            policy_version=unsigned.policy_version, evolution_identity=unsigned.evolution_identity,
            parent_state_digest=unsigned.parent_state_digest,
            request_provenance=unsigned.request_provenance,
            valid_from=unsigned.valid_from, expires_at=unsigned.expires_at,
            nonce=unsigned.nonce, signature="",
        )
        signature = base64.b64encode(signing_key.sign(to_sign.canonical_bytes()).signature).decode("ascii")
        signed = ProductionAuthorization(
            **{**to_sign.__dict__, "signature": signature}
        )
        trusted_key = TrustedIssuerKey("test-owner-issuer", "test-v1", bytes(signing_key.verify_key))
        validity_digest = "test-validity-evidence-digest"
        trust = ProductionTrustContext(
            issuer_key_resolver=_FixtureKeyResolver(trusted_key),
            authority_scope=frozenset({"evolution.commit"}),
            policy_version="test-policy-v1",
            trusted_clock=lambda: 100,
            validity_evidence_digest_resolver=lambda requested_id: validity_digest if requested_id == authorization_id else None,
        )
        validity = AuthorizationValidity(authorization_id, "test-policy-v1", validity_digest)
        legacy_auth = ExecutionAuthorization(
            request_provenance=provenance.provenance_id,
            owner_approved=True,
            evolution_identity=provenance.evolution_identity,
            approval_id=authorization_id,
        )
        request = _FailureInjectedCommitRequest(
            authorization=legacy_auth,
            intent_snapshot=ExecutionIntentSnapshot.from_provenance(provenance),
            request_provenance=provenance.provenance_id,
            evolution_identity=provenance.evolution_identity,
            provenance=provenance,
            authorization_validity=validity,
        )
        # The signed authorization/trust context are explicit test dependencies;
        # attach them to the fixture container rather than the commit request.
        fixture = _RealCommitFixture(
            conn, instance, candidate, record, request, SQLiteExecutionCommitAdapter(), signed.nonce
        )
        fixture.production_authorization = signed
        fixture.trust_context = trust
        pytest_request.addfinalizer(conn.close)
        return fixture
    except Exception:
        conn.close()
        raise
