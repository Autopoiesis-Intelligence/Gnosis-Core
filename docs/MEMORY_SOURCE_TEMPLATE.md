# Gnozis Memory Source Template

**Status:** ARCHITECTURAL BASELINE v0.1

An independent domain repository can participate in the Gnozis federated Memory Network through a small, open contract.

## Recommended structure

```text
<domain-source>/
├── README.md
├── LICENSE
├── SOURCE.yaml
├── schema/
├── records/
├── relations/
├── evidence/
├── provenance/
├── validation/
└── .github/workflows/gnozis-validation.yml
```

`SOURCE.yaml` declares source_id, domain, protocol/schema versions, repository identity, license, provenance policy, verification policy and federation status.

## CI expectations

A compatible source should validate schema, relation format, provenance, revision identity, content integrity where configured, license metadata and registry consistency.

## Independence

The template does not require use of the private Kernel or proprietary Genezis implementation. Federation does not grant write access to Genezis or Kernel state.

A source can begin as an ordinary repository and adopt the contract incrementally.
