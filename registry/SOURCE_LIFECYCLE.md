# Memory Source Lifecycle Contract

**Protocol:** 0.1

Registration is an explicit trust-boundary transition. A repository cannot authorize itself and a successful validator run does not grant Kernel access.

## States

```text
discovered → registered → authorized → verified → active
                    │           │          │
                    └───────────┴──────────┴→ quarantined → revoked
```

### discovered
The source is known but has no registry trust status.

### registered
The source has a registry identity and accepted manifest, but is not authorized for Kernel consumption.

### authorized
A registry policy has explicitly allowed the source for a declared scope. Authorization is separate from content truth.

### verified
The authorized source has passed the required validation/evidence gates for its declared scope.

### active
The source may be consumed through the permissions granted by its registry record.

### quarantined
Consumption is blocked while the source or its evidence is investigated. Existing provenance remains retained.

### revoked
Authorization is withdrawn. Revocation does not erase historical provenance or evidence.

## Non-transitions

- `PASS` from the local validator does not imply `authorized`.
- `registered` does not imply `verified`.
- `verified` does not imply scientific truth.
- `active` does not imply unrestricted use.
- `revoked` does not delete historical evidence.

## Scope

Every authorization must identify an explicit source scope. The registry must not issue an implicit global permission to influence the private Kernel.
