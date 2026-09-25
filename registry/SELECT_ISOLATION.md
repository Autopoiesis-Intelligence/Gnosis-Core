# Select Isolation Contract

**Version:** 0.1

Select is a Core decision stage. External source identity has no selector authority.

```text
Test Results
    ↓
 admissibility
    ↓
 deterministic ordering
    ↓
 Selected Candidate
```

The reference implementation accepts evidence-backed results allowed by an immutable selection policy and uses a stable `PASS_THEN_CANDIDATE_ID` ordering. Source identity is deliberately excluded from the ordering key.

Selection creates a signed-by-digest decision record but does not evolve or commit state. A selected candidate must still pass the existing Evolve, Verify and Commit gates.

The selection contract is intentionally replaceable by a stronger mathematically specified selector later; the trust boundary remains the same: external sources cannot select themselves.
