# Influence Gate Contract

**Version:** 0.1

The Influence Gate is the boundary between external observations and the Core evolution pipeline.

```text
External Observation
        ↓
 Influence Gate
        ↓
Candidate Pending Test
        ↓
      Test
        ↓
     Select
        ↓
     Evolve
        ↓
    Verify
        ↓
    Commit
```

The gate does not allow an external source to select, mutate or commit Core state. It validates the observation envelope, checks admissibility policy, and creates a bounded candidate reference containing the observation digest and the policy revision used for admission.

Admission is not acceptance. `ADMITTED_AS_CANDIDATE` means only that the observation may enter the existing candidate/test pipeline.

Any domain or resource-type mismatch, digest mismatch, unsupported version or externally supplied influence capability causes rejection.
