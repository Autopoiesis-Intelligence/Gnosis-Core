# E7.31 — Partner Capability Enforcement & Runtime Scope Boundary Contract

## Objective

Define the runtime enforcement boundary that constrains a partner to the exact capabilities and scope resulting from explicit acceptance, current policy and current validity.

## Effective capability set

For partner p:

C_eff(p,t) =
C_declared(p)
∩ C_policy(p,t)
∩ C_accepted(p,t)
∩ C_currently_valid(p,t)

No runtime action may be authorized from declared or accepted capability alone if current policy or validity denies it.

## Scope tuple

Every runtime request SHOULD resolve to:

S = (partner_identity, capability, resource_scope, action, contract_revision, package_revision, acceptance_revision)

Authorization MUST evaluate the complete tuple.

## Default deny

If any mandatory component is missing, ambiguous, stale or conflicting:

Authorize(S) = false

The runtime MUST fail closed.

## Capability enforcement

A capability MUST map to an explicit set of permitted actions and resource boundaries.

Capability labels MUST NOT be treated as unrestricted permissions.

For example:

LearningRead != CoreWrite

ContributionSubmit != ContributionAdmit

ContractRead != ContractEdit

EvidenceSubmit != EvidenceVerify

Admission != Governance

## Runtime isolation

Partner requests MUST cross an explicit boundary before reaching protected resources.

The enforcement layer MUST prevent:

- direct Core state mutation;
- direct database authority escalation;
- audit history modification;
- policy mutation;
- contract registry authority mutation;
- bypass of validation/quarantine;
- bypass of admission;
- access outside granted resource scope.

## Scope narrowing

A runtime component MAY narrow an already granted scope.

It MUST NOT widen it.

Formally:

S_runtime ⊆ S_granted

A request for broader scope MUST enter a separate governed capability-change process.

## Revocation and expiry

Before protected actions, current validity MUST be checked where policy requires.

If capability, acceptance, partner identity, package or contract becomes revoked/expired:

new protected actions MUST fail closed.

Historical events remain preserved.

## Confused-deputy protection

The enforcement layer MUST NOT accept a partner-controlled identifier as sufficient proof of another actor's authority.

Delegation MUST be explicit, scoped and independently validated.

Partner A MUST NOT use a capability to cause the runtime to perform an action reserved for Partner B or Core governance.

## Cross-partner isolation

One partner's capability MUST NOT implicitly grant access to another partner's:

- private contributions;
- contract acceptance;
- credentials/secrets;
- provenance records where restricted;
- mutable workspace;
- governance state.

Shared/public evidence MAY be separately scoped as policy permits.

## Runtime decision record

A protected action decision SHOULD preserve:

- partner identity;
- requested capability;
- requested resource/action;
- effective capability set;
- applicable contract/package/acceptance revisions;
- policy revision;
- decision;
- denial predicate where denied;
- event identity.

The decision MUST be auditable under the existing audit boundary.

## Atomic enforcement

Where a protected action mutates persistent state, authorization and the protected mutation MUST share the appropriate transactional boundary.

A successful authorization MUST NOT be treated as durable permission if the corresponding protected operation fails.

## Acceptance requirements

Implementation MUST eventually test:

1. allowed action;
2. undeclared capability;
3. unaccepted capability;
4. revoked capability;
5. expired acceptance;
6. stale contract/package;
7. resource scope escalation;
8. direct Core mutation attempt;
9. direct audit mutation attempt;
10. validation/admission bypass;
11. cross-partner access;
12. confused-deputy/delegation abuse;
13. restart/recovery;
14. authorization/mutation atomicity;
15. deterministic denial reasons.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract defines the enforcement boundary only. It does not claim that partner capability enforcement is currently implemented.
