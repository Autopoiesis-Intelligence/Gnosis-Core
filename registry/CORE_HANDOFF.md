# Federation → Core Handoff Contract

**Version:** 0.1

This is a non-authoritative handoff record. It does not create Core authority and does not execute a mutation.

```text
Federation Authorization
        ↓
Core Handoff Record
        ↓
existing Core IntegrationRecord / Provenance
        ↓
ExecutionIntentSnapshot
        ↓
ExecutionCommitRequest
        ↓
existing Core authority + persistence
```

The handoff carries external identity and evidence references only. The existing Core `ExecutionAuthorization`, `ExecutionIntentSnapshot`, `ExecutionCommitRequest`, candidate binding, and `SQLiteExecutionCommitAdapter` remain authoritative.

The handoff status `PENDING_CORE_AUTHORITY` is intentionally terminal from the Federation perspective: Federation must never upgrade it to `COMMITTED` on its own.

A future production adapter may consume this record at the application composition root, but it must construct the existing Core authorization/provenance objects and invoke the existing Core boundary rather than introduce a second state, execution identity, or persistence mechanism.
