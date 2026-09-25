# Gnozis Memory Network — Domain Taxonomy

**Status:** ARCHITECTURAL BASELINE
**Date:** 2026-09-25

## Principle

The Memory Network is not a fixed catalogue of sciences. It is an extensible, machine-readable map of human knowledge, research and problem-solving resources.

A domain repository may represent an established discipline, interdisciplinary field, applied domain, research program or other coherent knowledge boundary.

## Initial domain families

- Mathematics
- Physics
- Chemistry
- Biology and Life Sciences
- Medicine and Health Sciences
- Neuroscience
- Computer Science
- Artificial Intelligence
- Engineering
- Materials Science
- Earth and Environmental Sciences
- Astronomy and Space Science
- Climate and Energy
- Psychology and Cognitive Science
- Economics and Finance
- Sociology
- Anthropology
- Linguistics
- History
- Philosophy
- Political and Legal Studies
- Education
- Architecture and Design
- Arts and Culture
- Agriculture and Food
- Robotics
- Systems and Complexity Science
- Cross-Domain Research
- Open Problems and Human Questions

This list is an initial taxonomy, not a repository creation mandate.

## Repository creation rule

A dedicated memory repository is justified when a knowledge area has a meaningful independent boundary in one or more of:

- domain;
- lifecycle;
- ownership;
- access policy;
- provenance;
- community;
- licensing;
- research workflow.

Otherwise, the material should remain in an existing domain or cross-domain repository.

## Cross-domain layer

Cross-domain relationships are first-class knowledge.

A relationship may connect concepts, evidence, models, methods or open problems from multiple domains. Cross-domain records MUST retain provenance to each contributing source.

## Memory record classes

Domain repositories may contain:

- definitions;
- models;
- axioms and assumptions;
- observations;
- evidence;
- proofs;
- experiments;
- datasets;
- counterexamples;
- hypotheses;
- conjectures;
- relationships;
- open problems;
- research questions;
- methods;
- provenance;
- validation records.

The schema MUST distinguish established evidence from hypotheses, interpretations and unresolved questions.

## Kernel interaction

The private Kernel may register a domain repository as a Memory Source through an explicit Memory Source Contract.

Registration does not imply trust.

The lifecycle remains:

```
source revision
 -> provenance
 -> schema validation
 -> candidate evidence
 -> Kernel evaluation
 -> verified memory
 -> optional incorporation
```

## Extensibility

New domains do not require Kernel redesign if they conform to the Memory Source Contract and common machine-readable schemas.

The taxonomy is therefore a discovery/indexing layer, not a hard architectural dependency.
