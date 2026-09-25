# Core Integration Audit — Federation Boundary

**Version:** 0.1  
**Scope:** federation registry branch → existing private Core execution/persistence path

## Finding

The existing Core already has a canonical execution authorization boundary. The integration must use it rather than introduce a second `ExecutionInput` abstraction.

### Existing canonical path

```text
Governance
  ↓
ExecutionAuthorization
  ↓
ExecutionIntentSnapshot
  ↓
ExecutionCommitRequest
  ↓
require_execution_commit()
  ↓
require_execution_candidate_binding()
  ↓
SQLiteExecutionCommitAdapter.commit()
  ↓
_persist_transition()
  ↓
load_state()
  ↓
ExecutionReceipt
```

The existing authority boundary recomputes the canonical evolution identity from candidate, execution, parent-state, proposed-state, evidence, evaluation, shadow, invariant, governance and provenance identities. It also checks the candidate binding and resulting persisted state before producing the execution receipt.

## Integration decision

The Federation `Commit Gate` MUST NOT become a second commit authority. Its output must be translated into the existing `ExecutionCommitRequest` boundary, subject to the existing owner-authority semantics.

The previous draft reference to a standalone `execution_input_sha256` is therefore **not canonical** and must not be wired into Core as a competing identity. Federation provenance can be retained as evidence/reference metadata, while Core `ExecutionIntentSnapshot` and canonical evolution identity remain authoritative for execution.

## Required adapter

```text
Federation authorization
        ↓
Federation integration record
        ↓
existing Core provenance
        ↓
ExecutionIntentSnapshot
        ↓
ExecutionCommitRequest
        ↓
existing SQLiteExecutionCommitAdapter
```

The adapter must be fail-closed if federation identity, candidate identity, parent state, proposed state, provenance, or policy binding disagrees with the Core request.

## Current status

- Core execution authorization: **IMPLEMENTED in main**
- Intent snapshot binding: **IMPLEMENTED in main**
- Candidate/transition binding: **IMPLEMENTED in main**
- Atomic persistence adapter: **IMPLEMENTED in main**
- Post-commit execution receipt: **IMPLEMENTED in main**
- Federation → Core adapter: **MISSING**
- Runtime/CI evidence for this new federation integration: **UNVERIFIED**

## Safety conclusion

Do not duplicate the Core state model, persistence transaction, execution identity, or audit chain. The federation layer remains an upstream proposal/evidence surface; the existing private Core remains the final execution authority.
