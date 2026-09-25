# Evolution Boundary Contract

**Version:** 0.1

Selection does not receive direct mutation authority. The Evolution Boundary converts a validated selection into a bounded evolution input.

```text
Selected Candidate
       ↓
Policy + digest verification
       ↓
Evolution Input
       ↓
Evolution stage
```

The evolution input contains identity, evidence references, selection provenance, policy revision and domain. It explicitly carries empty mutation, execution and commit capability sets.

`ADMITTED_FOR_EVOLUTION` means only that the selected candidate may enter the evolution stage. It does not authorize state mutation or commit.

The existing Core evolution contract remains responsible for generating and validating the proposed state transition.
