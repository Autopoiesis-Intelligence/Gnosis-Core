# Federation → Core Integration Contract

**Version:** 0.1

This document defines the integration boundary between the federated registry pipeline and the existing private Core execution/persistence path.

```text
Federation
  ↓
Commit Authorization
  ↓
Canonical ExecutionInput
  ↓
Core Evolution / Persistence
  ↓
Atomic Commit
  ↓
Audit + Provenance
```

## Rules

1. The Federation layer must not create a second state model.
2. The Federation layer must not write directly to Core persistence.
3. `ExecutionInput` is the canonical identity of the execution request.
4. A commit authorization must reference the exact ExecutionInput digest.
5. Core remains responsible for transition validation, transactional persistence, replay protection and audit-chain append.
6. A successful Federation authorization is insufficient if Core rejects the execution input or transition.
7. Core rejection must fail closed and must not be converted into an external success.
8. Federation provenance is retained as evidence references; it does not replace Core provenance.

## Required integration record

```yaml
integration_version: "0.1"
commit_id: <unique>
execution_input_sha256: <sha256>
commit_authorization_sha256: <sha256>
federation_source_refs: []
core_transition_status: PENDING|COMMITTED|REJECTED
core_audit_ref: <required when committed or rejected>
```

## Trust boundary

The Federation proposes and authorizes within its scope. The private Core independently decides whether the supplied canonical execution input is executable and whether the resulting transition can be durably committed.
