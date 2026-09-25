# Independent Verify Gate Contract

**Version:** 0.1

Verify is independent from Evolution and is fail-closed. A proposal cannot become commit-ready merely because Evolution returned `PROPOSED`.

The verifier receives the proposal, previous state, proposed state, evidence references, provenance references and an immutable verification-policy revision.

Verification checks structural requirements, policy identity, required evidence/provenance, state-change presence and reproducibility references. It emits a digest-bound verification record with `VERIFIED` or `REJECTED`.

```text
Evolution Result
      +
Previous State
      +
Proposed State
      +
Evidence
      +
Provenance
      ↓
Independent Verify
      ↓
VERIFIED / REJECTED
      ↓
Commit Gate
```

`VERIFIED` is not itself a commit. The Commit Gate remains the final state-changing authority.

The reference implementation's input-reference check is intentionally conservative and must be replaced by the canonical Core execution-input digest contract before production integration.
