# Professors feedback implementation handoff

The November 19 requirements and design are the revised specification. The code at d73c2c4896967e3d913116567fa9b7504d350c31 remains the dealership feasibility demo. The written scope and acceptance tests align with the professors' annotated feedback. The subsequent fall implementation adds shared business configuration and service inquiries; see [fall progress](fall-progress.md) for executed checks and remaining live verification. The baseline evidence below describes the earlier vehicle demo.

## Current evidence

- backend/main.py has business-filtered owner/staff routes for vehicle drafts, approval, public snapshots, inquiries and diagnostics. It verifies users through Supabase Auth.
- migrations/001_demo.sql has businesses, a one-business-per-subject membership table, vehicle-bound inquiries and AI task metadata. Migration 002 links AI tasks to listings.
- backend/ai.py calls the account model catalogue, then xAI for draft/classification. It records result and provider usage metadata after the attempt. It has a project attempt cap, not the full per-business usage model.
- Customer questions support price and mileage. Unknown questions offer a saved inquiry. There are no voice, appointment, general business configuration or administration routes.
- Existing test results in docs/local-demo-handoff.md are historical. This documentation revision does not rerun or certify live integrations.

## Original fall continuation plan

1. Work from feat/feasibility-demo and preserve uncommitted local work. Use a feature branch. Read AGENTS.md and the revised requirements/design.
2. Add atomic, checksum-tracked migrations for business domain/slug/status, departments, service definitions, intake schema revisions and approved knowledge. Preserve original rows and published snapshots. Do not edit already-applied migration checksums.
3. Extend inquiries to support an optional listing and a required business, request type, service if relevant, source interaction and explicit submission. Keep old payloads compatible and map old open state to New at the API boundary until clients migrate.
4. Add business-scoped configuration and generic public request endpoints. Validate concrete service schemas. Adapt the dashboard to show shared services/rules and domain-specific fields. Preserve vehicle drafting/publication.
5. Supply separate dealership and salon fixtures with different hours, intake and service rules. Treat fixtures as synthetic data. Make no claims of new stakeholder interviews.
6. Add focused regression tests for existing listings, tenant isolation and inquiry compatibility. Keep provider calls mocked. Rebuild the frontend and rehearse the two-business flow.

## Later final-system work

Implement platform administration, business-user CRUD, department grants and privileged MFA before exposing multi-business administration. Follow with transactional resource scheduling, reminders/outbox, test activation and voice. Implement dealership appraisal, test drives, sales/lease records, title cases, service status, comparison and approved-policy answers, then the studio and retained event modules. Verify sandbox subscription state and hosted deployment.

The project instruction is to complete fall work before starting the final spring build. The final-system requirements document the required destination and dependencies. Additional paid services require a concrete cost decision. The existing authorized xAI allowance is $5.

## Review proof

Every feedback item is mapped in requirements.md Appendix A. Every functional requirement has a matching acceptance test, and the use-case table maps the full set. Do not represent drafted requirements as implemented features. Use code changes, executed tests, integration evidence and a browser rehearsal to advance feature status.
