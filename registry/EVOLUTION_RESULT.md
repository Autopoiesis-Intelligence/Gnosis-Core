# Evolution Result Contract

**Version:** 0.1

Evolution produces a proposal record, never an implicit commit.

Allowed results:

- `PROPOSED`
- `NO_CHANGE`
- `REJECTED`
- `FAILED`

A `PROPOSED` result requires a proposed transition and evidence. Every result requires candidate/evolution identity, immutable policy identity and revision, input digest, deterministic flag and result digest.

The result has no commit capability. A valid proposal must enter the independent Verify and Commit gates.

```text
Evolution Input
      ↓
  Evolution
      ↓
Evolution Result
      ↓
   Verify
      ↓
 Commit Gate
```
