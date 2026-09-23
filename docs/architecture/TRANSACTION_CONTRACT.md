# Persistence Transaction Contract

**Status:** proposed contract for implementation

**Boundary:** storage/repository layer only. Ψ-Core remains unaware of SQL and transaction mechanics.

## Transaction vocabulary

- **Logical operation:** one domain action such as root creation, rejected candidate recording, accepted transition, or fork.
- **Atomic commit:** after a successful commit all required rows are visible; after rollback none of the operation's rows are visible as a new logical result.
- **Current head:** the authoritative persisted state pointer for one instance.
- **Audit event:** immutable evidence of an operation, linked through a global monotonic sequence and SHA-256 chain.

## Connection contract

Every connection must:

1. enable foreign keys and verify that the pragma is active;
2. use explicit transaction boundaries rather than implicit mixed behavior;
3. configure a documented busy timeout;
4. use a documented journal and synchronous mode;
5. rollback on every exception before returning the error;
6. avoid exposing a connection that can write outside repository policy.

The first implementation should use stdlib `sqlite3` and keep SQL confined to storage modules.

## Atomic operations

### T-01 Fresh database initialization

```text
BEGIN
  create schema/version metadata
COMMIT
```

Schema initialization is idempotent only for the same schema version. An incompatible version fails closed; it is not silently migrated by an unrelated repository method.

### T-02 Root instance creation

```text
BEGIN IMMEDIATE
  insert initial state and relation rows
  insert root instance with current_state_id = initial state
  append root-created audit event
COMMIT
```

No root instance without a valid current state may become visible.

### T-03 Rejected candidate

```text
BEGIN IMMEDIATE
  insert parent/proposed states if policy requires deduplicated storage
  insert candidate
  insert transition accepted=false
  append rejected-transition audit event
COMMIT
```

The instance head is unchanged. Candidate and transition are visible together, or neither is visible as a new operation.

### T-04 Accepted transition

```text
BEGIN IMMEDIATE
  lock/validate instance current_state_id = candidate.parent_state_id
  validate candidate and proposed state through the existing Core contract before persistence
  insert proposed state and relation rows
  insert candidate
  insert transition accepted=true with explicit from/to IDs
  allocate audit sequence and append event with prev_hash/event_hash
  update instance current_state_id
  update execution/budget snapshot if this phase persists budget
COMMIT
```

There must be exactly one head advance for one accepted logical transition.

### T-05 Fork

```text
BEGIN IMMEDIATE
  validate parent instance and source state
  insert child instance with parent and generation + 1
  set child current_state_id to isolated cloned state
  append fork audit event
COMMIT
```

Parent head does not change. Child creation cannot be externally observed without its head.

## Audit append contract

Within the same write transaction:

1. read the current last audit sequence/hash under the write lock;
2. compute `sequence = previous + 1`;
3. canonicalize immutable event fields;
4. compute `event_hash = SHA256(canonical_event)`;
5. insert the event with unique sequence and event ID;
6. reject any mismatch or duplicate before commit.

`UPDATE` and `DELETE` on audit events are not part of the normal repository API. Triggers may reject them as defense in depth. Hash verification remains mandatory because database-level constraints cannot detect every payload mutation.

## Failure semantics

| Failure point | Required result |
|---|---|
| Before begin | No operation rows |
| During state insert | Rollback; prior head unchanged |
| During candidate insert | Rollback; no partial candidate/transition pair |
| During transition insert | Rollback; proposed state is not a committed head |
| During audit hash/insert | Rollback; no accepted head advance |
| During head update | Rollback; no visible transition without matching head |
| During commit | SQLite determines all-or-nothing durability; reopen and verify, never guess |
| After commit | New head and full event chain recoverable |

## Read visibility

Readers may observe only committed rows. A repository read that combines multiple tables must either use one read transaction or perform consistency validation before returning a domain object. It must not return a state head assembled from mixed transaction snapshots.

## Concurrency contract

The first implementation must serialize accepted head updates using a write transaction and compare-and-validate the expected current head. A stale candidate must be rejected without moving the head. Concurrent operations on different instances may be serialized initially; optimization is not an acceptance requirement.

Duplicate logical operations must be handled by deterministic IDs and unique constraints. The result must be either idempotent replay of the same operation or explicit duplicate rejection. It must never create two different audit events for the same idempotency key without documentation.

## Append-only enforcement layers

| Threat | Constraint/trigger | Repository behavior | Verification |
|---|---|---|---|
| `UPDATE audit_events` | Reject trigger or restricted DB role where available | No update method | Direct adversarial test plus chain verification |
| `DELETE audit_events` | Reject trigger | No delete method | Direct adversarial test |
| Change `prev_hash` | Hash chain detects | Verification fails | Tamper test |
| Change `event_hash` | Recompute detects | Verification fails | Tamper test |
| Insert in middle | Sequence/unique constraints and chain detect | Verification fails | Reordering test |
| Change sequence | Unique/order/hash checks detect | Verification fails | Sequence tamper test |
| Delete last event | Head/event continuity detects where referenced | Fail closed or documented proven rollback only | Final deletion test |
| Duplicate event | Unique event/idempotency key | Idempotent or reject | Duplicate test |
| Payload substitution | Event hash detects | Fail closed | Payload tamper test |

## Core boundary

Persistence may serialize, store, load, and verify domain objects. It must not:

- select candidates;
- generate candidates;
- decide whether a transition passes Core invariants;
- mutate `Engine.state` directly;
- become a hidden external selector;
- introduce SQL imports into `gnosis/core`.

The accepted transition decision originates in the existing Core engine. The storage adapter receives a committed domain result and persists it atomically.

## Commit proof obligation

For each successful accepted commit, the repository test must prove all of these after reopening the database:

```text
instance.current_state_id == transition.to_state_id
transition.from_state_id == previous_head
candidate.parent_state_id == transition.from_state_id
candidate.proposed_state.state_id == transition.to_state_id
audit event exists and verifies in the chain
```

For each rejected commit, the same test must prove that the instance head is unchanged.

## E5.04 — Authorization provenance boundary

Authority-sensitive commits must be bound to the exact evolution provenance being authorized.

Required evidence includes, where applicable:
- target/evolution identity;
- principal/owner decision reference;
- policy/invariant version evaluated;
- evidence references;
- evaluator identity/version;
- scope and time validity;
- resulting transition identity;
- rollback/revocation relation.

An append-only/hash-chained audit record is tamper-evidence for the recorded history; it is not proof that the recorded authorization was truthful or valid.

`AuditIntegrity != AuthorizationTruth`.

Authorization evidence must exist before the authority-sensitive commit; a post-commit audit event cannot retroactively create missing authorization.

The current owner-authority issuer remains intentionally unimplemented; the runtime must fail closed rather than manufacture authorization.
## E5.05 — External-audit closure gates

The following gates are prerequisites for accepting authority-sensitive execution as end-to-end verified.

### E5.05-A — Trusted issuer / root of trust
The fail-closed execution boundary is not equivalent to a complete authorization system. A trusted issuance path must bind an explicit authority root, scope, policy version, evidence and exact evolution identity.
`OwnerApproval != ExecutionAuthorization`.

The current `issue_execution_authorization` boundary intentionally fails closed with `NotImplementedError`; this remains an implementation gap until a governed issuer exists.

### E5.05-B — Freshness and replay
Authorization validity must include exact binding, temporal validity, revocation state, replay/consumption state and policy validity.
`Valid(Auth,t,tau) = Binding ∧ Fresh ∧ ¬Revoked ∧ ¬Consumed ∧ PolicyValid`.

Time or generation counters alone are insufficient when a valid authorization can be replayed against another execution. Tests must cover cross-evolution replay, same-authorization reuse, expiry/staleness, revocation and parent-state mismatch.

### E5.05-C — Real CI evidence
Authority-sensitive acceptance requires real CI/pytest evidence tied to the exact commit. Static inspection, historical counts and offline test shims are supplementary evidence only.
`HistoricalPass != CurrentHEADPass`.

### E5.05-D — Implementation/evidence synchronization
Status must distinguish implementation from evidence. A required status record is:
`(ImplementationState, EvidenceState, Scope, Commit)`.

Documentation drift is recorded as a gap; it does not become proof of implementation or verification.

### Gate ordering
E5.05-B may be formalized in parallel, but end-to-end acceptance remains blocked until the trusted issuer (E5.05-A) and real verification evidence (E5.05-C) are closed.
## E5.06 — Trusted issuer boundary

A future trusted issuer must have an explicit, versioned authority scope and may issue authorization only for transitions inside that scope.

`Authorize_I(tau) -> tau in A_I`.

Issuance and execution remain separate events. The issuer does not bypass exact evolution binding or protected invariants.

Credential/key validity must account for active state, expiry, revocation and scope. Rotation must preserve explicit provenance and must not silently expand authority.

Secret credentials/keys must never be persisted in repository source, ordinary audit events, or unprotected project database state. Audit may retain non-secret identifiers and verification metadata.

Revocation invalidates future use according to policy without rewriting historical audit evidence.

The issuer must not self-authorize an expansion of its own authority.

Current owner-authority issuance remains intentionally unimplemented; this contract defines the required boundary and does not claim runtime completion.
## E5.07 — Cryptographic authorization boundary

Future authorization issuance must use canonical payloads and cryptographic verification bound to an explicit issuer key/version.

`Verify(pk_I, Canonical(Auth.payload), Auth.signature) = true` is necessary for signature validity, but `SignatureValid != AuthorityValid`.

Authorization signatures must be domain-separated from unrelated signed objects. The signed payload must bind issuer/version, authority scope/version, exact evolution identity, parent-state identity, policy version, validity bounds, unique authorization identity/nonce, and delegation reference where applicable.

Key rotation is an explicit governance transition. Verification resolves the key version referenced by the authorization; it must not silently substitute the newest key.

Delegation must satisfy `Scope(delegate) ⊆ Scope(delegator)` and preserve explicit expiry, constraints, depth and provenance. Delegation does not become root authority.

Unknown/revoked/expired keys, invalid signatures, unsupported algorithms, malformed payloads, scope/policy mismatch and invalid delegation fail closed.

Ψ-Core must not contain secret signing material and must not become the cryptographic root of trust.

Trusted issuer, key rotation and delegation runtime remain NOT_IMPLEMENTED unless separately verified.
## E5.08 — Canonical authorization identity and replay boundary

Authorization identity must be deterministic over a canonical, domain-separated representation:
`AuthID = H(Domain || Version || CanonicalPayload)`.

All security-relevant fields must be included in the canonical/signature domain. Nonce uniqueness is required within the applicable issuer authority domain, but nonce uniqueness alone cannot replace binding to target, parent state, scope and policy.

Replay analysis must cover same-authorization reuse, cross-evolution reuse, parent-state mismatch, policy-version mismatch and cross-protocol reinterpretation.

Authorization domains and protocol versions require explicit separation and compatibility rules; no implicit cross-protocol or cross-version acceptance.

Hash-derived identity is not equivalent to authorization validity:
`AuthIDMatch != AuthorizationValid`.

Legitimate idempotent retries must be explicitly distinguished from replay of a consumed authorization.

Current runtime does not claim completed canonical serialization, nonce registry or cross-protocol replay enforcement.
## E5.09–E5.19 — External interaction and delegation evolution gates

These contracts extend the existing authorization boundary into multi-domain and external-effect execution.

### E5.09 Root-of-Trust closure
`Issue -> Persist -> Verify -> Consume -> Execute -> Audit -> Recover` must form one evidence-backed path. Partial controls do not constitute end-to-end authorization.

### E5.10 Capability attenuation
`Authority(child) ⊆ Authority(parent)` and `Scope(child) ⊆ Scope(parent)`. Shared storage/process does not imply shared authority; domain and policy context bind capability use.

### E5.11 External API trust boundary
External credentials are authority-bearing. External effects must pass `Intent -> PolicyCheck -> Authorization -> Gateway -> ExternalEffect -> Receipt -> Audit`. External responses are untrusted evidence.

### E5.12 Generation fence / activation
Experimental state cannot acquire stable authority merely through persistence, lineage or restart. Cross-generation external effects require active-generation and authorization binding.

### E5.13 Local approval gateway
Out-of-scope power requires an immutable `ExecutionIntentSnapshot` and explicit governed approval. Stale or materially changed intent fails closed.

### E5.14 Domain risk matrix
Each domain requires explicit autonomy policy `Omega_d` covering actions, power limits, approval rules, rate limits, rollback and evidence requirements. Domain risk labels are policy metadata, not universal truth.

### E5.15 Delegation lineage
Delegation forms an explicit root-to-descendant lineage with non-expanding scope, explicit depth/expiry/audience/action class and policy-defined ancestor revocation behavior.

### E5.16 Multi-domain persistence isolation
Shared persistence must not create cross-domain authority. Cross-domain references require explicit authorization and provenance; incompatible recovery must fail closed.

### E5.17 External side-effect boundary
External non-atomic effects require `PrepareIntent -> Authorize -> Execute -> Receipt -> PersistReceipt -> Reconcile`. Unknown external outcomes must not be blindly retried when the effect is non-idempotent.

### E5.18 Autonomous budget / blast radius
Autonomous power must be bounded by an explicit cumulative budget. Restart, delegation and capability refresh cannot silently reset or increase it.

### E5.19 Approval freshness / exact intent binding
Human approval is valid only for the exact bound intent, parent state, domain policy and validity window. Material changes require re-approval.

These gates do not authorize a Ψ-Core redesign. They define requirements for bridges, delegation, activation and external-effect layers.
## E5.09 — Integrated trust/external-action acceptance

E5.09 integrates E5.05–E5.19 into one acceptance predicate:
`E5.09_ACCEPT = Foundation ∧ Control ∧ Interaction ∧ Isolation ∧ Verification`.

Foundation = trusted issuer, authority scope, cryptographic issuance and canonical authorization identity. Control = capability attenuation, generation fence, domain policy, delegation and cumulative budget. Interaction = external gateway, local approval, side-effect reconciliation and approval freshness. Isolation = multi-domain persistence separation. Verification = exact-commit CI/adversarial evidence.

Required end-to-end sequence:
`IntentCreated -> PolicyEvaluated -> AuthorizationIssued -> AuthorizationPersisted -> AuthorizationVerified -> CapabilityConsumed -> GatewayAdmitted -> ExternalEffect -> ReceiptCaptured -> Reconciled`.

`Persisted != Active`; recovery must not resurrect revoked authority or reset cumulative autonomous budget.

For derived capabilities/actions: `Authority(child) ⊆ Authority(parent)`.

For each domain/time window: `Σ PowerImpact(executions) <= B_domain`.

Approval remains valid only when the execution intent, parent state, policy version and validity window match the approved snapshot.

Unknown external outcome enters `UNKNOWN_EXTERNAL_OUTCOME`; non-idempotent retry requires explicit reconciliation/idempotency policy.

### Acceptance status
E5.09 formal integration contract is CLOSED. Runtime integration remains BLOCKED/UNVERIFIED until a trusted issuer, cryptographic issuance path, delegation/gateway runtime and exact-commit CI evidence exist.

## E5.21 — Test authority boundary bridge

A verified test authorization may be adapted into the existing `ExecutionAuthorization` boundary only inside the test/development authority surface. The adapter must preserve exact `request_provenance` and `evolution_identity` and must continue to pass through `require_execution_authorization`. It must not implement the production owner issuer or grant real external authority.


## E5.22 — Exact intent / issuer binding

The test issuer may derive a development authorization only from the exact provenance object. The resulting test authorization must bind the same provenance/evolution identity used by `ExecutionIntentSnapshot`. Material parent-state or evolution-identity changes fail closed. This adapter is test-only and does not implement production owner authority.


## E5.23 — Recovery non-resurrection

For test/development authorization persistence, recovery must preserve monotonic consumed/revoked state. Closing and reopening the backing store must not resurrect an authorization that was already consumed or revoked. This is a test-level contract only and does not establish production recovery correctness.

## E5.25 — Persistence is not an issuer

`Persist(Store,a)` does not imply authorization. Stored authority remains valid only when issuer verification, exact context binding, and registry integrity all hold. The test registry must not expose an independent issuance path.

## E5.26 — Monotonic authority lifecycle

Test authority lifecycle must not reverse terminal execution states. Expiry cannot extend validity; consumed and revoked authority cannot return to an executable state. Any future re-issuance must create a new authorization identity and independent issuer evidence.

## E5.27 — Distinct terminal authority reasons

Execution authority state must distinguish consumed, revoked, and expired. These reasons have different semantics and must not be collapsed into one generic inactive state. None may return to executable authority; supersession, if introduced, creates a new authorization identity.

## E7.9.9 — Action outcome is not retroactive authorization

Action outcomes are post-action evidence. They cannot retroactively establish that the original decision, authorization, or intent was valid. Retrospective learning must use a new evidence update and versioned re-evaluation.
## E5.29 — Partner Repository Agency / Knowledge Federation

A separately audited partner repository may be attached as an external research/learning source with an isolated partner database.

Required path:

Partner Repository -> Partner DB -> Provenance/Audit -> Quarantine -> Evidence -> Candidate -> Core Verification -> Governed Evolution

The partner database is not a second Core and cannot issue authority.

`PartnerTrust != CoreAuthority`
`PartnerRepositoryAccess != ExecutionAuthority`
`PartnerData -> CanonicalState` has no direct path.

Every source requires immutable revision provenance, schema/version metadata, audit scope, trust dimensions and revocation state. Partner material remains skeptical external evidence until verified for a declared scope.

Initial agency levels are separately governed:
READ_RESEARCH, SUBMIT_EVIDENCE, SUBMIT_CANDIDATE, SUBMIT_TEST, REQUEST_REVIEW, PROPOSE_CHANGE, EXECUTION_AUTHORITY.

The first six are research collaboration capabilities; EXECUTION_AUTHORITY remains under the Root-of-Trust contracts.

Status: DESIGNED / NOT_IMPLEMENTED.

## E5.30 — Agent identity and contract discussion boundary

A participant enters Gnozis through the machine-readable participation template. Submission is not access, identity is not trust, trust is not authority, and discussion is not authorization.

Required conceptual lifecycle:
PARTICIPATION_SUBMISSION -> NORMALIZE -> IDENTITY_CHECK -> PROVENANCE/AUDIT -> QUARANTINE -> CAPABILITY_GRANT -> CONTRACT_DISCUSSION -> CORE_VERIFICATION.

Accepted agents receive stable scoped identity/provenance records. Discussion records preserve agent_id, contract/version, claim, evidence references, challenge/response and resolution status.

Agents may submit evidence, candidates and tests or discuss contracts without receiving execution authority. Consensus among agents is evidence for comparison, never an implicit proof or issuer.

PartnerData -> CanonicalState has no direct path.

Status: DESIGNED / TEMPLATE IMPLEMENTED; runtime identity/discussion infrastructure NOT_IMPLEMENTED.