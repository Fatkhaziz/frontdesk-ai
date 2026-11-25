# FrontDesk AI Detailed System Design

> November 24 scope update: the current dealership AI showcase, setup, acceptance criteria and evidence map are in [showcase-release.md](showcase-release.md). This document retains earlier baseline or full-system design details; three live business examples are no longer required for the fall showcase.

CIS 457 Senior Design 1 | Team submission | Revised November 19, 2026

Fatkhaziz Mukhamedov, Al Baraa Khaled, Mohammad Abdullah, Amar Al Balkhi

> November 24 implementation status: [Fall Release 1](fall-release-1.md) adds shared studio configuration and evidence-checked natural-language business Q&A. The full-system architecture below includes future work; its earlier demo-gap statements describe the November 19 baseline.

## 1 Scope and architectural decisions

This design implements the revised FrontDesk AI Requirements Use Cases and Constraints dated November 19, 2026. The target is one hosted platform serving businesses in different domains with shared receptionist services and separate operating rules. The configured examples are a dealership, salon and photography studio. The current dealership demo is a working subset. New entities, endpoints and workflows below are implementation designs.

The architecture retains React and TypeScript, a modular Python FastAPI backend, Supabase PostgreSQL/Auth/storage and server-side xAI requests. Shared modules handle administration, configuration, approval, reception, resources, inquiries, delivery and evidence. Domain modules provide fields and rules. A separate worker executes durable reminder, notification, synchronization and retention jobs.

The final hosted website runs on a hosted service such as Render. The local Mac remains a development and demo environment. No local language model is required. Provider availability, selected model and costs are checked during integration. The existing authorized xAI budget remains $5.

## 2 Components and trust boundaries

| Component | Responsibility | Boundary |
| --- | --- | --- |
| React dashboard and customer pages | Platform administration, business setup, content approval, domain work, appointments, inquiries and evidence | Browser receives permitted public configuration and user tokens. It never receives database or provider secrets. |
| FastAPI identity and authorization | Verify authentication, role, active business membership and department on every protected operation | A business ID supplied by a client never proves membership. Customer actions need verified authority for the selected record. |
| Shared workflow modules | Versioned rules, appointments, publication, handoff, usage and audit | Application services validate changes and own transactions. The model cannot directly write database rows. |
| Domain modules | Dealership stock/trade-ins/sales/leases/service/title cases, salon skills/chairs, studio packages/resources | Modules use the same tenant and resource contracts with domain validation. |
| Supabase | Managed identity, relational data and private object storage | Backend database roles are restricted. Public API roles cannot read application tables directly in the current architecture. |
| AI gateway | Build minimal prompts, validate structured output, enforce usage and record outcomes | Output is untrusted input. The backend retrieves approved values and performs authorized actions. |
| Worker and provider adapters | Deliver notices, process signed events, reconcile jobs and purge expired content | External calls use bounded retries and stable event IDs. Completion follows verified outcomes. |

FIGURE_ARCHITECTURE

## 3 Identity and business isolation

There are four user roles in the requirements. Platform administrators have separate platform grants. Business administrators and domain staff have scoped memberships. Public customers select a business by an approved slug, listing link or called number. Private customer records require a verified management token or contact code.

Supabase Auth owns sign-in and password verification. Its password security documentation states that password hashes use bcrypt [1]. The application stores a user subject reference and permissions, with no password column. Privileged access requires an MFA session assurance level of aal2 in addition to the current membership check [2]. Session inactivity and throttling targets are verified in the application and chosen provider configuration.

The backend resolves business_id from a trusted membership or a public resource lookup, then adds business and department predicates to every query. Child records use composite foreign keys to prevent linking one business's inquiry, booking or vehicle to another's record. A platform role cannot be assigned through a business invitation. A support session has actor, business, purpose, start, expiry and audit records.

The current demo's memberships table uses subject as its primary key and supports owner/staff. The planned migration introduces a separate platform_admins table and business memberships keyed by business_id and subject. Existing owner becomes business_admin. Existing staff becomes domain_staff with an explicit department assignment reviewed during migration. Historical roles and actors remain readable.

## 4 Shared configuration and revision model

Business templates define available module names, allowed service fields and default forms. A business configuration revision contains hours, holidays, time zone, service catalogue, resource rules, inquiry schemas, routing rules, notification subscriptions, enabled channels and greeting revision. Templates are copied into a private business revision before editing. Editing a template never silently changes an active business.

Business administrators activate validated revisions. Staff contributors may propose revisions only for assigned departments. Approved knowledge stores source, question/answer or factual field, applicable service, effective interval, revision and approver. Public content and active rules are immutable snapshots until explicitly replaced.

Every public session is bound to a business and current configuration revision. Published records can change during a conversation. The backend re-reads the active published snapshot before returning factual values, so a private draft cannot leak into an answer. Booking commit rechecks resource rules and capacity. A disabled business or module is refused on the next action.

### Configuration validation

Validate every Section 3 required field in the requirements with a typed request model. Restrict question types to short text, long text, number, date/time, yes/no, approved choice and contact. Store required flags and field constraints as schema data. Required operational fields must be present before automatic completion. An explicitly submitted staff request can record unanswered fields.

Normalize US numbers into E.164 using a maintained number parser. Distinguish parse validity, reachability test result and verified customer control. Caller ID plus a name is insufficient to authorize a booking change. Verify a one-time code or a signed, expiring appointment-management token before returning private details.

## 5 Data model and integrity

The existing demo has businesses, memberships, listings, inquiries, ai_tasks, audit_events, ai_budget, listing_ai_tasks and schema_migrations. It stores listing facts and snapshots as text containing JSON. Keep those records and migration checksums intact. Add new tables and nullable columns, backfill explicitly, then switch callers through compatible serializers.

| Entity group | Planned entities and minimum fields | Integrity |
| --- | --- | --- |
| Administration | businesses with slug/domain/status, platform_admins, business_memberships, departments, department_grants | Unique business slug. Composite membership key. Separate platform authorization. |
| Configuration | domain_templates, business_modules, config_revisions, services, intake_schemas, routing_rules, notification_subscriptions | Every business-owned row includes business_id. A service belongs to the same configuration and department. |
| Knowledge and publication | knowledge_items, knowledge_revisions, published_snapshots, listing extensions | Approval names exact revision and actor. Effective interval and public state checked at read time. |
| Customer operations | interactions, customers when verified, inquiries with optional listing/service and source_interaction_id | Do not require a vehicle listing for general business questions. Unique business/request key. Contact verification state explicit. |
| Resources and booking | resources, staff_skills, resource_schedules, appointment_allocations, appointments, management_tokens | Composite business/resource keys. Capacity and overlap checked under lock. Token digest and expiry only. |
| Dealership | vehicle_specs, trade_ins, test_drives, sales, leases, title_cases, service_orders | Vehicle belongs to same business. One completed disposition per vehicle. Staff approval and external references explicit. |
| Delivery and evidence | outbox_jobs, delivery_attempts, provider_events, activation_tests, expanded ai_tasks and audit_events | Unique event/request keys. Signed callbacks verified. Provider status and application commit kept distinct. |
| Subscription and event modules | plans, subscriptions, subscription_events, events, registrations | Deduplicated provider events and capacity transactions. Payment card fields absent. |

FIGURE_DATA

### Existing data compatibility

Map inquiries.open to New through a compatibility serializer until all clients understand the revised states. Preserve pending/resolved meaning. Convert integer USD cents using a tested serializer and keep form entry in dollars. Preserve existing published snapshots and their revision numbers. Old AI tasks without a known source revision remain legacy records with that field empty.

An existing published listing continues to load after migration. A failed backfill or migration rolls back. New foreign keys are validated against actual data before enforcement. Customer contact fields and private stock notes are never copied into public snapshots.

## 6 Reception appointments and domain transactions

### Reception and handoff

Resolve the business, enabled module and configuration before calling the AI gateway. Classify into an allowed intent and field set. The workflow service fetches only the approved records for that business, validates structured output and constructs the factual response. Unknown, mixed or failed requests offer follow-up. A completed FAQ answer creates an interaction outcome and no inquiry.

Follow-up submission records consent, type, department, source interaction, optional listing/service, customer-provided details and request key. It commits the inquiry and notification outbox event together. The public response says saved only after commit. Delivery state is visible separately. A retry with the same key and same payload returns the original result. Reuse with a different payload returns a conflict.

### Booking and rescheduling

Represent resources separately from services. A service specifies duration, buffer, skills and needed resource types. Lock all candidate resource rows in a stable order, check overlapping allocations, insert appointment and allocations, and create the confirmation job in one transaction. Test drives lock vehicle and salesperson. Salon appointments lock stylist and chair. Studio sessions lock photographer and location resource.

Rescheduling locks the existing appointment and both resource sets before changing allocations. One commit reserves the replacement and releases the original. Cancellation is idempotent. Use a unique business/request key for every action and database constraints for record relationships. Optional external calendar synchronization runs after commit using a stable external event ID. A sync failure is shown as pending synchronization and does not claim the internal booking failed.

### Dealership workflows

Trade-ins preserve customer-stated facts and staff appraisal separately. Sale and lease transitions require authorized staff, expected revision and a vehicle lock. Completing either records an external transaction reference and updates stock availability in the same transaction. A sale/lease uniqueness rule prevents both completing for the same vehicle. No AI output can complete those transitions.

Title cases link to the completed business transaction and an approved document checklist. Service orders link a request, vehicle, appointment and staff-approved estimate. Policy answers include the exact effective approved policy revision. Comparisons select two to four public vehicles from the same business and display missing values explicitly.

## 7 Voice activation notifications and recovery

Voice is a planned adapter that maps the called number to a business. It plays the administrator-approved greeting and disclosure and passes allowed intents to the same workflow services as chat. A programmable provider exposes incoming webhooks and call-progress callbacks [3]. Verify provider signatures and deduplicate callback event IDs before updating state.

Activation tests record business_id, assigned number, started_at, deadline, expected greeting revision, provider call ID, matched callback state, playback evidence and administrator confirmation. A two-minute deadline is computed server-side. A late callback may be logged but cannot silently pass an expired test. No call-progress status alone proves the administrator heard the intended greeting.

The dashboard lists readiness for Web reception, Booking, Voice reception, Notifications and Calendar synchronization. Each shows Ready, Disabled or Needs setup plus the missing requirement. Activating one ready channel does not label unfinished channels active.

Notifications use durable outbox records committed with the business action. Jobs claim leases, record attempts and use an event/destination/channel uniqueness key. Confirmations, changes, scheduled reminders and staff alerts use distinct event types. Consent and opt-out state are checked before each delivery. Retry limits and next-attempt time are persisted. An exhausted job becomes Failed and appears in the dashboard.

Voice overload or an AI outage routes to a tested fallback, then the business's approved message route. The configured AI timeout and call-answer target must be measured with the selected provider. Provider outages and dropped connections create safe outcomes and evidence. They cannot confirm an appointment or imply staff received a message.

## 8 API contracts and interface flows

The existing /api/listings, publication, public question and inquiry routes remain compatible during migration. New routes are planned contracts. Every protected route derives the business and permission context before reading or writing. Browser controls mirror backend checks.

| Route group | Intended contract | Enforcement |
| --- | --- | --- |
| /api/platform/businesses | Create/update/deactivate business and enabled modules | Platform administrator, audit, expected revision |
| /api/businesses/{business}/members | Invite/revoke business users and departments | Business administrator, no platform-role assignment |
| /api/businesses/{business}/configuration | Draft/validate/approve rules, services and questions | Department draft rights, administrator activation |
| /api/businesses/{business}/knowledge | Draft and publish approved knowledge | Exact revision and effective scope |
| /api/public/businesses/{slug}/questions | Answer approved business/service questions | Resolve business, published records, usage/request limits |
| /api/public/businesses/{slug}/requests | Submit a confirmed inquiry independent of a listing | Valid schema, voluntary contact, idempotency |
| /api/public/businesses/{slug}/appointments | View availability and confirm a booking | Resource locks, confirmed intake, idempotency |
| /api/appointments/{id}/manage | Reschedule/cancel private booking | Verified customer management token or authorized staff |
| /api/dealership/* | Stock, comparisons, trade-ins, test drives, sale/lease/title/service records | Business and department, expected revision, staff approval |
| /api/channel-tests and /api/provider-events | Activation tests and signed provider callbacks | Admin starts tests, verified provider events complete evidence |
| /api/diagnostics and /api/audit | Role-filtered task and action evidence | Business administrator or audited platform support |

Platform dashboard navigation is Businesses, Modules and Platform status. Business navigation is Overview, Knowledge, Services and rules, Appointments, Inquiries, Team and System status, with domain modules enabled as needed. Customer pages show the selected business, public services or inventory, questions and a visible human-contact option. Knowledge/rule editors show Draft, Approved and Active revision state. Forms show required fields and field-specific errors.

## 9 Evidence security and standards

An AI task is created before the provider attempt with request_id, business_id, optional source record/revision, model, kind and Started state. On completion store status, safe error category, elapsed time, provider response ID and usage when returned. Record application-output validation separately from provider transport success. An unavailable usage value stays null. The current demo logs task outcomes after the request and does not yet provide this complete provenance model.

Instructor evidence comes from the application's AI task records, the linked source revision, redacted server request ID and provider dashboard. Customer inquiries are a separate table and cannot prove that an AI call occurred. Password verification belongs to managed Auth. A password hash is inspected only by authorized administration when needed, with secrets hidden during presentation.

Implement the requirements' tenant/role test matrix, privileged MFA, safe rendering, restrictive object access, request/body limits, usage budgets and provider signature checks. Never execute instructions embedded in customer text or knowledge items as authorization. Use HTTPS for hosted traffic and validate database TLS. Verify the selected provider's encryption and backup properties before claiming those controls.

Use WCAG 2.2 AA as the accessibility target for labels, keyboard focus and error messages. Use applicable OWASP ASVS and LLM application guidance for authentication, authorization, injection and output handling. Use NIST CSF 2.0 to organize recovery and incident tasks. Record implemented controls and exclusions rather than claiming certification.

## 10 Implementation order and verification

| Stage | Work and dependency | Required evidence |
| --- | --- | --- |
| Fall continuation | Preserve demo records and published snapshots. Add shared business/service configuration, business-independent inquiries and a second domain fixture. | Dealership and salon use different approved questions/rules. Cross-business reads and writes fail. Existing listing flow still passes. |
| Final platform foundation | Platform administrator, business CRUD, business administrator staff management, department permissions and MFA | AT-01, AT-02, AT-03 and role/isolation tests |
| Final operations | Resource scheduler, appointment lifecycle, outbox, channel activation and voice adapter | AT-07, AT-09, AT-10 plus outage and capacity tests |
| Final domains | Dealership operational records, salon and studio workflows, policy answers and event module | AT-13 through AT-24 with domain fixtures |
| Final delivery | Hosted deployment, sandbox subscription lifecycle, privacy jobs, recovery and user trials | AT-12 and all NFR evidence with recorded environments |

The repository review at commit d73c2c4896967e3d913116567fa9b7504d350c31 confirms source for the dealership draft/publication/inquiry workflow and AI task logs. It also confirms that public business setup, platform administration, MFA enforcement, generic services, appointments, voice and automatic delivery are still implementation work. Historical test results in the handoff remain historical evidence. This revision introduces no new live-provider test result.

## Technical references

[1] Supabase password security. https://supabase.com/docs/guides/auth/password-security

[2] Supabase Auth MFA. https://supabase.com/docs/guides/auth/auth-mfa

[3] Twilio Voice webhooks. https://www.twilio.com/docs/usage/webhooks/voice-webhooks

[4] xAI authenticated model catalogue. https://docs.x.ai/developers/rest-api-reference/inference/models

