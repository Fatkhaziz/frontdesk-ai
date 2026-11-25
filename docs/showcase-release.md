# Fall Release 1 dealership showcase

> **Live follow-up after PR #3:** the user started the existing Mac server, and the real Safari owner session, connected service status, six published vehicles, two-/three-vehicle comparisons ($4,600/$6,000 differences), private knowledge saving/public exclusion and one consented synthetic shopping inquiry were observed. After checking 9/10 attempts, the correct configured model, $5.00 rounded credit, disabled auto top-up and less than $0.01 prior spend since the original purchase, exactly one real Find my fit request completed. It extracted a $25,000 vehicle-price budget, five minimum seats and fuel-economy priority; compared the fictional Compact Hatch/City Hybrid; returned six published price/seats/MPG references and a relevant follow-up; and identified missing ownership/condition/tax information. **The final attempt has been used: do not send more AI requests or raise/reset the cap.** Owner AI suggestions, another conversation turn, the separate AI comparison button and fair-price questions have not been live verified. The earlier setup-stage server blockers and 9/10 remaining-attempt instructions below are historical. After loading the frontend review fix, the memory-only owner session required private sign-in again; owner publication, inbox status, the refreshed counter and actual durable provider/model/token/latency evidence inspection are pending that step. The existing customer tab retains the real response. Frontend fixes preserve selected IDs in Find my fit, separate inquiry activity from AI Thinking, and add explicit answer-review actions. [PR #4 CI](https://github.com/Fatkhaziz/frontdesk-ai/actions/runs/45531318371) passed 62 backend tests, 11 frontend tests, production build, disposable PostgreSQL and all rendered mocked-Auth/Grok workflows. These automated results do not replace the remaining live checks.

This is the current fall scope following the November 24 discussion with Dr. Matovu. Demonstrate concrete AI use in one dealership: owner knowledge preparation, customer preference discovery, and explained vehicle comparison. The platform remains for small businesses. Additional business-domain completion is final-system work; existing salon/studio code is retained, not removed.

## Acceptance scope

| Capability | Acceptance evidence |
| --- | --- |
| Owner knowledge preparation | Real AI suggests likely customer questions and information gaps; it does not invent answers. Owner supplies answers or staff-only boundaries, saves privately, and explicitly publishes a saved revision. |
| Vehicle facts | Optional body style, fuel type, drivetrain, transmission, seats, combined MPG, cargo space and features. Unknown facts remain unknown. Existing six-field listings still work. |
| Customer discovery | A free-text need updates editable preferences, asks one useful follow-up, preserves earlier requirements and supports changed preferences within the page. No contact details are required for browsing/chat. |
| Comparison | Select two or three published vehicles from one business. View facts, missing values, hard-constraint checks and exact backend price differences without an AI request. |
| AI explanation | Real Grok interprets intent and explains trade-offs from published sources. Cite source references and show missing evidence. Never claim an unsupported market valuation, warranty, accident history or total cost. |
| Staff follow-up | Only an explicit, consented submission saves contact, question, preferences and selected published snapshots. Staff can change Open/Pending/Resolved status. No notification delivery or booking is claimed. |
| Technical evidence | A durable task precedes each new showcase API request. Match task ID to request ID, provider ID, model, tokens, latency, source snapshot and separate provider/application outcomes. |
| Regression | Existing owner/staff permissions, listing drafts/publication/deletion and business separation continue to work. Old migrations are unchanged; 005 is additive. |

## Start on the configured Mac

1. In GitHub Desktop, fetch and pull `main` (PR #2 is merged). Use the configured project checkout with its existing private `.env` and certificate, not a new download without settings.
2. In Terminal, change into that repository and run:

```sh
bash scripts/setup-showcase.sh --with-examples
```

The script builds the frontend, checks real Auth configuration, applies pending checksum-tracked migrations, checks existing-row preservation, adds four clearly fictional vehicles to the sole existing owner business, and starts the server at `http://127.0.0.1:8000/`. Existing vehicles, users, policies, credentials and the attempt counter are not reset. Re-running the seed does not duplicate or overwrite its example vehicles. If multiple owner businesses exist, seed separately with `python -m scripts.seed_showcase --confirm-synthetic --business-id ACTUAL_ID` instead of guessing.

The launcher enables AI mode for its process when existing xAI settings are present. It does not change `.env`, raise `AI_CALL_LIMIT`, buy credits, or make an inference request. If port 8000 is occupied, stop the earlier app process with Ctrl+C in its terminal first. Keep the app terminal running during the showcase. Running the website does not require an active Codex session; paid API usage occurs on AI actions.

After setup is complete, later restarts do not need dependency installation, migration or example seeding:

```sh
bash scripts/run-local.sh
```

Keep that Terminal open. The application is local; closing Terminal or pressing Ctrl+C stops it. The configured Python 3.9 environment is supported by this maintenance fix; Python 3.12 remains the CI/production recommendation. The app must actually bind port 8000 before its URL can be called running.

3. Sign in using the existing confirmed Supabase owner credentials. Open **Listings → Open customer inventory**. The public path is `/shop/{business_id}`. Original individual listing pages also link to the inventory/comparison page.
4. Review **Owner knowledge** and **System status** before presenting. An AI-disabled state or exhausted attempt cap is not a successful live verification.

### Budget and live verification

The existing global attempt limit is preserved. Last observed before this release: 9 of 10 used; current value must be checked in System status. Account credit balance is separate. Do not assume a new release creates more attempts or more credits.

Use `python -m scripts.verify_showcase_live --business ACTUAL_ID` for a read-only preflight. The explicit execute flag performs one real customer-shopping request only after both remaining budgets and current pricing are supplied and checked. It does not reset the counter or silently retry. A model mismatch stops execution. Owner question suggestions still require their own real browser check.

The observed xAI billing page showed a rounded **$5.00** balance, one original $5 purchase, and **auto top-up disabled**. No payment or billing setting was changed. The live database was independently checked at **9/10 attempts used** after migration/seeding; only one attempt remains. A rounded dashboard balance is not a precise cumulative-cost ledger, and the remaining balance must still cover the conservative request ceiling. With only one attempt, owner suggestions plus shopping, follow-up, comparison explanation and fair-price responses cannot all be verified live. Prioritize the new shopping endpoint if the application can run, and explicitly mark every unperformed AI operation unverified. Never spend the attempt through a provider playground as a substitute for the application.

Current published standard global prices for `grok-4.20-0309-non-reasoning` are $1.25 per million input tokens and $2.50 per million output tokens, checked November 24 at https://docs.x.ai/developers/pricing. Each showcase request has a 48,000-byte payload bound and 1,800-token output cap. The current conservative CLI ceiling, including system instructions and framing allowance, is **$0.07294625**; actual tokenization/billing is authoritative. Pricing, balance and total authorized spending must be checked before real verification. An attempt cap is not dollar accounting. Retain the original total $5 spending authorization.

## Presenter sequence

Open the owner dashboard and the customer inventory in two browser tabs. Prepare real AI checks before class rather than discovering configuration issues while presenting.

1. **Owner knowledge.** If a separate paid attempt is available and its budget is verified, click **Suggest customer questions with AI** once. With the current single remaining attempt reserved for shopping, do not click it; demonstrate **+ Add a question** and state that AI question generation is unverified live. Point out a missing-information question. Supply a true approved answer or mark **Staff must answer**. Save privately, review the saved revision, tick the approval checkbox and publish. Do not publish fictional warranty or history claims.
2. **Inventory.** Show the four vehicles labeled fictional examples. Their specifications are illustrative; this is not real inventory or an actual dealership offer.
3. **Find my fit.** Only after budget/attempt checks and actual application startup, enter: "My vehicle-price budget is $25,000. I need 5 seats for commuting and I prefer lower fuel use." Send once. Point to the updated preferences and the follow-up. Model wording will vary; assess whether it respects the facts and budget.
4. **Refine.** If another paid attempt is available, respond to its actual follow-up. With the present 9/10 cap, this second live turn is blocked; preferences can still be edited manually, which is not a verified AI turn. To show an explicit change, say: "I can raise my vehicle-price budget to $30,000." Confirm the changed preference. A new send is another paid request.
5. **Compare.** Select two or three vehicles in Inventory. Click **Compare selected**. Show the specification table, missing MPG/cargo values and calculated price difference. These factual comparisons make no AI request. Only click **Explain this comparison with AI** if another funded attempt is available. The present single remaining attempt cannot also fund this after an initial chat; do not imply the calculated table is AI output.
6. **Question limits.** Ask "Is this a fair price?" if budget allows. A useful answer explains the asking price and known differences while identifying missing market and condition evidence. It must not invent a market valuation.
7. **Handoff.** Click **Ask staff to follow up**, review the summary, use a synthetic test contact such as `class-test@example.invalid`, tick consent and submit. Return to **Inquiries → Refresh inquiries**, expand the requirements/selected-vehicles details and change status to Pending.
8. **Evidence.** Open **System status → Refresh status → Latest showcase AI requests**. Point to the operation, time, provider response ID, request ID, task ID, tokens and application outcome. Expand published source evidence. Viewing logs does not spend AI credits.

### Short speaking script

"The owner first uses AI to identify likely customer questions and missing information, then approves the answers the receptionist may use. On the customer side, AI interprets a natural request into preferences and asks a relevant follow-up. Our backend checks which published vehicles meet those requirements and calculates the comparison. AI explains the trade-offs using the approved information. If evidence is missing, the customer can send a contextual inquiry to staff. This request record shows the actual provider response and our validation result."

## Exact technology and code locations

| Technology or code | Responsibility |
| --- | --- |
| React/TypeScript `PublicShop.tsx` | Inventory, editable preferences, multi-turn page state, comparison, sources and consented follow-up. No secret keys. |
| `KnowledgeSetup.tsx` | Suggested questions, owner answers/source notes, staff-only boundaries, private saving and explicit publication. |
| FastAPI `shopping.py` | Published inventory, knowledge revision checks, comparison arithmetic, hard constraints, inference validation and business-scoped inquiries. |
| [`backend/showcase_ai.py:20`](../backend/showcase_ai.py#L20) `provider_call()`; the POST is at lines 24–31 | Actual HTTPS POST to `https://api.x.ai/v1/chat/completions`, with model, system instructions and minimal structured context. |
| `showcase_ai.py` `run_ai()` | Reserve an attempt; persist task/evidence before the network; validate result; check current snapshots; save separate provider and application outcomes. |
| `main.py` `identity()` and `owner()` | Validate bearer through Supabase Auth and require active membership/owner role. Never trust a client business ID as proof of permission. |
| `db.py` | Parameterized PostgreSQL access, commit and rollback. |
| `migrate.py` and migration 005 | Apply additive schema changes under advisory lock with checksums. Never edit already-applied SQL. |
| Supabase | Hosted PostgreSQL and authentication. The local Mac serves the web app; Grok runs at xAI. No local model or training is used. |

## What is stored where

| Supabase table | Stored information |
| --- | --- |
| `auth.users` | Managed login identity. `encrypted_password` stores a salted bcrypt hash, not a readable password. |
| `public.businesses` | Business ID/name; parent of memberships, listings, knowledge, inquiry and evidence scopes. |
| `public.business_profiles` / `public.business_profile_events` | Existing private/published business configuration and publication audit; retained for the earlier receptionist path. |
| `public.audit_events` / `public.listing_ai_tasks` | Listing publication/deletion audit and earlier listing/task association. Audit actors are not foreign keys to Auth. |
| `public.memberships` | Auth subject, business, owner/staff role and active state. It is not a password table. |
| `public.listings` | Private vehicle facts/description, revisions, approval and published snapshot. Extended facts remain JSON text. |
| `public.dealer_knowledge` | Private question/answer cards and the separately published owner-reviewed snapshot. |
| `public.knowledge_events` | Knowledge publication/unpublication audit contract; current UI publishes reviewed snapshots. |
| `public.ai_tasks` | Operation, recorded model, provider status, time, duration and typed usage metadata. New completions record `usage.requested_model` and nullable `usage.provider_model`; the model column uses the reported provider model when available. Missing provider model stays unknown. |
| `public.assistant_runs` | New showcase task/request/business links, source snapshot (source IDs encode published listing/knowledge revisions), cited source IDs, provider response ID, tokens, latency and application outcome. The task FK links to the model metadata in `ai_tasks`; the evidence API joins them and System status shows Requested model and Provider model separately. |
| `public.ai_interaction_evidence` | Earlier business-profile Q&A evidence path; not the table for the new shopping assistant. |
| `public.shopping_inquiries` | Explicitly submitted contact/message, preference and vehicle snapshots, retry key and status. |
| `public.inquiries` / `public.business_inquiries` | Earlier vehicle/service request flows, retained. |
| `public.ai_budget` | Shared lifetime attempt count. Not a provider dollar balance. |
| `public.schema_migrations` | Applied migration filenames and SHA-256 checksums. |

### Schema and route details

The [baseline technical reference](fall-release-1.md#database-contract) describes migrations 001–004 and the full Supabase authentication path. Migration [005](../migrations/005_shopping_assistant.sql) adds these `public` contracts; snapshots and token metadata are JSON encoded in `TEXT`, and timestamps/IDs remain text:

| Table | Important columns and links |
| --- | --- |
| `dealer_knowledge` | `business_id` PK/FK → businesses; private `revision/cards`; separate `published/published_revision`; `approved_by` Auth subject by convention, without Auth FK. Published revision cannot exceed private revision. |
| `knowledge_events` | `id` PK; `business_id` FK → businesses; `actor`, `revision`, `action`, `created_at`. No HTTP/task/actor FK or separate historical full snapshot. |
| `assistant_runs` | `task_id` PK/FK → ai_tasks with cascade; composite `(task_id,business_id)` FK enforces tenant/task ownership; `business_id` FK → businesses. Records `request_id`, `operation`, `source_snapshot`, `source_ids`, `provider_response_id`, `token_usage`, `latency_ms`, `provider_outcome`, `application_outcome`. No durable HTTP-request FK. |
| `shopping_inquiries` | `id` PK; `business_id` FK → businesses; unique `(business_id,request_key)`; `contact`, `message`, JSON-text `context` (preferences/published selected vehicles), `status`, `created_at`. No AI-task/request FK or notification-delivery record. |

All following handlers are in [shopping.py](../backend/shopping.py). Public routes use only published business-scoped snapshots. Owner routes reuse `identity()` → Supabase `/auth/v1/user` → confirmed user → active membership → `owner()` role check; staff inquiry status uses the same identity/membership check without the owner requirement. No browser role directly queries these PostgreSQL tables.

| Feature/function | HTTP endpoint |
| --- | --- |
| `public_inventory`, `compare`, `assist` | `GET /api/shop/{business_id}`; `POST /api/shop/{business_id}/compare`; `POST /api/shop/{business_id}/assist` |
| `get_knowledge`, `save_knowledge`, `publish_knowledge`, `suggest` (owner) | `GET/PUT /api/dealer/knowledge`; `POST /api/dealer/knowledge/publish`; `POST /api/dealer/knowledge/suggest` |
| `submit_followup`, `update_followup` | Public `POST /api/shop/{business_id}/inquiries` (explicit consent required); member `PATCH /api/shopping/inquiries/{id}` |
| `evidence` (owner); combined inbox in `main.inbox` | `GET /api/assistant/evidence`; `GET /api/inquiries` |

`PublicShop` sends published inventory, customer message/history, preferences and selected IDs to `assist`. The server validates input and source ownership, atomically reserves one budget attempt and writes `ai_tasks` plus `assistant_runs` before `run_ai` calls xAI. It parses a normal stop/JSON completion; `validate_answer()` checks exact fields/types, allowed source IDs, recommendations/hard constraints, explicit preference changes, numerical evidence and selected unsupported guarantees. A fresh catalog comparison rejects stale publication results. It records transport/provider success separately from accepted/invalid/stale application results; errors remain visible. These bounded checks do not prove all prose claims or semantic correctness. Owner suggestions validate question-only structure and reject stale owner/catalog revisions; they do not supply approved answers. There is no automatic retry or inquiry creation.

HTTP logs contain request ID, route, status and duration in the app process console. The new AI table stores the matching request ID durably. Raw customer chat and raw provider output are not retained as evidence. Shopping inquiries and showcase evidence retain submitted/published snapshots when an individual listing is deleted; no automatic retention purge is implemented. Inputs/outputs still travel to xAI for inference; public business data is not private merely because its evidence is owner-only.

### Show the latest recorded API request

Run in Supabase SQL Editor:

```sql
SELECT t.created_at,t.kind,t.model,t.status,
       t.usage::jsonb->>'requested_model' AS requested_model,
       t.usage::jsonb->>'provider_model' AS provider_model,
       r.request_id,r.task_id,r.provider_response_id,
       r.provider_outcome,r.application_outcome,
       r.token_usage,r.latency_ms
FROM public.assistant_runs r
JOIN public.ai_tasks t ON t.id=r.task_id AND t.business_id=r.business_id
ORDER BY t.created_at DESC
LIMIT 5;
```

A provider success is not automatically an accepted answer. An empty result means no new showcase request has been recorded. Existing vehicle requests remain in `ai_tasks`; they are not backfilled into this table. Read the timestamp rather than implying an old response happened during class.

### Show password storage

Supabase **Authentication → Users** lists accounts. In SQL Editor, name `auth.users.encrypted_password` and show only whether a hash is present. Keep actual hashes and account contact details off the projector. Never show `.env`, bearer tokens, an xAI key or a database connection string on a projector.

```sql
SELECT id, email_confirmed_at IS NOT NULL AS email_confirmed,
       COALESCE(length(encrypted_password), 0) > 0 AS password_hash_present
FROM auth.users
WHERE id = 'ACTUAL_AUTH_USER_UUID';
```

Official explanation: https://supabase.com/docs/guides/auth/password-security . Password hashing is a Supabase capability already in use, not a new custom password-storage implementation.

## Verification and honest limits

Automated suites use injected Auth and mocked provider completions. They test state transitions, rejection paths, source identity and constraints; they do not establish real Grok answer quality or semantic correctness. Prompts, source citations and numeric checks reduce specific failure modes, not every hallucination. Display the AI explanation as advisory and review facts. Known hard constraints may yield no verified match; unknown fees block claiming a total-budget fit.

The merged implementation's previous CI passed 60 backend tests, 9 frontend tests and rendered Chromium workflows at https://github.com/Fatkhaziz/frontdesk-ai/actions/runs/45523930544 . Those were simulated Auth/Grok tests, not live service verification.

### Configured Mac verification and remaining blocks

- Latest `main` (`59ac213859808ab38ec8dc6d3aba27c1f9ac7862`) was fetched through the GitHub connector and its Git objects hash-verified after shell DNS failed. The old branch was preserved. No `AGENTS.md` was present in the ancestors or current repository tree.
- The existing Mac Python is 3.9.6. New showcase nullable model annotations failed import there. They now use equivalent `Optional` annotations; **62 local backend regressions pass** with isolated SQLite/mocked providers, and the **production TypeScript/Vite build passes**. Two new checks cover returned-model evidence versus requested aliases. Full local frontend tests remain blocked by unavailable cached test dependencies; the complete [maintenance CI suite](https://github.com/Fatkhaziz/frontdesk-ai/actions/runs/45528060342) passed: 62 backend tests on both Python 3.9 and 3.12, nine frontend interaction tests, the strict production build, disposable PostgreSQL checks and all three rendered Chromium workflows (mocked Auth/Grok).
- `scripts/setup-showcase.sh --with-examples` was inspected and invoked. Its pinned Python requirements were already installed; npm failed in the restricted command runner. Cached build dependencies were restored without changing the lockfile, and the build succeeded.
- An existing signed-in Supabase dashboard session matched the configured project. Through its SQL editor, migration 005 was applied under the same advisory lock, after verifying checksums for 001–004. A single transaction recorded 005's exact checksum and added the same four deterministic fictional examples as `seed_showcase.py`. Hash-set checks across all 12 pre-existing application tables required every old row to remain present and unchanged or the transaction would roll back. No actual policies or knowledge answers were invented/published.
- Live verification after commit: 005 checksum matched; four new table/column contracts were inspected; **19 foreign keys**, **zero anon/authenticated grants** on the new tables, **one confirmed active owner**, **four fictional published examples / six published vehicles total**, **zero showcase AI runs**, and **9/10 attempts used**. Existing users/memberships and records were preserved. No old request was backfilled into `assistant_runs`.
- The xAI billing dashboard was read without opening keys or making a purchase: rounded balance $5.00, original $5 purchase and auto top-up disabled. No paid inference was attempted, no counter reset and no cap increase occurred.
- **Not running / not live UI verified:** no existing server occupied port 8000. The managed command runner cannot resolve/connect to Supabase and cannot bind loopback (`PermissionError`). Desktop control of Terminal was explicitly rejected by the computer-use safety policy. The browser dashboard provided a legitimate route for SQL work, but does not start an OS web process. Thus this run could not leave the Mac website running or check the current authenticated application routes/rendered flows. The prior owner session/service checks from the earlier release are historical, not proof of this release's login. Do not ask for a password before the application can actually run.
- **Still unverified live:** owner AI question generation; current application password/token/member route path; customer chat/preferences/follow-up changes; AI comparison and fair-price/missing-information answers; new real `ai_tasks`/`assistant_runs` response IDs/model/tokens/outcomes; current UI consent/inbox/edit/delete/mobile/private-public behavior. Automated Chromium may cover these with mocks, but those results must remain labeled simulated.

The configured inventory URL is **http://127.0.0.1:8000/shop/demo-dealer** and the dashboard is **http://127.0.0.1:8000/**. They are target URLs, not a claim that a server is currently listening. After execution access is available, restart with `bash scripts/run-local.sh`; no new download, credentials reset, database reset or Codex session is needed. The sole remaining paid attempt cannot establish every AI operation above.

## Offline fallback

Build first, then run `python -m scripts.rehearse`. Open `http://127.0.0.1:8002/`, sign in with `owner-motors@example.invalid` / `rehearsal`, and open the customer inventory. Synthetic data and simulated sign-in are clearly labeled; AI is disabled. This demonstrates interface and factual comparison if network/provider access fails. It is not a substitute for showing a previously verified real API record or for declaring the AI acceptance complete.

## Not included in this release

No appointment reservation, phone receptionist, payments, external inventory/market scraping, autonomous changes, model training, full production hosting or verified cross-industry deployment. Existing cross-industry architecture is preserved for later work. Presentation scope is the dealership workflow above, not a claim that the full small-business platform is complete.
