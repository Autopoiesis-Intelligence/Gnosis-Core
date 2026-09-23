# E7.36 — Partner Evidence Query & Reconstruction Protocol

## Objective

Define deterministic, revision-aware reconstruction of partner evidence state from append-only history without turning query results into an independent authority source.

## Query identity

Every reconstruction request MUST identify:

- subject/evidence identity;
- requested historical or current time/context;
- applicable contract/policy revision where required;
- requester identity and scope;
- query purpose where policy requires.

A query MUST NOT silently substitute a different subject or revision.

## Reconstruction model

For evidence e and reconstruction context q:

R(e,q) = F(H_e, q, Policy_q, Contract_q)

where H_e is the relevant append-only history.

The result MUST distinguish:

- historical events;
- derived current state;
- unavailable/redacted payload;
- unresolved/conflicting evidence;
- applicable revisions;
- provenance references.

## Historical reconstruction

A historical query MUST reconstruct the state applicable to the requested context, not simply return today's state.

A later revocation, correction or retention action MUST NOT be retroactively inserted into an earlier historical state unless the governing contract explicitly defines such retroactive effect.

## Current reconstruction

A current query MUST evaluate currently applicable:

- contract revision;
- policy;
- revocation;
- acceptance;
- retention/privacy state;
- provenance validity where required.

Historical validity MUST NOT automatically imply current usability.

## Conflict handling

If authoritative evidence sources conflict:

QueryResult.status = CONFLICTED

unless an explicit governing rule resolves the conflict.

The query layer MUST NOT silently choose a last-writer-wins interpretation.

Protected actions based on an unresolved conflict MUST follow the applicable fail-closed rule.

## Redaction and unavailable data

A query result MUST distinguish:

NOT_FOUND
from
REDACTED
from
UNAVAILABLE
from
CONFLICTED

Absence of a payload MUST NOT be represented as proof that the historical event never existed.

## Query result authority boundary

QueryResult != Permission
QueryResult != GovernanceDecision
QueryResult != Admission
QueryResult != Verification

A result may provide evidence to those processes, but cannot create authority merely by being returned.

## Access control

A requester MUST receive only data within its current scope.

Cross-partner private evidence MUST remain isolated.

Querying another partner's public contract metadata MAY be permitted separately from querying restricted evidence.

## Determinism

For identical history, query context, policy and contract revisions, reconstruction MUST be deterministic.

Equivalent queries MUST NOT depend on arbitrary storage order.

## Pagination and completeness

If history is paginated or truncated, the result MUST explicitly identify incompleteness.

A partial history MUST NOT be represented as a complete reconstruction.

## Audit

Sensitive reconstruction requests SHOULD be auditable where policy requires.

Audit records MUST identify requester, subject, query context and result class without unnecessarily persisting private payload.

## Acceptance requirements

Implementation MUST eventually test:

1. current reconstruction;
2. historical reconstruction;
3. correction history;
4. revocation history;
5. retention/redaction state;
6. missing subject;
7. redacted payload;
8. unavailable evidence;
9. conflicting evidence;
10. incomplete pagination;
11. deterministic repeated query;
12. cross-partner access denial;
13. query cannot grant authority;
14. restart/recovery;
15. audit integrity.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract defines evidence reconstruction semantics only. It does not claim that the query/reconstruction runtime is implemented.
