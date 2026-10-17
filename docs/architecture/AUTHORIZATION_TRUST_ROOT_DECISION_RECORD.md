# Authorization Trust-Root Decision Record

**Status:** BLOCKED — decisions required; no production authorization implementation is approved by this record.
**Scope:** owner-authority verification for trusted execution.
**Observed base:** `3169a271bf31522273833c8aaf7f13417bd9faba`
**Related design proposal:** PR #241, `PRODUCTION_AUTHORIZATION_VERIFIER_CONTRACT.md`
**Related diagnostic evidence:** PR #240. Keep both PRs Draft/unmerged until remediation is implemented and proven.

## 1. Problem statement

The current trusted execution path does not independently verify cryptographic proof that an authorization was issued by a trusted owner authority. Caller-controlled fields and `owner_approved` are not proof of issuer authority. Authorization consumption and audit-chain validation establish consumption/audit properties, not authenticity of the authority.

## 2. Observed implementation facts

- `gnosis/reflection/trusted_issuer.py` compares caller-supplied strings and fields and then creates an `ExecutionAuthorization(owner_approved=True)`; it does not verify a signature or resolve a trusted key.
- `gnosis/reflection/authorization_validity.py` represents validity with caller-provided fields and a boolean revocation flag; no independently sourced revocation check is present in this component.
- `gnosis/reflection/trusted_execution_gate.py` has no issuer-proof verification step before consumption.
- `gnosis/reflection/test_issuer.py` is explicitly test/development-only and uses HMAC-SHA256. It is not a production trust root.
- `pyproject.toml` declares no core runtime dependencies. No production cryptographic provider was established by the inspected package configuration.
- `docs/DATABASE_SCHEMA.md` labels itself draft/not implemented and describes an `identities` table that is absent from the current `gnosis/storage/database.py` schema. It must not be cited as an implemented trust-root registry.
- The execution adapter wraps gate and persistence in one storage transaction. Remediation must preserve atomicity and reject before consumption/audit mutation.

## 3. Decisions that remain unresolved

No value below is selected by this document.

| Decision | Required authority/evidence | Status |
|---|---|---|
| Who owns the owner-authority signing key and how is that ownership established? | Explicit owner-approved project/security contract | BLOCKED |
| Where does the trusted verifier obtain its trust-root/key registry? | Implemented configuration source and access boundary, independent of the presented authorization | BLOCKED |
| Which signature algorithm and maintained provider are approved? | Dependency/security decision plus supported Python/runtime constraints | BLOCKED |
| How are issuer IDs, key versions, rotation, disablement and revocation governed? | Defined lifecycle and authoritative revocation source | BLOCKED |
| What source supplies trusted time for not-before/expiry checks? | Explicit clock/time trust contract | BLOCKED |
| How are scope, audience, policy version, request provenance, evolution identity, parent-state digest and execution intent canonically bound? | Versioned artifact contract and deterministic serialization | DESIGN PROPOSAL |
| How are verification, one-time consumption and state commit made atomic under concurrency? | Transaction contract plus adversarial tests | DESIGN PROPOSAL |
| Which test keys/fixtures are permitted? | Isolated test-only fixtures with no production fallback | BLOCKED |

## 4. Safety constraints while blocked

1. Do not generate or embed a default owner key.
2. Do not treat caller-supplied `authority_root`, a string identity, an `owner_approved` boolean, or an unsigned dataclass as proof of authority.
3. Do not promote the test HMAC issuer to production.
4. Do not silently add a new crypto dependency or claim key custody/revocation/time is solved.
5. Do not change production runtime, database schema, migrations or commit semantics until the unresolved authority decisions are grounded in an approved project contract.
6. Once decisions are supplied, implement in a separate branch, fail closed on unknown/untrusted keys and malformed/expired/revoked artifacts, and prove that rejected artifacts do not write a consumption event.

## 5. Acceptance criteria for a future implementation

- Valid signature from a configured trusted issuer is required.
- Unknown issuer/key version, invalid signature, unsupported algorithm, wrong scope/audience, wrong policy/evolution/parent/intent binding, expired/not-yet-valid authorization and revoked key/authorization are rejected.
- Caller-created authorization objects cannot bypass verification.
- Rejection occurs before consumption/audit mutation.
- Consumption and commit remain one atomic transaction; duplicate/replayed authorization fails under concurrency.
- Tests prove both successful verification and each adversarial rejection path.
- Evidence reports exact commit SHA, CI run IDs/results, and any runtime/persistence audit separately.

## 6. Evidence status

- DESIGN: this record documents unresolved decisions and constraints.
- IMPLEMENTED: production issuer-proof verification is not established.
- REACHABLE: no verified production verifier path established.
- RUNTIME: not proven by this record.
- PERSISTED: not proven by this record.
- AUDITED: diagnostic evidence exists in PR #240; remediation is not audited.
- CI_PROVEN: not established for a remediation because no remediation implementation exists.

This record is not an execution authorization, key registry, or approval to deploy.
