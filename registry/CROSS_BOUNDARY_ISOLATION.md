# Cross-Boundary Isolation Contract

**Version:** 0.1

The Federation authorization boundary and the private Core mutation authority are distinct authorities.

Required invariant:

```text
Federation AUTHORIZED
        ↓
PENDING_CORE_AUTHORITY
```

It must never become `COMMITTED` or acquire mutation/commit capability inside the Federation handoff.

Regression tests cover both directions:

1. an authorized Federation request produces only a pending handoff;
2. an unauthorized Federation request cannot produce a handoff.

The Core remains the only component permitted to upgrade a valid handoff into a Core execution request and durable state transition.
