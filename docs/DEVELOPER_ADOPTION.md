# Gnozis Developer Adoption Layer

**Status:** ARCHITECTURAL BASELINE v0.1

Make federation adoption simple enough for an independent researcher or developer to turn an ordinary repository into a compatible Memory Source without adopting the private Kernel.

## Adoption path

Template → SOURCE.yaml → Domain records → Relations + provenance → Validator → GitHub Action → Registry request → Federated Source.

## Compatibility levels

**Level 0 — Ordinary repository:** no federation contract.

**Level 1 — Structured Source:** SOURCE.yaml, schemas and provenance.

**Level 2 — Federated Source:** valid relations and automated validation.

**Level 3 — Verified Source:** documented verification policy and stable revision history.

These levels describe protocol capability, not quality ranking.

## Automation

A standard GitHub Action should validate SOURCE.yaml, schema versions, required provenance, relation syntax, resource references, revision metadata and license metadata.

Failure can block federation publication or registration updates according to the source policy.

## Registration

Registration is explicit. Passing CI does not automatically grant trusted Kernel consumption.

## Independent implementation

The protocol should remain documented well enough for implementations outside GitHub.

## Developer principle

The easiest way to join should be to publish useful, well-provenanced knowledge—not to adopt proprietary infrastructure.
