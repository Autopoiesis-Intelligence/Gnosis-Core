# Repository Role and Naming Contract

Status: CURRENT ROLE CONTRACT — documentation only.

## Canonical identities and repositories

- **Gnozis** is the public project/product brand.
- `Autopoiesis-Intelligence/Gnosis-Core` is the canonical repository for executable Core behavior, protected invariants, governed transitions, persistence, and accepted implementation.
- `Autopoiesis-Intelligence/Gnosis-Genesis` is the protected factory/orchestration and commercial workspace. It may prepare candidates and call explicit Core interfaces, but it is not a second canonical state authority.
- `Autopoiesis-Intelligence/Gnosis` is the public product/evidence surface; publication does not grant execution authority.
- `Gnosis-Memory`, `Gnosis-Research`, and `Gnosis-Knowledge` are research/context inputs. Their exact contracts and operational integrations must be established separately.
- `Gnosis-Exchange` and `Gnosis-SDK` must not be assigned authority or production capabilities merely from their names; use their accepted repository contracts to determine exact scope.

This table records intended roles. It does not prove that every repository has a working implementation or an operational integration.

## Permitted responsibility direction

```text
Research / Memory / Knowledge / partner inputs
                 |
                 v
       evidence and proposals
                 |
                 v
 Gnosis-Genesis: candidate preparation/orchestration
                 |
                 | explicit, governed Core request
                 v
 Gnosis-Core: verification and canonical state transition
                 |
                 v
       accepted Core state
                 |
                 v
 public publication of approved, shareable results
```

The diagram expresses intended trust direction, not evidence of a deployed end-to-end pipeline.

## Authority and evidence rules

- Research findings, external model output, connector access, a proposal, a passing test, an approval statement, or an audit receipt do not independently authorize a Core mutation.
- Only the protected Core authorization and governance path may admit canonical state changes.
- Authorization must be bound to the exact operation and evolution provenance and independently verified; plain-string equality is not cryptographic owner authentication.
- Persistence and append-only audit records provide durable/tamper-evident records but do not establish that an authorization was truthful.
- Missing, incomplete, stale, revoked, or inconsistent authority must fail closed.
- Core must not depend on Genesis, research repositories, external AI, connectors, or commercial services as implicit authority sources.
- Public repositories may contain only material intended for public access. Secrets, private partner data, signing keys, and private configuration must remain within their authorized trust boundaries.

## Historical identifiers

Names such as `Gnozis-V2` and old owner/repository paths may appear in historical records, migration evidence, protocol identifiers, or source provenance. Preserve them when needed to identify historical artifacts or compatibility-sensitive interfaces. Do not use them as current canonical repository pointers, and do not perform blind global replacements. Namespace, schema, or protocol renames require a separate compatibility and migration review.

## Acceptance boundary

This document defines intended repository roles and trust boundaries only. It does not prove a production composition root, trusted owner issuer, key provisioning, trusted-time source, revocation provider, or end-to-end runtime. Those capabilities require separate source-level, exact-SHA CI, and runtime evidence.
