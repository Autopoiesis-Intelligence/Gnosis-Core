# Preliminary Hidden Contract Inventory — Future Agent Evolution

This is a discovery inventory extracted from existing architecture, audits, AI_CONTEXT and repository synchronization requirements. It is a candidate registry, not proof of implementation.

| Candidate ID | Hidden contract | Why it exists | Initial state |
|---|---|---|---|
| AG-01 | Agent Identity & Continuity | Agent identity must remain stable across submissions/revisions/keys | DESIGNED |
| AG-02 | Agent Capability Negotiation | Requested capability must be separated from granted capability | DESIGNED |
| AG-03 | Agent Contract Dialogue | Agents need structured claim/challenge/evidence dialogue | DESIGNED |
| AG-04 | Agent Memory / Session Continuity | Dialogue and contribution history must survive restart without becoming Core state | MISSING |
| AG-05 | Agent Revocation & Supersession | Identity, keys and capabilities need bounded withdrawal and replacement | DESIGNED |
| AG-06 | Agent Contribution Provenance | Every proposal/evidence/test must remain traceable to source revision | DESIGNED |
| AG-07 | Agent Conflict-of-Interest Declaration | Partner influence must be represented as evidence context, not hidden trust | DESIGNED |
| AG-08 | Multi-Agent Evidence Independence | Similar submissions must not be counted as independent without provenance analysis | DESIGNED |
| AG-09 | Agent Adversarial Challenge Budget | Challenge generation must be bounded and non-sovereign | THEORETICAL |
| AG-10 | Agent Consensus Non-Authority | Consensus cannot directly authorize a Core transition | DESIGNED |
| AG-11 | Agent Proposal Expiry / Freshness | Old proposals must not be silently reused after relevant state changes | DESIGNED |
| AG-12 | Agent Dataset Revision Binding | Learning material must remain tied to immutable dataset revision | DESIGNED |
| AG-13 | Agent Sandbox Boundary | Partner code/tools cannot gain execution/network/credential access by participation alone | DESIGNED |
| AG-14 | Agent-to-Agent Communication Provenance | Cross-agent messages require sender, recipient, lineage and revision binding | MISSING |
| AG-15 | Agent Contract Escalation | Unresolved contract disputes need deterministic escalation/stop conditions | THEORETICAL |
| AG-16 | Agent Withdrawal / Claim Retraction | A participant must be able to retract a claim without rewriting history | DESIGNED |
| AG-17 | Agent Evaluation Independence | An agent must not certify its own boundary expansion solely from its own evaluation | DESIGNED |
| AG-18 | Repository/Agent Capability Drift | Changes in an agent repository may invalidate its previous capability grant | MISSING |
| AG-19 | Cross-Repository Update Synchronization | Public/project information must track verified repository state and commit | DESIGNED |
| AG-20 | Agent Learning Feedback Boundary | Learned knowledge may generate candidates but cannot directly mutate canonical state | DESIGNED |
| AG-21 | Human Override / Local Approver Boundary | Human authorization must remain distinct from agent recommendation | DESIGNED |
| AG-22 | Agent Audit Replay | Agent decisions/discussions must be replayable from immutable evidence | MISSING |

## Discovery rule
Future audits SHOULD treat this inventory as a hypothesis list. A candidate contract becomes active only after its scope, invariants, evidence requirements, dependencies and acceptance tests are explicitly defined.

## Priority suggestion
P0: AG-01, AG-02, AG-05, AG-06, AG-11, AG-18, AG-19, AG-22.
P1: AG-03, AG-04, AG-08, AG-12, AG-13, AG-14, AG-15, AG-17, AG-20, AG-21.
P2: AG-07, AG-09, AG-10, AG-16.

Status: DISCOVERY / PRELIMINARY.