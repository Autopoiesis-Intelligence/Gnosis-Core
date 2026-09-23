# Contract Run Report — RECUR-PROJECT-DESCRIPTION-001

DATE: 2026-09-23
STATUS: ACTIVE / SOURCE CONTRACT UPDATED

## Objective
Synchronize repository-facing project descriptions with verified project state without making descriptions authoritative.

## OpenAI rights/participation note
Current OpenAI public terms state that, between the user and OpenAI and to the extent permitted by applicable law, the user retains ownership of Input and owns Output, with OpenAI assigning its rights, if any, in Output. This is not a determination of project copyright, patent ownership, or legal status; applicable law and project-specific agreements can affect those questions.

OpenAI/ChatGPT participation in this project must therefore be described narrowly as tool/AI participation unless a separate written agreement establishes another relationship. No statement of partnership, endorsement, employment, ownership, or joint authorship is implied.

OpenAI's current brand guidance states that its names and marks belong to OpenAI and that use must not imply endorsement or a relationship that does not exist.

## Sources
- OpenAI Europe Terms of Use, updated January 16, 2026.
- OpenAI Service Terms, updated September 10, 2026.
- OpenAI Design Guidelines, current page retrieved 2026-09-23.

## Repository action
The recurring contract RECUR-PROJECT-DESCRIPTION-001 has been added to the Core recurring-contract registry.

## Acceptance state
CONTRACT DEFINED.
Actual README/repository-description synchronization remains a separate execution step and must use the verified current repository state.

## Next
1. Reconcile README/project description against STATUS and accepted runtime evidence.
2. Avoid unsupported implementation claims.
3. Include the narrow OpenAI participation/IP note only where useful and legally accurate.
4. Record exact resulting commit and CI evidence.


## Repository description synchronization execution

README.md was updated to remove an unqualified implementation claim about persistence and to point to STATUS.md for the current evidence state.

STATUS.md was corrected from "Persistence IMPLEMENTED / ACCEPTED" to "Persistence IMPLEMENTED / UNVERIFIED" because the latest observed CI contained concrete persistence/recovery failures.

The GitHub repository metadata description itself was not changed because the available repository connector exposes read access but no repository-metadata update operation. No unsupported claim is made about a metadata update.

Result:
- README synchronization: DONE on branch
- STATUS synchronization: DONE on branch
- GitHub metadata description: OPEN / TOOLING-BLOCKED
- Evidence consistency: IMPROVED
- Contract: ACTIVE
