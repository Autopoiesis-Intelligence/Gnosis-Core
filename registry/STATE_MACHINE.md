# Registry State Machine

**Version:** 0.1

The registry lifecycle is enforced as a closed transition graph.

```text
discovered → registered → authorized → verified → active
     │             │            │           │         │
     └─────────────┴────────────┴───────────┴─────────→ quarantined → verified
                                                  \→ revoked
```

## Allowed transitions

- discovered → registered | quarantined
- registered → authorized | quarantined
- authorized → verified | quarantined | revoked
- verified → active | quarantined | revoked
- active → quarantined | revoked
- quarantined → verified | revoked
- revoked → terminal

Every transition requires a source identity, immutable policy revision reference, actor identity and reason.

The state machine validates lifecycle legality only. It does not itself grant authorization, establish scientific truth, or connect a source to the private Kernel.
