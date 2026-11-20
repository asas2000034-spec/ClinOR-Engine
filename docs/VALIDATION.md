# Validation and review controls

EVIDORIX supports discovery across specialties. No specialty has a clinically validated treatment-selection pathway here. Discovery labels are bibliographic heuristics. A citation identifier confirms a retrieved record exists. It cannot establish that a generated statement follows from that record.

Every solver defaults to the sandbox. For clinical requests an operator must configure CLINOR_REVIEW_DIRECTORY outside the public tree. Protect this directory with OS permissions. After independently reviewing the complete input, reviewer identity, source URL, version, hard exclusions, and prerequisites, install a JSON record named with the output of clinor.reviews.model_digest(request) followed by .json. Record fields are revision, state, change_note, effective_from and expires_at. Dates require time zones. Only approved, currently effective records authorize computation. Revoke permission by changing state to revoked. Preserve previous revisions in access-controlled version history. No records ship enabled.

The digest binds the request schema, approval metadata and all parameter values. A changed weight, option, or restriction needs fresh review. The local operator is responsible for verifying reviewer identity. The software does not independently verify licenses, jurisdictional applicability, contraindication completeness, guideline conflicts, or patient eligibility.

Synthetic tests cover solver constraints and reference calculations. MILP benchmarks selecting the three largest integer benefits from 0 through n-1 yielded objectives 9 and 114 for n=5 and n=40. These are implementation checks only. No clinical efficacy, outcome improvement, diagnostic accuracy or production security certification has been established.
