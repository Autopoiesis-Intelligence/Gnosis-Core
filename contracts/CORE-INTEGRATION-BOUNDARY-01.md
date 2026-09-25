# CORE-INTEGRATION-BOUNDARY-01

## Purpose
Establish a reproducible boundary proving that external task/context/connector layers can submit bounded proposals to Core without becoming a second Core state model or gaining direct mutation authority.

## Contract
1. External observations MUST enter through an explicit normalized proposal boundary.
2. Only a bounded Candidate/proposal may enter Core evaluation.
3. External agents/connectors MUST NOT directly mutate canonical Core state.
4. Context restoration MUST NOT confer execution authorization.
5. Persistent context MUST remain distinct from canonical Core state.
6. Agent agreement MUST NOT be treated as proof.
7. Any required Core semantic change MUST become an explicit architecture change with invariant, compatibility, migration, tests, and audit evidence.

## Required evidence
1. Direct external mutation attempt is rejected.
2. Context restoration without authorization is rejected.
3. Normalized proposal is attributable to its source/input identity.
4. Candidate enters the existing Test → Verify → Commit path.
5. Persistence/reload does not create a second Core state model.
6. Negative/bypass tests pass reproducibly in CI.
7. Independent audit can distinguish evidence from authorization.

## Closure rule
CLOSED only after reproducible runtime tests and CI evidence demonstrate the boundary. Documentation alone is insufficient.

## Current status
SPECIFIED / EXECUTION PENDING
