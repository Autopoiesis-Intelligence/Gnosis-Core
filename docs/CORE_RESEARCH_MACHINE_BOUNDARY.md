# Gnozis Core ↔ Research Machine Boundary Contract

## Status

ACTIVE — restructuring R1.

## 1. Canonical ownership

**Gnozis Core owns:**
- canonical Ψ state and transitions;
- invariants and verification;
- protected execution/authorization boundaries;
- durable evolutionary state and recovery;
- Core analytical layers, autopoiesis, memory and internal sandbox;
- evidence required to establish canonical state.

**Gnozis Research Machine owns:**
- machine-readable research;
- reverse-analysis and mathematical exploration;
- task/handoff continuity;
- AI_CONTEXT and development-session memory;
- historical findings, rejected hypotheses and research provenance;
- temporary analysis that has not passed the engineering admission path.

Research Machine is development memory/knowledge infrastructure. It is not a second Core.

## 2. Allowed direction

The normal information path is:

Research Machine
→ Knowledge Interface
→ Engineering consequence
→ bounded Core task
→ implementation
→ test/CI
→ audit
→ acceptance

Core may emit evidence, findings and provenance references back to the Research Machine.

Neither direction grants the receiving side authority by itself.

## 3. Forbidden crossings

Research Machine MUST NOT:
- directly mutate canonical Ψ state;
- directly authorize a transition;
- bypass Core validation or verification;
- become the source of truth for canonical evolution state;
- silently replace Core invariants with documentation or task metadata.

Core MUST NOT:
- require the entire research corpus to execute;
- treat AI_CONTEXT as canonical state;
- import historical conclusions as executable authority;
- depend on conversation history.

## 4. Admissible payloads

Research → Core may contain only bounded, typed information such as:
- requirement;
- hypothesis;
- candidate rule/proposal;
- evidence reference;
- counterexample;
- task specification;
- provenance;
- explicit admissibility/status.

Core decides applicability and authority.

Core → Research Machine may contain:
- implementation result;
- test result;
- CI result;
- audit finding;
- counterexample;
- failure evidence;
- stable identifiers and commit references.

These are evidence, not instructions to bypass Core.

## 5. Development memory rule

AI_CONTEXT and task/handoff material are continuity mechanisms. They may describe what should be investigated or implemented, but documentation alone never proves implementation.

A development-memory record can become durable engineering evidence only through the normal executable evidence path.

## 6. Physical separation rule

During R1, semantic separation precedes physical repository separation.

Do not move/delete material merely because it is classified as Research Machine material. First preserve:
- stable identifier;
- source path;
- source commit;
- provenance;
- status;
- destination/reference.

Physical extraction is a later controlled migration.

## 7. Kernel expansion

Core may gain additional internal tools when a demonstrated condition requires them, provided the new capability:
1. has an explicit contract;
2. has a bounded authority scope;
3. preserves Ψ/invariant semantics;
4. has executable evidence;
5. does not convert Research Machine or task memory into hidden authority.

The internal sandbox remains part of Core.

## 8. Acceptance gate

The boundary is considered implemented only when:
- both sides have explicit ownership;
- crossing data has a defined contract;
- unauthorized mutation paths are tested;
- provenance survives the crossing;
- Core remains executable without the research corpus;
- Research Machine remains useful without being granted Core authority.
