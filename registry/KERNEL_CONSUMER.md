# Kernel Consumer Contract

**Version:** 0.1

The Kernel Consumer is a separate trust boundary after Scoped Consumption.

```text
Federated Source
      ↓
Scoped Envelope
      ↓
Kernel Consumer
      ↓
Observation
      ↓
Core Evidence / Candidate Pipeline
      ↓
Independent Influence Gate
      ↓
(optional) State Commit
```

The consumer verifies the envelope version, required identity fields, content digest shape, envelope SHA-256 and capability restrictions.

A valid envelope is accepted only as an `OBSERVATION`. It does not become a Core state, relation, rule, candidate or mutation automatically.

The consumer rejects envelopes carrying mutation or execution capabilities.

This preserves the separation between retrieval/consumption and influence. A later Core pipeline must independently establish evidence and authorization before any state-changing operation.
