# Commit Gate Contract

**Version:** 0.1

The Commit Gate is the final authorization boundary before a Core state transition. It authorizes a commit but does not itself mutate the state store.

Required inputs:

- `VERIFIED` verification result;
- matching immutable policy identity/revision;
- canonical `ExecutionInput` SHA-256;
- previous state;
- proposed state;
- unique commit identity.

The gate rejects verification failures, policy mismatches, invalid execution identity, no-op transitions, stale or substituted previous/proposed state and missing commit identity.

```text
VERIFIED
   ↓
Commit Gate
   ↓
AUTHORIZED
   ↓
Core Commit Transaction
   ↓
New State + Audit
```

Authorization is not mutation. The actual state store must perform the transaction atomically and record the resulting provenance/audit links. Replay protection belongs to the durable commit transaction and its unique commit identity.
