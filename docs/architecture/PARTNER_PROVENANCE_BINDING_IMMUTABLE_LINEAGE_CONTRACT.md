# E7.25 — Partner Provenance Binding & Immutable Contribution Lineage Contract

## Objective

Bind every accepted or quarantined partner contribution to an immutable, auditable provenance lineage from partner identity and source revision through validation and all derived learning artifacts.

## Provenance tuple

For contribution c:

P(c) = (partner_identity, source_id, source_revision, manifest_revision, contribution_id, content_digest)

The tuple MUST identify the exact declared origin of the contribution.

A provenance binding is valid only when every mandatory component is present and internally consistent.

## Lineage

The minimum lineage is:

PartnerIdentity
-> Source
-> SourceRevision
-> ManifestRevision
-> Contribution
-> ValidationEvent*
-> AdmissionEvent?
-> DerivedArtifact*
-> GovernanceDecision?

Each edge MUST be explicit.

A derived artifact MUST NOT lose the provenance of the contribution(s) from which it was produced.

## Immutable binding

Once a contribution is admitted or retained as evidence, its provenance binding MUST NOT be silently edited.

Correction requires a new revision/event that references the prior record.

Therefore:

ProvenanceMutation != ProvenanceCorrection

A correction preserves history rather than rewriting it.

## Content integrity

For contribution payload x:

digest(x) = recorded_content_digest

For a derived artifact d:

digest(d) MUST be recorded independently, together with references to all source contribution identifiers used to derive it.

Changing source content MUST NOT silently preserve the old derived artifact as if it had the same evidence basis.

## Lineage closure

For every admitted contribution c:

exists P(c)

and:

all mandatory provenance edges are resolvable.

For every derived artifact d:

Sources(d) != empty

unless d is explicitly classified as an independently originated artifact.

## Multi-source derivation

If an artifact is derived from contributions c1...cn:

Sources(d) = {c1,...,cn}

The system MUST preserve the complete source set.

Partial provenance is insufficient for an artifact claimed to be derived from multiple partner sources.

## Quarantine lineage

Quarantine MUST NOT destroy provenance.

A quarantined contribution retains:

- PartnerIdentity;
- source and revision;
- manifest revision;
- content digest;
- validation result;
- failure evidence;
- lineage references.

If later revalidated, the new validation event references the existing contribution identity rather than replacing its history.

## Revocation

Revoking a partner, source or manifest MUST NOT erase historical provenance.

The system records:

RevocationEvent -> affected identities/revisions/contributions

Existing historical artifacts remain attributable to their original source, while their current usability is determined separately by policy.

## Authority boundary

Provenance establishes origin, not authority.

Provenance(c) does NOT imply:

- truth;
- trust;
- admission;
- execution authority;
- Core mutation authority.

Formally:

Provenance(c) != Authority(c)

and:

VerifiedProvenance(c) != VerifiedTruth(c)

## Replay

A replay with identical identity, source revision, manifest revision and content digest MAY resolve to the existing contribution idempotently.

A replay with conflicting provenance or content MUST fail closed.

It MUST NOT create an alternative history under the same contribution identity.

## Acceptance requirements

Implementation MUST eventually test:

1. complete provenance binding;
2. missing provenance;
3. source revision mismatch;
4. manifest revision mismatch;
5. content digest mismatch;
6. provenance-preserving quarantine;
7. immutable correction through new event/revision;
8. multi-source derived artifact lineage;
9. revocation without history deletion;
10. identical replay;
11. conflicting replay;
12. restart/recovery of lineage;
13. provenance does not create authority;
14. derived artifacts retain source references.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract is a specification only until runtime implementation and reproducible verification exist.
