# Gnozis Partner / Agent Participation Template

Machine-readable intake contract for a person, AI platform, agent, tester, researcher, or development group requesting participation in Gnozis evolution.

## 0. Submission identity
- agent_id: globally unique proposed identifier
- agent_type: HUMAN | AI_PLATFORM | AGENT | TESTER | RESEARCH_GROUP | HYBRID
- display_name:
- organization_or_project:
- contact_reference:
- submission_version:
- created_at:
- source_repository:
- source_revision:
- declared_role:

## 1. Participation intent
- participation_goal:
- problems_of_interest:
- domains:
- expected_contribution:
- requested_access_level:
- requested_contracts:
- constraints:
- known_conflicts_of_interest:

## 2. Proposed agency
Requested capabilities:
- READ_RESEARCH
- SUBMIT_EVIDENCE
- SUBMIT_CANDIDATE
- SUBMIT_TEST
- REQUEST_REVIEW
- DISCUSS_CONTRACT
- PROPOSE_CHANGE
- MAINTAIN_PARTNER_DATASET
- EXECUTION_AUTHORITY

Requested capability does not constitute granted capability.

## 3. Evidence and provenance
- claims:
- supporting_evidence:
- evidence_sources:
- known_uncertainty:
- known_counterexamples:
- reproduction_method:
- source_license_or_usage_constraints:

## 4. Technical interface
- repository:
- database_or_dataset:
- schema_version:
- supported_protocols:
- agent_endpoint_or_connector:
- read_capabilities:
- write_capabilities:
- sandbox_requirements:
- network_requirements:

No credentials or secrets belong in this template.

## 5. Contract participation
The agent must declare:
- contracts it accepts;
- contracts it challenges;
- contracts it proposes;
- assumptions it believes are missing;
- invariants it believes should be tested;
- failure cases it expects;
- conditions under which it will withdraw a claim.

## 6. Debate / discussion profile
- preferred_reasoning_style:
- challenge_policy:
- disagreement_protocol:
- evidence_standard:
- response_deadline_or_budget:
- will_accept_core_rejection: true | false
- will_revise_claims: true | false

The purpose is adversarial cooperation, not authority delegation.

## 7. Audit declaration
- self_declared_limitations:
- known_security_risks:
- known_data_quality_risks:
- known_dependency_risks:
- requested_audit_scope:
- previous_audit_references:

## 8. Machine identity material
The submission MUST distinguish human-readable identity from machine identity.
- agent_public_key:
- identity_method:
- identity_scope:
- key_rotation_policy:
- revocation_reference:

Private keys, tokens and credentials MUST NEVER be submitted.

## 9. Dataset contribution
If the participant supplies a learning repository/database:
- dataset_id:
- dataset_revision:
- dataset_schema:
- dataset_purpose:
- provenance_policy:
- update_policy:
- revocation_policy:
- retention_policy:
- derived_work_policy:

## 10. Declaration
The submitting party declares that the information above describes the intended participation scope and does not itself grant access or authority.
- submitted_by:
- submission_signature:
- submission_timestamp:

## Machine processing result
This section is filled by Gnozis, not the applicant:
- normalized_agent_id:
- identity_status:
- provenance_status:
- audit_status:
- data_status:
- discussion_status:
- granted_capabilities:
- quarantine_status:
- contract_participation_status:
- revocation_status:
- core_verification_references:

## Core rules
SubmittedParticipation != AcceptedParticipation
Identity != Trust
Trust != Authority
Discussion != Authorization
PartnerData != CoreState

The template is an intake protocol, not a permission mechanism.