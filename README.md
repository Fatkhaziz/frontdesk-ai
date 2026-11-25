# FrontDesk AI

FrontDesk AI is an AI receptionist platform for small businesses. The [November 19 requirements](docs/requirements.md) and [aligned detailed design](docs/detailed-design.md) address the professors' annotated feedback, including multiple business domains, business-specific rules, four roles and dealership operations. [Implementation work and evidence](docs/professor-feedback-implementation.md) describe the gaps between that specification and the current code. Earlier Word/PDF snapshots in this folder are historical design references.

## Current fall showcase

Following the November 24 faculty discussion, the 20% showcase focuses on a dealership with concrete AI use: **owner question suggestions and knowledge preparation**, **conversational customer preferences**, and **personalized vehicle comparison**. The final product remains a small-business platform. Existing salon/studio configuration code is retained for later development.

Start with the [current release guide](docs/showcase-release.md). It includes one-command Mac setup, the exact presentation sequence, code/database maps, API/password evidence and real-service verification limits. Earlier handoffs and Word snapshots describe prior scope and are historical where they conflict with that guide.

```sh
# In the existing configured Mac checkout, after pulling the release:
bash scripts/setup-showcase.sh --with-examples
```

The owner dashboard has **Listings**, **Owner knowledge**, **Inquiries** and **System status**. **Open customer inventory** opens `/shop/{business_id}` with Inventory, Find my fit and Compare. Four explicitly fictional vehicles can be added without overwriting existing rows. AI actions are explicit; browsing/comparison/status checks do not call xAI. Keep the existing total $5 authorization and shared attempt cap under review; setup does not reset or raise it.

## Local configuration

Use a local `.env` copied from `.env.example`; never commit credentials. `.env`, `.certs/`, `.venv/`, `frontend/node_modules/`, and `frontend/dist/` are ignored. Runtime configuration exposes only the Supabase public URL/key to the browser.

| Setting | Purpose |
| --- | --- |
| `DATABASE_URL` | Supabase session-pooler PostgreSQL URL with `sslmode=verify-full` and an absolute readable `sslrootcert` path. Percent-encode path spaces as `%20`, not `+`. Keep the CA in ignored `.certs/`. |
| `SUPABASE_URL` | Project HTTPS URL. `VITE_SUPABASE_URL` is accepted as a fallback. |
| `SUPABASE_PUBLISHABLE_KEY` | Public publishable or legacy anon key. Never a service-role/secret key. `VITE_SUPABASE_PUBLISHABLE_KEY` is a fallback. |
| `XAI_API_KEY` | Backend-only funded xAI key. |
| `XAI_MODEL` | Exact available text-model ID. Legacy drafting checks the catalog; showcase requests use the configured model and fail safely if unavailable. |
| `QUESTION_MODE` | `demo`: AI disabled for the showcase; `ai`: enables explicit shopping and owner-question AI requests when provider settings exist. Legacy vehicle Q&A remains narrower. |
| `DRAFT_AI_ENABLED` | `1` enables paid listing drafts, `0` disables them. If omitted, follows question mode. |
| `AI_CALL_LIMIT` | Hard project-wide lifetime attempt cap, including failed attempts. Local demo: 10. Not a dollar-balance meter. |

Do not place xAI/database secrets in a `VITE_` variable. The configured model is `grok-4.20-0309-non-reasoning`. Legacy vehicle inference has a 200-token output cap; new showcase inference has an 1,800-token output cap and a 48,000-byte payload bound. No automatic retry. The customer explicitly sends conversation context/preferences to xAI; staff inquiry contacts are kept out of AI payloads. The input filter rejects common credential/contact patterns but is not a universal personal-data detector.

## Database setup

A confirmed Supabase email/password user must already have an active owner/staff membership. No public business creation or role-management endpoint exists in this bounded demo. Only an owner can publish, unpublish, delete, or view system diagnostics. Staff can prepare drafts and handle inquiries. All private routes verify Supabase identity and business membership.

For a new database, load the environment privately and run:

```sh
python -m backend.migrate
python -m backend.check_connection
```

Migrations are atomic, serialized, and checksum-tracked. An existing manually created untracked schema is refused for review; do not recreate/reset it. `001_demo.sql` defines the existing data; additive `002_listing_ai_tasks.sql` links new AI requests to listings for safe deletion. Migrations 001 and 002 were applied in the earlier Supabase demo. Additive `003_business_reception.sql` creates business profiles, service inquiries and publication events; `004_ai_interaction_evidence.sql` adds provenance for new business Q&A attempts. Apply pending migrations before starting this updated application. Migrations 003/004 were verified on the configured Mac on November 24. New `005_shopping_assistant.sql` adds reviewed owner knowledge, publication events, shopping inquiries and correlated showcase AI runs; apply it before starting this release. Migration 005 and its checksum are now verified live through the configured Supabase dashboard; four authorized fictional vehicles were added while all pre-existing rows were preserved. The current attempt count is 9/10. See the release guide for the separate Mac server and real-AI blockers. Provision the business/membership using parameterized administration or the Supabase SQL editor with the actual confirmed Auth UUID. Browser database roles have no application-table grants.

## Build and run

Python 3.9+ (3.12 recommended) and Node 22+:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm ci --prefix frontend
npm run build --prefix frontend
bash scripts/run-local.sh
```

The launcher loads the project's `.env`, verifies the CA path and TLS mode, checks PostgreSQL, then serves http://127.0.0.1:8000/. Stop the existing server before restarting. Rebuild after frontend changes; restart after backend/environment changes. Do not assume an earlier detached server is current. Stop the old process and run the setup/start command from the current checkout.

## Interface and publication

The owner dashboard defaults to **Listings**, with separate **Inquiries** and **System status** sections. Latest published vehicles sort first; the latest published 2022 Toyota Camry is the default selection. Duplicate vehicle names are labeled for review; nothing is automatically deleted. Selection is remembered within the browser tab using only the listing ID. Auth tokens stay in memory; reloading requires sign-in and fetches records again.

The editor has three switchable stages: **Vehicle details**, **AI description**, **Review and publish**. Prices are entered in dollars and converted to integer cents only when building the API payload. Client and server validation reject invalid facts with friendly messages. Grok and the non-AI formatter are distinctly labeled. Generated text remains private and editable. Only explicit owner approval of the exact saved revision permits publication. Unsaved/private edits cannot change the public snapshot. A prominent **View public page** button follows publication; unpublish/delete are separate management actions.

Public listings show approved facts and description, conversation-style Q&A, and voluntary staff handoff. Supported questions include `Price?`, `Mileage?`, `Price and mileage?`, `What is the price?`, and `How many miles does it have?`. In live mode, Grok's field classification must agree with the bounded scope; FastAPI re-reads the published snapshot and builds the final price/mileage answer. Unsupported/mixed/ambiguous inputs, invalid AI output, and provider failures offer handoff. Availability and accident history are outside customer Q&A scope. Successful inquiry submission means saved in the staff inbox; no email/phone notification is claimed.

**System status** shows validated Auth, database readiness, drafting state, question mode, used/limit, backend health, and last successful model/token usage/time. Detailed diagnostics are collapsed and owner-only. `/health` is process health only; `/docs` describes the API.

## Safe listing deletion

`DELETE /api/listings/{id}` requires owner membership in the listing's business. A single database transaction locks the parent and removes inquiries, linked AI tasks, publication audit entries, and the listing row (including saved revision, approval and public snapshot). Foreign keys enforce relationships; any failure rolls back. The lifetime AI counter remains unchanged. Legacy AI tasks predating migration 002 have no provable listing link and are retained as business-level logs. No current demo record has been automatically deleted. The UI confirms the vehicle name before deletion.

## Checks

```sh
python -m unittest discover -s tests -v
npm test --prefix frontend
npm run build --prefix frontend
git diff --check
```

62 backend tests pass locally using isolated SQLite with foreign keys enabled and injected Auth/AI. [Maintenance CI](https://github.com/Fatkhaziz/frontdesk-ai/actions/runs/45528060342) passed 62 backend tests on both Python 3.9 and 3.12, all nine frontend interaction tests, the strict production build, disposable PostgreSQL checks and all three rendered Chromium workflows. These use mocked Auth/Grok, not the real configured services. The local production build passed; full local frontend tests remain blocked by unavailable test dependencies in the restricted runner. No lint/format script existed; the build includes strict TypeScript checks. Optional `scripts/check-browser.py` uses Playwright/Chromium, a temporary SQLite database and mocked Auth/Grok on loopback port 8001 to rehearse the full owner/public/delete workflow at desktop/mobile sizes. Install browser tooling outside the repository's tracked artifacts; run with the project root on `PYTHONPATH`. Automated tests never load `.env` or call paid xAI.

These mocks are not real integration evidence. Earlier handoffs describe historical provider checks; the PR #3 setup stage made no paid requests and did not attribute new metadata to historical records. The subsequent real-browser follow-up used the final authorized attempt; see the release guide’s current verification checkpoint. Real Safari sign-in must use the owner's credentials privately.

## Deployment and limits

The existing Docker/Render configuration serves the built frontend and backend as one web service. Supply secure runtime settings, apply migrations before starting updated code, and verify the hosted flow before claiming deployment. The earlier handoff records that local run. This continuation prepares source for review; it does not start the user’s Mac server or deploy to Render.

This is a bounded demo, not an open public service. It has a project attempt cap rather than full token-cost accounting or per-client rate limiting. Keep it on loopback for presentation. Retention jobs, load testing, user trials, real Safari automation, photos, and spring features remain outside this preparation. The [handoff](docs/local-demo-handoff.md) distinguishes completed checks from those limits.
