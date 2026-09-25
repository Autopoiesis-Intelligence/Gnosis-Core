# Gnozis Capability Authorization

**Status:** ARCHITECTURAL BASELINE v0.1

## Principle

Gnozis grants bounded capabilities rather than broad system access.

```
Subject
  -> Capability
  -> Scope
  -> Policy
  -> Permission
```

## Capability examples

- READ_PUBLIC_KNOWLEDGE
- CONTRIBUTE_RESEARCH
- SUBMIT_PROPOSAL
- EXECUTE_CONTRACT
- ACCESS_PROJECT_ARTIFACT
- MAINTAIN_REPOSITORY
- REVIEW_DELIVERABLE

These are conceptual capabilities. Concrete implementation may introduce narrower permissions.

## Rules

1. Role does not equal capability.
2. Capability does not equal Kernel authority.
3. Contract scope limits contract-related capabilities.
4. Public repository access does not imply private resource access.
5. Revoked or expired authorization must fail closed.
6. Authorization decisions must be auditable.

## Protected resources

Private Kernel state, proprietary algorithms, confidential commercial information and protected memory are separate resources and require explicit authorization.

## External contributors

A contributor can produce an artifact, evidence or proposal without receiving access to internal Kernel state.

## Revocation

Capability grants must support explicit revocation and expiration where appropriate.

Historical actions remain auditable after revocation.
