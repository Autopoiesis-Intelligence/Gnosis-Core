# E7.97 — Post-Closure Monitoring, Reverification & Reopening Trigger Contract

## Objective

Define the governed post-closure monitoring boundary for remediation.

A CLOSED or CONDITIONALLY_CLOSED remediation MUST remain observable where policy requires monitoring. Material drift, new evidence, failed obligations or changed conditions MUST be able to trigger controlled re-verification or reopening without rewriting historical closure records.

## Preconditions

Monitoring MUST reference:

- exact remediation closure/revision;
- remediation plan/revision;
- latest outcome verification;
- residual-risk record(s);
- outstanding obligations;
- monitoring criteria;
- review interval or trigger condition;
- applicable monitoring policy revision.

## Monitoring states

A monitoring record MUST use explicit states:

- SCHEDULED;
- ACTIVE;
- OBSERVING;
- HEALTHY;
- DRIFT_DETECTED;
- REVIEW_REQUIRED;
- REVERIFICATION_REQUIRED;
- REOPENING_REQUIRED;
- SUSPENDED;
- CLOSED;
- SUPERSEDED.

Monitoring status MUST NOT alter the historical closure record.

## Monitoring criteria

Monitoring MUST define, where applicable:

- observed signal/state;
- acceptable range or condition;
- evidence source;
- sampling/review condition;
- responsible authority;
- escalation threshold;
- retention requirement.

Criteria MUST be versioned.

## Drift detection

DRIFT_DETECTED MUST identify:

- exact affected scope;
- observed deviation;
- evidence identity;
- detection time/order evidence;
- applicable threshold;
- materiality assessment;
- required next action.

A drift signal MUST NOT automatically assert that the original remediation failed unless the evidence satisfies the applicable failure criteria.

## Reverification trigger

REVERIFICATION_REQUIRED MUST be triggered when:

- monitored criteria materially deviate;
- residual-risk assumptions change;
- delayed external effects contradict prior verification;
- required evidence becomes invalid;
- a monitoring obligation fails;
- new material evidence affects the verified outcome.

Reverification MUST create a new verification record referencing the prior verification.

## Reopening trigger

REOPENING_REQUIRED MUST be used when policy/evidence establishes that closure criteria may no longer be satisfied.

Automatic reopening, where supported, MUST be deterministic, policy-bound and evidence-linked.

Reopening MUST create a new governed closure/review path while preserving the original closure.

## False-positive handling

A drift signal that does not satisfy reopening criteria MUST be recorded as reviewed/reconciled rather than silently discarded.

The system MUST preserve the evidence and rationale for not reopening.

## Residual-risk monitoring

Residual-risk monitoring MUST track:

- risk state;
- mitigation state;
- review date/condition;
- owner;
- evidence;
- escalation status.

Expired or violated risk controls MUST enter REVIEW_REQUIRED or REOPENING_REQUIRED according to policy.

## Privacy and security

Monitoring MUST use minimum necessary data.

Continuous monitoring MUST NOT become an unrestricted data collection channel.

Sensitive evidence MUST remain access-controlled and referenced where possible.

## Recovery and replay

Monitoring state and trigger evidence MUST survive restart/recovery.

Identical observations MAY be idempotent when observation identity, evidence identity, criteria revision and monitoring record are identical.

Conflicting replay MUST fail closed.

Recovery MUST NOT fabricate HEALTHY or CLOSED status.

## Authority separation

Monitoring != verification
Monitoring != reopening decision
Drift detection != finding confirmation
Reverification != history mutation
Automatic trigger != execution authorization
Monitoring != Ψ-Core mutation

## Acceptance gate

E7.97 is satisfied only when implementation and tests demonstrate:

1. exact closure-to-monitoring provenance;
2. versioned monitoring criteria;
3. deterministic drift detection;
4. evidence-linked reverification triggers;
5. controlled reopening trigger;
6. false-positive preservation;
7. residual-risk monitoring;
8. privacy/security controls;
9. replay/recovery integrity;
10. no historical closure mutation;
11. exact-commit runtime/CI evidence.

Documentation alone is not implementation proof.

## Dependencies

- E7.96 — Remediation Closure & Residual Risk Governance
- E7.95 — Remediation Execution Result Reconciliation & Outcome Verification
- E7.89 — Corrective Finding Governance Review & Remediation Trigger

## Status

DESIGNED / NOT_IMPLEMENTED

Contract revision: E7.97-r1
