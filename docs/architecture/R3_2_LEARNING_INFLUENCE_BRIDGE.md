# R3.2 — Learning Influence Bridge

## Objective

Prove that an evidence-gated verification outcome can influence the identity and inputs of the next learning cycle without acquiring execution authority.

## Required causal chain

Cycle N → VerificationFeedback → LearningFeedbackAdmission → FeedbackCycleLink → Cycle N+1.

A rejected result is represented as a `COUNTEREXAMPLE`, not as a positive learning signal.

## Invariants

- only `ADMITTED` feedback may seed a next cycle;
- `FAIL` cannot become `LEARNING_SIGNAL`;
- the next cycle binds to the exact admission and evidence references;
- the link is deterministic and digest-bound;
- the bridge creates no execution authority;
- the test proves influence at the data/provenance boundary, not autonomous Core mutation.

## Remaining proof

This unit test establishes the bridge contract. Runtime integration with durable persistence and a two-cycle sandbox experiment is still required before R3.2 is VERIFIED.
