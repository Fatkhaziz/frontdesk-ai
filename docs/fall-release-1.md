# Fall Release 1 technical reference

Updated November 24, 2026. Source links below target the [existing review branch](https://github.com/Fatkhaziz/frontdesk-ai/tree/docs/professor-feedback-2026-11-19). They describe implemented behavior, not the complete spring requirements.

## Database contract

Definitions: [`001_demo.sql`](../migrations/001_demo.sql), [`002_listing_ai_tasks.sql`](../migrations/002_listing_ai_tasks.sql), [`003_business_reception.sql`](../migrations/003_business_reception.sql), [`004_ai_interaction_evidence.sql`](../migrations/004_ai_interaction_evidence.sql), and [`migrate()`](../backend/migrate.py). JSON snapshots are PostgreSQL `TEXT`, not native JSONB. IDs/subjects and UTC ISO timestamps are text; revisions, cents, counts and durations are integers; flags are Boolean.

| Schema/table | Important columns and relationships |
| --- | --- |
| `public.businesses` | `id` PK, `name`. Parent business identity. Domain lives in the profile, not this table. |
| `public.memberships` | `subject` PK, `business_id` FK → businesses, `role` owner/staff, `active`. `subject` is the Supabase user ID by application convention; **no FK to `auth.users`**. One membership per subject, not multiple business memberships. |
| `public.listings` | `id` PK; `business_id` FK → businesses; unique `(id,business_id)`; `revision`, `facts`, `description` private state; `approved_revision`, `approved_by`; `published`, `published_revision` active snapshot. Facts: make/model/year, USD cents, mileage, availability. Approver is a subject string, without an Auth FK. |
| `public.inquiries` | Vehicle inquiry: `id` PK, `business_id`, `listing_id` composite FK → listings; unique `(business_id,request_key)`; `contact`, `message`, `status` open/pending/resolved, `created_at`. No AI task/request FK. |
| `public.ai_tasks` | `id` PK, `business_id` FK → businesses; `kind`, configured `model`, provider `status`, `duration_ms`, legacy `result`, `usage`, `created_at`. New writes leave raw `result` null; historical rows remain unchanged. Migration 004 adds a unique index on `(id,business_id)`. |
| `public.ai_budget` | Singleton `id=1`, `calls` attempt counter. Application reads `AI_CALL_LIMIT`, defaulting to **10**; existing private configuration remains **10**. This is not a token/dollar balance or per-business allowance. |
| `public.listing_ai_tasks` | `task_id` PK/FK → ai_tasks, delete cascade; `(listing_id,business_id)` FK → listings, delete cascade. Its business is checked by application callers; the task FK itself does not enforce same-business ownership. |
| `public.audit_events` | `id` PK, `business_id` FK → businesses, `actor`, `listing_id`, `revision`, `action`, `created_at`. Publication audit; no listing/actor FK, HTTP request ID or AI-task link. |
| `public.business_profiles` | `business_id` PK/FK → businesses; private `revision`, `profile`; active `published`, `published_revision`, `approved_by`. Check requires snapshot/revision together and published revision ≤ private revision. Profile: name, domain (`dealership`, `salon`, `photography_studio`), about, public contact, IANA time zone, seven days of hours, services and FAQs. Each service has ID/name/description, minutes, optional USD cents and ordered intake question IDs/labels/required flags. |
| `public.business_inquiries` | `id` PK; `business_id` FK → business_profiles; unique `(business_id,request_key)`; `profile_revision`, optional `service_id`, saved `service_name`, `message`, `contact`, JSON-text `answers` and `answer_labels`, `status`, `created_at`. Service/revision are snapshot values, **not FKs to historical revisions**. No HTTP/AI-task link. |
| `public.business_profile_events` | `id` PK; `business_id` FK → business_profiles; `actor`, `revision`, publish/unpublish `action`, `created_at`; unique `(business_id,revision,action)` makes repeats idempotent. No request ID, actor FK or retained full profile snapshot. |
| `public.ai_interaction_evidence` | `task_id` PK/FK → ai_tasks, delete cascade; `(task_id,business_id)` composite FK → ai_tasks, delete cascade; `business_id` FK → businesses; `request_id`, `published_revision`; JSON-text `approved_sources`, `selected_sources`; nullable `provider_response_id`, `token_usage`, `latency_ms`; separate `provider_outcome`, `application_outcome`. Index `(request_id,business_id)`. Published revision is evidence, not a FK to an immutable revision table. |
| `public.schema_migrations` | `name` PK, `sha256`; created by migration runner. No timestamp. Tracks immutable migration contents. |
| `auth.users` (Supabase managed) | Auth service owns `id`, email/confirmation, password hash and other identity state. Application reads only the authenticated `/auth/v1/user` response (`id`, `email_confirmed_at`), not the SQL table or password hash. Managed Auth also owns its session/token tables; this application does not define or query those tables. |

The implementation uses `public` and Supabase-managed `auth`. Storage, realtime, extensions and other provider/system schemas are not application persistence contracts. A complete live project schema inventory is **not yet verified** because DNS blocks database access. There are no application storage buckets, photo uploads, scheduling, payment or voice tables.

Migrations revoke all application-table privileges from `anon` and `authenticated`. The browser uses FastAPI rather than PostgREST for application records. These migrations do **not** enable RLS or define a restricted backend database role: tenant predicates and dependencies are enforced by the backend. Database credentials remain server-only.

## Feature / function / HTTP map

All routes are implemented in [backend/main.py](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/backend/main.py) unless another file is linked. Public means no sign-in; private derives business from verified membership, never from a submitted business ID.

| Feature and source | Function(s) | Endpoint / access |
| --- | --- | --- |
| Runtime configuration | `config`, `config.supabase_config`, `question_mode`, `ai_enabled` | `GET /api/config`, public; only Auth URL/publishable key, question mode, drafting flag and rehearsal marker |
| Health and rendered app | `health`, `frontend`, static assets | `GET /health`, `/`, `/listing/{lid}`, `/business/{lid}`, `/assets/*`; public; `/docs` and `/openapi.json` are FastAPI-generated |
| Sign-in UI, [main.tsx](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/frontend/src/main.tsx) | `App`, `api`, `load`, form handler | Supabase `POST /auth/v1/token?grant_type=password`, then protected FastAPI routes |
| Workspace, [business.py](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/backend/business.py) | `create_router.workspace` | `GET /api/workspace`, active owner/staff |
| Shared settings; [BusinessSettings.tsx](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/frontend/src/BusinessSettings.tsx), [business.ts](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/frontend/src/business.ts) | `Profile` validators, `save_profile`, `publish_profile`, `unpublish_profile`; UI `BusinessSettings`, `exampleProfile` | `PUT /api/business/profile`; `POST /api/business/profile/publish`, `/unpublish`; owner only |
| Published business page and Q&A | `business_page`, `public_profile`, `answer`; [business_qa.py](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/backend/business_qa.py) `answer_question`, `sources_for`, `validate_result`; UI [PublicBusiness.tsx](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/frontend/src/PublicBusiness.tsx) `ask` | `GET /api/public/businesses/{business_id}`; `POST .../questions`; public, published snapshot required |
| Explicit service/general inquiry | `submit_inquiry`, `update_inquiry`, `format_inquiry`; `PublicBusiness.submit` | `POST /api/public/businesses/{business_id}/inquiries`, public; `PATCH /api/business/inquiries/{inquiry_id}`, active owner/staff |
| Combined staff inbox | `inbox`, `inquiry_status`; `App` inbox | `GET /api/inquiries`, owner/staff; `PATCH /api/inquiries/{iid}` for vehicle inquiries |
| Vehicle draft CRUD | `listings`, `create`, `get_listing`, `edit`, `update_draft`, `record`, `serialize`; [ListingEditor.tsx](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/frontend/src/ListingEditor.tsx) | `GET/POST /api/listings`, `GET/PATCH /api/listings/{lid}`; owner/staff |
| Vehicle AI draft | `draft`; [ai.py](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/backend/ai.py) `call_ai` | `POST /api/listings/{lid}/draft`, owner/staff, drafting enabled and matching private revision |
| Vehicle publication/deletion | `publish`, `unpublish`, `delete_listing` | `POST /api/listings/{lid}/publish`, `/unpublish`; `DELETE /api/listings/{lid}`; owner only. Deletion is an existing explicit feature, not invoked against live records during this work. |
| Vehicle public questions/inquiry | `public`, `question`, `inquiry`; [demo.py](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/backend/demo.py) `fields_for_question`; [PublicListing.tsx](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/frontend/src/PublicListing.tsx) | `GET /api/public/{lid}`, `POST .../questions`, `POST .../inquiries`, public |
| Status and AI evidence | `diagnostics`, `ai_evidence`; [SystemStatus.tsx](https://github.com/Fatkhaziz/frontdesk-ai/blob/docs/professor-feedback-2026-11-19/frontend/src/SystemStatus.tsx) `refresh` | `GET /api/diagnostics`, `/api/ai/evidence`; owner only, own business, latest 50 evidence rows |
| HTTP tracing / errors | `trace`, `validation_error`, [errors.py](../backend/errors.py) `error_category` | Middleware / validation handler on every route; no standalone endpoint |
| Connectivity/migration verification | [verify_integration.py](../backend/verify_integration.py) `check_auth`, `inspect_database`, `schema_contract`, `snapshot_rows`; [migrate.py](../backend/migrate.py) `migrate`; [check_connection.py](../backend/check_connection.py) `check` | CLI only, no HTTP administrative migration endpoint |
| Disposable PostgreSQL integration | [check_postgres.py](../scripts/check_postgres.py) `main` | CLI only; explicit ephemeral marker and loopback DB required; upgrades legacy fixtures, verifies three business paths with mocked Auth/Grok and no live Supabase data |
| Safe rehearsal | [rehearse.py](../scripts/rehearse.py) `main`, `rehearsal_identity`, `rehearsal_login`, `sample_profile` | Process-only `POST /rehearsal-auth/auth/v1/token`; loopback port 8002; synthetic accounts/SQLite, paid AI disabled |
| Optional live check | [verify_live_qa.py](../scripts/verify_live_qa.py) `main`, `estimate_cost` | CLI; default database-only preflight; explicit paid flag + interactive confirmation invokes one public question endpoint via in-process TestClient |

The vehicle API is retained for compatibility. Hiding the Listings tab for non-dealership profiles is a UI choice; the backend does not enforce a domain-specific ban on those routes.

## Authentication and authorization path

1. `App` loads `/api/config`. `supabase_config()` selects canonical settings over `VITE_` aliases and rejects service-role JWTs and `sb_secret_` keys for browser configuration.
2. The Supabase client submits the entered password directly to that configured project's Auth API. FastAPI never receives the password. Browser Auth uses `persistSession:false`, `autoRefreshToken:false`, `detectSessionInUrl:false`.
3. The returned access token stays in React memory. Refresh requires sign-in. `sessionStorage` holds only the selected listing ID. Sign-out clears local token/workspace state; it does not revoke all server sessions.
4. `api()` sends `Authorization: Bearer ...` to FastAPI. `identity(request)` requires that prefix, calls Supabase `GET /auth/v1/user` with the token plus configured publishable key, requires HTTP 200 and `email_confirmed_at`, then reads `memberships WHERE subject=user.id AND active=TRUE`.
5. Each protected call repeats validation; token expiry/project validation belongs to Supabase. Missing/invalid tokens → 401, unconfirmed email/inactive or absent membership → 403. Upstream connection errors become safe 503 responses via `trace`.
6. `owner()` additionally requires `role='owner'`. Business-profile writes/publication, listing publication/deletion, diagnostics and evidence use it. Staff can read settings, edit vehicle drafts and update only their business's inquiries.
7. Private SQL scopes by trusted membership business ID. Public business routes resolve only the requested business's published row; public listing routes resolve its own business from the listing. Composite relationships protect supported child links. Guessed foreign IDs return 404 where records are scoped.
8. There is no platform administrator, department authorization, self-service provisioning, MFA enforcement, application idle timeout, sign-in throttling or customer-contact verification in Release 1. Auth configuration settings alone do not prove a real user login or correct membership provisioning.

## Published revisions and inquiries

`save_profile` uses expected revision 0 for initial insert and compare-and-update thereafter. Saving private settings increments the draft revision and leaves the previous published JSON intact. `publish_profile` requires owner, literal approval `true` and the current saved revision; it copies profile → published and records a publication event in the same transaction. Stale saves/publications return 409. `unpublish_profile` clears the active snapshot/revision. A published pointer, rather than a separate approval flag, identifies the approved version.

`submit_inquiry` locks the published profile row on PostgreSQL (`FOR UPDATE`; SQLite tests omit it). It checks request-key replay, exact published revision, business-owned service ID, allowed answer IDs, answer lengths and required questions. It saves the service name and question labels as submitted-form evidence. A matching replay returns the original ID; changed payload with the same key returns 409. The UI says saved only after the server commits. Status updates are scoped by business. No email, notification, appointment reservation or inferred lead is created.

## Business AI request and validation path

1. `trace` creates an application UUID, sets `request.state.request_id`, returns `X-Request-ID` and logs method, route template, status and HTTP duration. Client-provided IDs are not trusted.
2. `business.answer` reads `public_profile`, including its published revision. `sources_for` derives source statements only from this snapshot: name/about/public contact/time zone, daily hours, service descriptions/durations/prices and FAQ answers. Private profile JSON, inquiry tables, contacts/intake answers and conversation history are not queried for AI context.
3. Each source has `id={business}:r{revision}:{path}:{digest-prefix}`, `business_id`, `revision`, `path`, `label`, full `text`, full `sha256` and public-page URL. Labels include FAQ questions; amounts are deterministically rendered from approved integer cents. The evidence snapshot retains these statements even after later publication.
4. `QUESTION_MODE=demo` performs normalized exact FAQ-question matching. It returns `exact_match` plus the source, or `fallback` with `handoff:true`. It makes no provider call and creates no AI task. Rehearsal forcibly uses demo mode and empties provider credentials.
5. In AI mode, `safe_question` rejects recognized email/phone/credential patterns before inference. These patterns are not a complete privacy classifier. Missing credentials, exhausted budget or >32,000 bytes of prompt/source input return a safe error without inference.
6. A transaction conditionally increments singleton `ai_budget.calls` below the configured cap and inserts `ai_tasks(status='started')` plus `ai_interaction_evidence(provider_outcome='started',application_outcome='pending')` **before** network access. No question text or credentials are persisted.
7. An HTTPX client sends one `POST https://api.x.ai/v1/chat/completions`: configured model; system instruction; current question and published sources as JSON; temperature 0; JSON-object response format; output cap 1,600 tokens; 30-second HTTPX timeout settings; no tools/retries. This is not a strict whole-request wall-clock deadline. Source/question text never authorizes database writes.
8. HTTP success and output validity are separate. The parser requires a normal `stop` completion and JSON containing exactly `business_id`, integer `revision`, Boolean `handoff`, and a list of up to eight `claims`. Handoff must be true exactly when that list is empty.
9. `validate_result` requires every claim to contain exactly `source_id,text`, rejects duplicate/unapproved/foreign references, checks revision and exact entire source text/digest. There is no provider-generated answer prose. The application joins accepted source text to form the answer.
10. `read_current()` re-reads the entire active published snapshot. Changed publication, revision or unpublication rejects the result as `stale_source`; a concurrent private draft edit alone does not invalidate the approved snapshot. A publication immediately after this final check remains a normal read/return race; no long database lock spans inference.
11. The final transaction updates task/provider outcome, available identifier/token usage, elapsed task latency, application outcome and accepted source references. Invalid raw responses/error bodies are not saved. Provider IDs are restricted and usage allows only nonnegative integer prompt/completion/total counts; missing usage stays null.
12. The API returns `answer`, `handoff`, `revision`, `mode`, `sources`, `request_id`, nullable `task_id` and reason. `PublicBusiness.ask` clears prior answer/evidence before requesting, renders text safely through React and shows **Live AI**, **Exact FAQ matching**, **Fallback** or **Error**. A handoff only pre-fills the separate inquiry message; no submission occurs.

Prompts do not guarantee correctness. Exact-source validation rejects unsupported factual wording, but cannot prove the truth of the business's approved text, semantic relevance, completeness of a mixed question or provider interpretation accuracy. Real Grok semantic quality remains unverified.

## Legacy vehicle AI path

`draft` sends structured vehicle facts through `ai.call_ai`, converts cents to explicitly labeled USD, checks the returned description shape, then performs an expected-revision draft update. Existing description prose is not sent. Owner review is still required before publication; draft wording has no automatic factual-proof validator.

`question` uses `fields_for_question` as a narrow price/mileage gate. AI mode classifies only that supported input; the server rejects a mismatched field set and renders actual values from a fresh published snapshot. It is not the natural-language business Q&A engine. `call_ai` reserves the shared attempt count, performs a model-catalog GET, and logs a task only in `finally`, after the provider attempt. It stores allowed usage/provider response ID in `ai_tasks.usage` and optionally `listing_ai_tasks`. This path still lacks HTTP request correlation, source revision and separate application-validation outcome. No historical metadata is invented or backfilled.

## Record locations and missing links

| Evidence | Recorded location / limits |
| --- | --- |
| Every HTTP request | `frontdesk` process console via `trace`: generated ID, method, route template, status, duration; ID response header. Safe exception type/category/SQLSTATE/origin only. **No durable HTTP-request table**. |
| New business AI attempts | `ai_tasks.id` + `ai_interaction_evidence.task_id/request_id/business_id`. Budget reservations that fail before network are not inference tasks. `ai_budget.calls` is an aggregate, not an event ledger. |
| Provider identifier / usage | Business Q&A: `ai_interaction_evidence.provider_response_id/token_usage` and usage also in `ai_tasks.usage`; legacy: nested in `ai_tasks.usage`. Unknown fields stay null; configured model is stored, not a verified resolved provider-model alias. |
| Approved facts / revision | Current profile in `business_profiles.published/published_revision`; attempted/selected source snapshots and revision in evidence. Historical full profile revisions are **not** retained as their own rows. |
| Validation / failures | Evidence `provider_outcome`: started/succeeded/failed; `application_outcome`: pending/accepted/handoff/provider_error/invalid_output/stale_source. Successful HTTP transport may accompany invalid output. Detailed rejection subcategories and raw responses are not stored. |
| Publication audit | `business_profile_events` for profiles; `audit_events` for vehicles. Neither has an HTTP request ID. A repeated same-revision action deduplicates rather than recording every attempt. |
| Service inquiries | `business_inquiries`, separate from vehicle `inquiries`; joined only in the scoped inbox serializer. Neither references an AI task, provider response or HTTP ID. A handoff is not evidence that a customer submitted a request. |
| Exact matching / pre-provider fallback | HTTP console entry and response mode/sources only. **No durable interaction row**, question transcript or inferred inquiry. |

Crash/DB failure after network completion can leave a started/pending row; there is no recovery worker. Final evidence-write failure returns a safe 503 rather than an accepted answer. There is no retention/purge implementation, per-client rate limiting, global dollar ledger, immutable source FK, audit on inquiry-status changes, or request-to-inquiry foreign key. Source hashes prove content identity, not factual truth. Source URLs identify the public page/evidence section, not an immutable historical document.

## Environment and migration verification

`config.database_options()` keeps an existing configured certificate path. If that path is missing, it accepts only the same basename inside this checkout's `.certs`, refuses a resolved path outside that directory and parses the PEM through `ssl.create_default_context`. The file, `.env` and `sslmode=verify-full` are unchanged. `db.connect` and the local preflight use these options. The stale path blocker is resolved. Offline checks also found matching DB/Auth project references and a non-expired local CA; they do not prove a successful TLS handshake. Network DNS still fails for Supabase, npm and GitHub in the local runtime.

`python -m backend.verify_integration --apply-pending` checks Auth settings and rejection of an invalid bearer, then independently reviews database migration checksums and snapshots existing application rows privately. `migrate()` takes a PostgreSQL advisory transaction lock, refuses changed checksums/untracked initial schema, applies pending SQL atomically and records hashes. Post-checks compare every contract table/column, inspect FK definitions, require no anon/authenticated application grants and verify pre-existing row digests/counts and budget unchanged. No row data, digest, connection string or credentials are printed. `--database-only` is explicitly for isolated PostgreSQL CI, not evidence of Supabase Auth.

Real probes attempted with existing private configuration: CA resolves and verify-full remains; cap remains 10; Auth `ConnectError`, PostgreSQL `OperationalError` due unavailable DNS. The migration runner was **not reached**, no live schema/data changes occurred, and live tables/columns/migration state/used attempts remain unverified. The optional Supabase integration was discovered but remains uninstalled/unconnected; installing and connecting it is another possible access path. No verified owner password or usable access token was supplied; even a successful settings probe would not prove real sign-in/role behavior.

## Verification record

- Local backend: **43 tests passed**, synthetic SQLite and injected/mocked Auth/Grok, including three domains, tenant isolation, revision conflicts, explicit inquiry retries, source forgery, stale results, injection, failure paths, CA relocation and live-cost gate.
- Local frontend: strict TypeScript/Vite production build and three domain tests passed after restoring cached build dependencies with the repository lockfile unchanged. Full local interaction tests remain blocked by the uncached `xmlchars` package and registry DNS; complete interaction tests run in CI instead.
- Local rendered browser: unavailable browser access host and denied loopback bind; no successful local rendered run claimed.
- Remote verification: [workflow source](../.github/workflows/fall-release-1.yml) uses only the public repository's standard Ubuntu runner, no secrets or live provider configuration, pinned actions, mock/SQLite tests, complete frontend tests, production build, disposable PostgreSQL 16 migrations and actual headless Chromium workflows. The disposable PostgreSQL check validates all contract tables/columns, 13 foreign keys, denied browser grants, preserved synthetic legacy rows and three business inquiry/evidence paths. The [successful verification run](https://github.com/Fatkhaziz/frontdesk-ai/actions/runs/45359723183) tested implementation commit `e41a3941f6a38a639ac4ab3a0600fc97068b8c31`: **43 backend tests, 6 frontend tests, strict production build, PostgreSQL migration/integration smoke checks, and both rendered Chromium workflows passed**. Subsequent changes to this reference and README are documentation only; the workflow deliberately skips documentation-only pushes. This is application integration evidence, not live Supabase/Grok verification.
- `.env`, certificate contents, existing records and configured cap are preserved; the private-file hash comparison is local and its values are not published. No paid calls, purchases, limit increases, database resets or live record deletions were performed.

## User-initiated Grok check still required

After live connectivity/migrations and publication of a real business profile are verified, privately load the existing `.env` and run:

```sh
.venv/bin/python -m scripts.verify_live_qa --business ACTUAL_BUSINESS_ID
```

Default behavior is read-only database preflight, without provider access. The one paid action is:

```sh
.venv/bin/python -m scripts.verify_live_qa \
  --business ACTUAL_BUSINESS_ID \
  --remaining-usd CURRENT_PREPAID_BALANCE \
  --authorized-remaining-usd UNUSED_ORIGINAL_BUDGET \
  --billing-checked --execute-one-paid-request
```

For configured `grok-4.20-0309-non-reasoning`, the [official pricing](https://docs.x.ai/developers/pricing) checked November 24 is $1.25/M input and $2.50/M output for short global requests. Recheck the current price and correct team's balance/billing settings privately at [xAI Console](https://console.x.ai/). Current balance and unused portion of the original $5 are unknown; the original purchase is not today's balance.

The command requires both balances to cover the conservative full-input estimate **$0.04912** (32,000 bytes + 4,096 framing-token allowance and 1,600 output tokens), enforces a $0.05 estimate gate, verifies migration hashes and available attempt budget, performs a free model-catalog lookup, then requires typing `SEND ONE`. It asks one cancellation-policy paraphrase through the application. No retry, credits purchase, model substitution, cap change or inquiry submission occurs. This estimate is not a provider billing guarantee; a timeout may still incur charges. Actual Grok response quality, returned provider ID/usage, and billed cost remain unverified until this user action.
