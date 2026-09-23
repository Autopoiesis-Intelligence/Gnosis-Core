# E7.32 — Partner Action Audit & Evidence Contract

## Objective

Define the append-only evidence record for partner runtime actions and authorization decisions, including allowed, denied, failed and revoked-state attempts, without turning the audit layer into an authority source.

## Audit event model

For action a by partner p:

E = (event_id, partner_identity, request_id, action, resource_scope, capability, contract_revision, package_revision, acceptance_revision, policy_revision, decision, outcome, reason, provenance_refs, timestamp_context)

The exact fields may evolve, but the event MUST retain enough information to reconstruct the authorization decision under the applicable revisions.

## Decision and outcome separation

The audit record MUST distinguish:

Decision = ALLOW / DENY

from:

Outcome = SUCCESS / FAILURE / INTERRUPTED / REVOKED / NOT_EXECUTED

An allowed action that fails is not a successful mutation.

A denied action that is attempted is evidence of an attempted request, not evidence of granted authority.

## Append-only history

Partner action evidence MUST use the project's existing append-only audit boundary.

Events MUST NOT be silently edited or deleted.

Corrections MUST be represented by new events referencing the prior event.

## Authorization evidence

Where a protected action is evaluated, the event SHOULD preserve references to:

- effective capability set;
- contract/package/acceptance revisions;
- policy revision;
- scope decision;
- relevant validation/admission result;
- provenance references;
- denial predicate when denied.

The event stores evidence of the decision; it does not create the permission.

## No authority from audit

AuditEvent(p,a) != Authority(p)

Historical ALLOW does not automatically authorize a future action.

Historical DENY does not by itself define future policy unless current policy explicitly does so.

Audit records MUST NOT be treated as capability tokens.

## Sensitive information

Audit records MUST minimize secrets and unnecessary private payloads.

Credentials, private keys and raw secret material MUST NOT be persisted as ordinary audit evidence.

Where payload evidence is required, content-addressed references or approved redacted representations SHOULD be used.

## Correlation

Events SHOULD support deterministic correlation through:

- request_id;
- contribution_id;
- package_id;
- acceptance_id;
- admission_id;
- governance_decision_id;
- transaction/event chain references.

Correlation identifiers MUST NOT be interpreted as authority.

## Failure and interruption

If a protected operation fails after authorization:

Decision = ALLOW
Outcome = FAILURE

If execution is interrupted before durable commit, the audit record MUST not claim successful mutation.

Recovery MUST reconcile the action evidence with the persistence transaction outcome.

## Revocation evidence

If a request is denied because capability/acceptance/partner state is revoked or expired, the denial MUST identify the applicable state/revision where policy permits.

Revocation MUST NOT erase previous action history.

## Audit integrity

Where the existing audit chain provides hash chaining, partner events SHOULD participate in that same chain rather than creating a parallel trust root.

Any integrity failure MUST produce an auditable finding and MUST NOT be silently repaired.

## Query and export

Audit evidence MAY be exported for partner dispute resolution, compliance or research.

Exports MUST preserve event identity, applicable revisions and integrity references.

An export MUST NOT expose restricted information beyond its authorized scope.

## Acceptance requirements

Implementation MUST eventually test:

1. allowed action evidence;
2. denied action evidence;
3. successful mutation;
4. authorized but failed mutation;
5. interrupted transaction;
6. revoked capability denial;
7. stale contract denial;
8. cross-partner access denial;
9. append-only enforcement;
10. correction through a new event;
11. no secrets in audit storage;
12. audit-chain integrity;
13. restart/recovery correlation;
14. export/import evidence integrity;
15. audit cannot grant authority.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract specifies partner action evidence only. It does not claim that the complete runtime audit integration is currently implemented.
