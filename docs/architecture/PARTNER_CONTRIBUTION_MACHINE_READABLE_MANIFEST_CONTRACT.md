# E7.23 — Partner Contribution Machine-Readable Manifest Contract

## Objective

Define the machine-readable declaration required before a partner repository or partner agent may submit a contribution to the Gnozis learning boundary.

This contract describes declared capability and contribution metadata. It does not grant trust, authority, execution permission or Core mutation rights.

## Formal manifest

For partner identity p:

M_p = (I_p, S_p, D_p, L_p, P_p, Q_p, R_p, V_p, A_p)

where:

- I_p = immutable PartnerIdentity;
- S_p = source identity and revision;
- D_p = declared domains;
- L_p = declared learning targets;
- P_p = provenance requirements;
- Q_p = explicit prohibitions;
- R_p = revision, retention and revocation rules;
- V_p = verification requirements;
- A_p = declared admission state.

The manifest is a declaration, not evidence of the truth of its declarations.

## Non-implication invariants

DeclaredCapability(p) != GrantedCapability(p)

Contribution(p) != Authority(p)

Manifest(p) != Verification(p)

Admission(p) != ExecutionPermission(p)

Identity(p) != Trust(p)

A valid manifest MUST NOT itself create execution authority, Core mutation authority, governance authority or scope expansion.

## Contribution identity

Every contribution c MUST be addressable as:

c = (id, p, type, payload, digest, provenance, scope, status)

The contribution MUST remain linked to the PartnerIdentity and source revision from which it originated.

Anonymous or provenance-incomplete material MUST NOT be promoted as a normal admitted contribution.

## Provenance chain

The minimum conceptual chain is:

Origin -> Source -> PartnerIdentity -> Manifest -> Contribution

Breaking or unverifiable links MUST result in quarantine or rejection according to policy. Missing provenance MUST NOT be reconstructed from assumption.

## Declared versus granted scope

The partner may declare:

S_declared(p)

The effective scope is independently determined:

S_granted(p) subseteq S_declared(p)

No declaration may expand its own granted scope.

Undeclared capability is denied by default.

## Prohibited escalation

Manifest and contribution MUST NOT:

- bypass quarantine;
- disable verification;
- alter Core invariants;
- rewrite audit history;
- activate a RuleProposal or learned rule;
- grant authority to another actor;
- convert learning material into execution permission;
- declare their own material verified;
- silently broaden partner scope.

Therefore:

M_p does not imply AuthorityGain(p)

Contribution_p does not imply CoreMutation.

## Contribution lifecycle

The reference lifecycle is:

DECLARED
-> PARSED
-> VALIDATED
-> QUARANTINED
-> VERIFIED
-> ADMITTED
-> ACTIVE

Failure or revocation may move an active contribution to:

QUARANTINED or REVOKED.

All status changes MUST remain auditable and provenance-preserving.

## Learning boundary

Accepted partner material may become:

- ExternalObservation;
- ResearchEvidence;
- Hypothesis;
- Counterexample;
- Challenge;
- Candidate;
- RuleProposal.

None of these types automatically becomes a CoreRule or CoreState.

The required path remains:

Partner Contribution
-> Provenance
-> Quarantine
-> Verification
-> Candidate / RuleProposal
-> Shadow Evaluation
-> Governance
-> Protected Core transition

## Core / Self-Learning Archive boundary

The canonical engineering repository is Gnozis Core.

The separate temporary Self-Learning Archive is a research/context/evidence surface. It may preserve theory, mathematics, provenance and machine-readable learning material, but it is not a second Core and cannot become an authority root by declaration.

Research/archive material must cross the same evidence and governance boundary before affecting canonical Core behavior.

## Acceptance tests

A future implementation MUST provide reproducible tests for:

1. manifest schema validation;
2. identity binding;
3. source revision binding;
4. digest/integrity mismatch;
5. provenance omission or break;
6. declared-scope versus granted-scope escalation;
7. contribution-to-authority escalation;
8. admission bypass;
9. revoked partner/contribution;
10. historical provenance preservation;
11. replay of the same contribution;
12. restart/recovery without authority resurrection.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract must not be reported as runtime capability until implementation and current evidence exist.
