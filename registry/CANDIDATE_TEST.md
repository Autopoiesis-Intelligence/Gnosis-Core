# Candidate Test Contract

**Version:** 0.1

A federated candidate is admitted to an isolated test input only after deterministic validation.

```text
Candidate
   ↓
Integrity + Policy Check
   ↓
Isolated Test Input
   ↓
Test Execution
```

The generated test input contains no execution, mutation or selector capabilities. It carries only candidate/evidence identity and the immutable test-policy revision.

The test layer therefore evaluates a candidate without allowing the candidate, its source repository, or its payload to choose the test outcome or modify Core state.

Admission to test is not selection, evolution or commit.
