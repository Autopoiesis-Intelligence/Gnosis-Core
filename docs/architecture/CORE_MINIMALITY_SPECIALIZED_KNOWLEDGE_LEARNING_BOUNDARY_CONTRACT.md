# E7.39 — Core Minimality & Specialized Knowledge/Learning Layer Boundary Contract

## Objective

Define the canonical Core as the common, minimal and effective mechanics shared by all governed deployments, while keeping domain knowledge, datasets, learned models and domain-specific policies in replaceable specialization layers.

## Core definition

The canonical Core is a mechanism, not a universal knowledge repository.

Let:

Core = M_min

where M_min contains only mechanics required to preserve the project's universal invariants and execute governed state/evolution transitions.

Core MUST NOT require domain-specific knowledge in order to preserve its own invariants.

## Specialization model

A governed deployment MAY be represented as:

G_i = Core + K_i + D_i + L_i + P_i

where:

- K_i = domain knowledge;
- D_i = domain datasets/evidence;
- L_i = learned models/derived structures;
- P_i = domain-specific policy/configuration.

These layers remain distinguishable from Core mechanics.

Examples include financial analysis, enterprise IT, software engineering, game development and scientific research.

## Core minimality

A proposed addition MUST NOT enter canonical Core merely because it is useful to one specialization.

Candidate addition x requires evidence that x is a domain-independent mechanism necessary for universal invariants or governed interoperability.

Otherwise x belongs in a specialization layer, adapter, tool, policy or external knowledge repository.

## Knowledge boundary

The following MUST NOT be treated as canonical Core merely because they are learned or highly useful:

- domain facts;
- market data;
- company-specific information;
- customer/private datasets;
- game/project assets or rules;
- domain heuristics;
- learned predictions;
- specialized models;
- partner-specific workflows.

They MAY be referenced or consumed through governed interfaces.

## Learning boundary

A specialization MAY learn, update and evolve within its granted scope.

Learning MUST NOT silently mutate canonical Core mechanics.

A proposed Core change MUST enter the normal governed development/change process with provenance and verification.

Formally:

Learn_i -> Specialization_i

does not imply:

Learn_i -> Core

## Shared knowledge

Knowledge MAY be classified as:

- CORE_MECHANISM;
- SPECIALIZED_PRIVATE;
- SPECIALIZED_SHARED;
- PUBLIC_EXTERNAL;
- EXPERIMENTAL;
- UNVERIFIED.

Classification MUST be explicit where required.

Shared/public knowledge may be reused across deployments only through the applicable provenance, licensing, privacy and policy boundaries.

## Cross-partner isolation

Private knowledge learned by Partner A MUST NOT become available to Partner B merely because both instantiate the same Core.

Shared knowledge requires explicit classification and transfer authorization.

## Core upgrade

A Core upgrade MUST be represented as a new Core revision.

A specialization MUST declare the Core revision against which it was validated.

Silent substitution of Core mechanics is prohibited for governed deployments.

## Compatibility

A specialization MAY remain on an older compatible Core revision according to policy.

Compatibility MUST NOT be inferred solely from version strings.

Where a Core change affects an invariant or trust boundary, revalidation MUST be required.

## Knowledge portability

Specialized knowledge MAY be exported/imported separately from Core.

Portable knowledge MUST preserve provenance, schema/version and applicable policy restrictions.

Import MUST NOT modify canonical Core mechanics.

## De-specialization

Removing a specialization layer MUST NOT corrupt or redefine Core.

Core MUST remain valid with no particular domain knowledge attached, subject to its declared minimum operating requirements.

## Acceptance requirements

Implementation MUST eventually test:

1. Core operates without domain dataset;
2. financial specialization isolation;
3. IT specialization isolation;
4. game-development specialization isolation;
5. private/shared knowledge classification;
6. learning cannot silently mutate Core;
7. proposed Core change enters governed change process;
8. Core revision compatibility;
9. specialization on multiple Core revisions;
10. knowledge export/import without Core mutation;
11. cross-partner private-knowledge isolation;
12. de-specialization;
13. provenance preservation;
14. restart/recovery;
15. deterministic boundary enforcement.

## Status

DESIGNED / NOT_IMPLEMENTED.

This contract defines Core minimality and the boundary between universal mechanics and specialized learning/knowledge. It does not claim that the corresponding runtime architecture is implemented.
