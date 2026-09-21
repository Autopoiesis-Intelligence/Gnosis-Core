# Research Machine → Core Dependency Map R1.3

Status: ACTIVE
Baseline: Gnozis-V2 main @ 3daf7a0395426cb706a04c8b3d1672eb77b0870f

## Purpose

Measure which Research Machine knowledge items have an actual engineering consequence in Gnozis-V2, without treating research claims as Core authority.

## Findings

The current canonical Research Machine contains 185 records: 2 research records (R) and 183 claim records (C).

A representative inspection of C-0001 through C-0005, C-0126 and C-0184 shows a consistent pattern:

Research claim
→ explicit engineering consequence
→ explicit engineering gap
→ core_admissibility: RESEARCH_ONLY

This is a healthy separation. The claims can inform engineering work without becoming runtime truth merely because they are recorded.

## Dependency classes

### A. RESEARCH_ONLY

Claims with an engineering consequence but no admitted Core contract.

Examples:
- C-0001: proof continuity ≠ semantic continuity.
- C-0004: test validity ≠ test adequacy.
- C-0126: impact propagation must account for acceptance logic.
- C-0184: temporal provenance matters for adaptive verification.

These remain Research Machine knowledge. They may generate bounded engineering tasks, but they do not directly authorize a Core change.

### B. CORE-REFERENCED

A Research Machine record should receive this classification only when an explicit Core contract, implementation, test, or task references its stable ID.

No sampled claim was promoted to this class merely because its engineering consequence sounds important.

### C. CORE-ADMITTED

This is a stronger state and requires explicit evidence that the relevant proposition has been translated into a Core requirement/contract and accepted through the project's governance path.

No sampled claim is currently promoted on the basis of static research text alone.

### D. SUPERSEDED / HISTORICAL

Historical claims remain queryable and provenance-preserving. Supersession changes their lifecycle status; it does not erase their evidentiary history.

## Architectural rule

The direction of authority is:

Research Machine
→ evidence / knowledge / candidate engineering consequence
→ explicit Core requirement
→ implementation
→ verification
→ governance acceptance

Never:

Research Machine
→ implicit runtime authority

## Immediate engineering opportunity

The existing claims already expose many concrete gaps. The next conversion mechanism should therefore not copy claims into Core. It should create a traceable bridge:

research_record_id
→ engineering_task_id
→ core_path / contract
→ verification_evidence
→ acceptance

This allows the project to measure Research → Engineering conversion directly.

## R1.3 decision

Do not migrate the 183 C-records into V2.

Do not duplicate their contents.

Keep the Research Machine canonical and make V2 reference stable Research Machine IDs only when a concrete engineering dependency exists.

## Next bounded task

Define the minimal reference format in Gnozis-V2 for a Core task/contract to cite a Research Machine record without importing the record's authority or duplicating its semantics.
