# E7.15 — Self-Learning Vertical Slice Verification Contract

## Objective

Convert E7.10-E7.14 from distributed design into one reproducible verification scenario using the existing reflection, persistence, provenance, shadow-evaluation and governance components.

## Required vertical slice

1. Start from a known immutable parent state.
2. Register/resolve a scoped agent identity.
3. Ingest one immutable source revision.
4. Record provenance and independence classification.
5. Produce one finding and one counterexample.
6. Derive one RuleProposal/Candidate with complete lineage.
7. Execute shadow evaluation without mutating Core.
8. Persist the complete learning record.
9. Execute Core verification.
10. Apply governance decision.
11. If accepted, commit exactly one transition.
12. Reopen storage and reconstruct the learning lineage.
13. Replay the same input and verify equivalent decision semantics.
14. Change source revision or parent-state context and verify re-evaluation rather than silent reuse.

## Negative path requirements

The slice MUST demonstrate no accepted transition for:

- unknown/revoked agent;
- stale source;
- duplicated/replayed event;
- missing provenance;
- unresolved evidence independence;
- parent-state mismatch;
- failed shadow evaluation;
- failed Core verification;
- rejected governance.

## Evidence requirements

A passing claim MUST reference:

- exact repository commit;
- exact test command;
- test result;
- relevant persisted record identifiers;
- failure-injection result where applicable.

Documentation alone cannot mark the slice VERIFIED.

## Status

DESIGNED / NOT_IMPLEMENTED. Existing reflection/persistence tests provide partial component coverage; current HEAD runtime/CI execution is not claimed here.
