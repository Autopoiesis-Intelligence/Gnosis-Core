# Gnozis-V2 — Evidence and Provenance Contract

## Status

`ARCHITECTURE CONTRACT — IMPLEMENTATION NOT YET ACCEPTED`

Gnozis must be able to reconstruct not only the current answer, but why that answer is considered current. Evidence and provenance provide the bridge between connected-world observations and durable task continuity.

## 1. Logical evidence model

```text
EvidenceReference {
    evidence_id
    source_id
    locator
    content_type
    data_class
    producer
    observed_at
    captured_at?
    provenance
    verification_status
    integrity_reference?
}
```

This is a semantic model; storage is implementation-defined.

## 2. Reference before replication

Canonical TaskContext should reference durable evidence rather than silently embedding arbitrary external conversations, files, or datasets.

A reference must be sufficient for an authorized terminal to locate or reconstruct the evidence under the applicable source policy.

## 3. Provenance

Provenance should eventually answer:

```text
where did this evidence originate?
who/what produced it?
when was it observed?
through which connector or process was it obtained?
what transformation occurred?
what verification was performed?
```

The provenance record must not claim stronger verification than actually occurred.

## 4. Verification states

Evidence and task state must distinguish at least:

```text
observed
reported
runtime_verified
independently_verified
accepted
rejected
```

A source saying that something is true is evidence of a report, not independent verification of the claim.

## 5. Integrity

Where technically available, evidence references should eventually include an integrity reference such as a content hash, immutable source identifier, or authenticated record reference.

Absence of cryptographic integrity must remain explicit rather than being represented as verified integrity.

## 6. Temporal semantics

The system must preserve the difference between:

```text
observed_at
captured_at
stored_at
verified_at
```

A current task answer must not silently present old evidence as a current observation.

## 7. External AI output

An AI-generated analysis may become evidence of what an AI reported or computed. It does not automatically become a verified fact.

For example:

```text
Claude report
    ↓
AI-produced evidence
    ↓
independent execution/audit
    ↓
verification state changes
```

## 8. Recovery

A new terminal reconstructing a task should be able to answer:

```text
What evidence supports the current state?
Which evidence is only reported?
Which evidence was independently verified?
Which evidence is stale?
Which source should be consulted again?
```

## 9. Cross-source aggregation

Multiple sources may provide different observations about the same task. The evidence layer must preserve source identity and provenance rather than collapsing all observations into one unattributed value.

Conflicting evidence must remain visible until an explicit resolution process exists.

## 10. Security boundary

This contract does not implement authentication, authorization, encryption, or secret management.

## 11. Core boundary

Evidence is input to reasoning and verification. It must not directly mutate Ψ-Core state or bypass Candidate → Test → Verify → Commit.

## 12. Acceptance principle

Evidence/provenance is accepted only when an independent audit can reconstruct the origin, temporal status, verification state, and scope of material evidence without relying on an AI's narrative alone.


## Research Machine provenance

This contract is informed by Research Machine record `C-0004` for the distinction between test validity and verification adequacy. The research item is rationale only; it is not Core authority and does not replace the contract's independent verification requirements.

```yaml
research_ref:
  repository: Mikhail-Kucheriavyi-23/Gnozis
  record_id: C-0004
  source_commit: 7eb7caeb6a82e09e3bf40feef515b4db25b3eb0c
  relation: TEST_RATIONALE
```

## Common-mode dependency boundary

Evidence MUST NOT be treated as independent corroboration merely because it has different records, timestamps, agents, providers, or representations.

Where known, evidence provenance should preserve shared dependencies such as:
- common source or dataset;
- common model/verifier;
- common prompt or transformation;
- common upstream observation;
- shared evaluator;
- shared failure mode.

`RepeatedDetection != IndependentEvidence`.

An independence claim is always relative to a declared failure class and evidence-generation process. This contract does not require a universal statistical independence metric.