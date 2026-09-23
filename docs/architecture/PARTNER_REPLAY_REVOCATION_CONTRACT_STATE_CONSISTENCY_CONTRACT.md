# E7.27 — Partner Replay, Revocation & Contract-State Consistency Contract

## Objective

Define deterministic handling of replay, revocation and contract-version changes for partner contributions so that historical admission cannot be resurrected, bypassed or silently reinterpreted.

## Replay identity

A replay request MUST be evaluated against the immutable contribution identity and its bound provenance:

R(c) = (contribution_id, content_digest, source_revision, manifest_revision, contract_revision)

An identical replay MAY resolve idempotently to the existing result.

Any conflicting component MUST fail closed.

## Replay invariant

For an existing contribution c:

Replay(c) = c

must not create a second authoritative contribution history.

A conflicting replay MUST NOT:

- overwrite payload;
- replace provenance;
- change source revision;
- change manifest revision;
- change admission decision;
- replace audit actor/context;
- erase prior validation failures.

## Revocation

Revocation is a state/event transition, not history deletion.

Possible subjects include:

- PartnerIdentity;
- source;
- source revision;
- manifest revision;
- contribution;
- admission scope;
- contract revision.

Revocation MUST identify its exact target and effective scope.

## Revocation semantics

Historical facts remain attributable:

HistoricalAdmission(c) remains true as a historical event.

CurrentUsability(c) may become false.

Therefore:

HistoricalAdmission != CurrentValidity

Revocation MUST NOT retroactively rewrite historical events.

## Contract revision

If contract revision changes:

ContractRevision_n -> ContractRevision_n+1

existing records retain the revision under which they were validated/admitted.

A newer contract MUST NOT silently rewrite old validation evidence.

Policy may require revalidation under the newer revision; if so, this is a new validation event.

## Resurrection prevention

A revoked or invalidated contribution MUST NOT become active solely because an old valid manifest, old contract revision or historical admission is replayed.

Formally:

Revoked(c) ∧ Replay(old_valid_context) -> not Active(c)

unless a new explicit revalidation/admission process is completed.

## State consistency

The effective partner state MUST be derived from the ordered authoritative event history and applicable current policy.

Conflicting state sources MUST NOT be merged by preference or last-writer-wins without an explicit deterministic rule.

## Duplicate identity

The system MUST distinguish:

- exact duplicate;
- semantic revision;
- conflicting duplicate;
- replay after revocation.

These cases MUST NOT collapse into one generic idempotency path.

## Audit requirements

Every replay/revocation/revalidation event MUST preserve:

- subject identity;
- prior state;
- requested state/action;
- applicable contract revision;
- provenance;
- decision;
- reason/failure predicate;
- event identity.

Audit history MUST remain append-only.

## Acceptance requirements

Implementation MUST eventually test:

1. exact replay;
2. payload-conflicting replay;
3. provenance-conflicting replay;
4. source-revision conflict;
5. manifest-revision conflict;
6. contract-revision conflict;
7. replay after revocation;
8. partner-level revocation;
9. contribution-level revocation;
10. revalidation under a newer contract;
11. restart/recovery consistency;
12. duplicate-vs-revision distinction;
13. historical admission preservation;
14. no authority resurrection.

## Status

DESIGNED / NOT_IMPLEMENTED.

No runtime revocation/replay capability is claimed until implementation and reproducible verification exist.
