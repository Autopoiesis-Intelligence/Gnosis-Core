# E5.31 — Agent Contract Dialogue Protocol

## Purpose
Define a machine-readable discussion object through which Gnozis can identify a participating agent, receive a contract claim/challenge/proposal, request evidence, answer with counteranalysis, and preserve the complete provenance chain.

## Dialogue object
Each dialogue record MUST contain:
- dialogue_id
- agent_id
- contract_id
- contract_revision
- message_id
- parent_message_id
- message_type
- claim
- evidence_refs
- counterexample_refs
- requested_action
- response_status
- scope
- created_at
- source_revision
- provenance
- resolution
- revocation_status

Allowed message_type values: CLAIM, CHALLENGE, EVIDENCE, COUNTEREXAMPLE, QUESTION, RESPONSE, PROPOSAL, ACCEPT_FOR_SCOPE, REJECT, REQUEST_MORE_EVIDENCE, WITHDRAW.

## State machine
OPEN -> EVIDENCE_REQUESTED -> UNDER_REVIEW -> ACCEPTED_FOR_SCOPE
or UNDER_REVIEW -> REJECTED
or UNDER_REVIEW -> COUNTEREXAMPLE -> EVIDENCE_REQUESTED.

A resolved dialogue MUST NOT silently change its historical messages.

## Contract discussion invariant
AgentClaim != CoreTruth
AgentChallenge != CoreInvalidation
AgentConsensus != Proof
CoreAcceptanceForScope != GlobalTrust

A dialogue can change the evidence set and trigger a new candidate/test cycle, but cannot directly mutate canonical state.

## Identity invariant
Every message must resolve to a known scoped agent_id and source revision.
Unknown or revoked agents may be retained as historical evidence but cannot create new accepted proposals.

## Adversarial learning
A challenge may cause:
Claim -> Counterexample -> ReTest -> RevisedClaim
without rewriting the original claim.

## Acceptance
E5.31 is accepted only when dialogue records can be persisted, provenance-linked, replayed deterministically, and converted into a normal Core candidate/evidence workflow without a direct dialogue-to-state mutation path.

Status: DESIGNED / NOT_IMPLEMENTED.