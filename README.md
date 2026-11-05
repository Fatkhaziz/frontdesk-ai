# FrontDesk AI — fall dealership feasibility demo

React/TypeScript and FastAPI serve one application; Supabase provides PostgreSQL and Auth, and xAI provides server-side Grok drafting and bounded question classification. This demo covers structured vehicle facts → private AI draft → owner approval of a saved revision → public listing → approved-fact answers → staff inquiry handoff. Spring bookings, events, billing, photos, and other extensions are outside this preparation.

See [the presentation handoff](docs/local-demo-handoff.md) for exact Safari clicks, live verification results, retained records and duplicate cleanup. Original requirements/design documents remain in [docs](docs/).

## Local configuration

Use a local `.env` copied from `.env.example`; never commit credentials. `.env`, `.certs/`, `.venv/`, `frontend/node_modules/`, and `frontend/dist/` are ignored. Runtime configuration exposes only the Supabase public URL/key to the browser.

| Setting | Purpose |
| --- | --- |
| `DATABASE_URL` | Supabase session-pooler PostgreSQL URL with `sslmode=verify-full` and an absolute readable `sslrootcert` path. Percent-encode path spaces as `%20`, not `+`. Keep the CA in ignored `.certs/`. |
| `SUPABASE_URL` | Project HTTPS URL. `VITE_SUPABASE_URL` is accepted as a fallback. |
| `SUPABASE_PUBLISHABLE_KEY` | Public publishable or legacy anon key. Never a service-role/secret key. `VITE_SUPABASE_PUBLISHABLE_KEY` is a fallback. |
| `XAI_API_KEY` | Backend-only funded xAI key. |
| `XAI_MODEL` | Exact text-model ID in the account's authenticated `GET /v1/models` catalog. Checked before inference. |
| `QUESTION_MODE` | `demo`: honestly labeled Scripted fallback; `ai`: Grok classifies supported price/mileage questions. Unknown/mixed questions always offer handoff. |
| `DRAFT_AI_ENABLED` | `1` enables paid listing drafts, `0` disables them. If omitted, follows question mode. |
| `AI_CALL_LIMIT` | Hard project-wide lifetime attempt cap, including failed attempts. Local demo: 10. Not a dollar-balance meter. |

Do not place xAI/database secrets in a `VITE_` variable. The verified local model is `grok-4.20-0309-non-reasoning`. Each inference has a 200-token output cap and no automatic retry. Only vehicle facts or a supported question are sent to xAI; inquiry contacts are never sent.

## Database setup

A confirmed Supabase email/password user must already have an active owner/staff membership. No public business creation or role-management endpoint exists in this bounded demo. Only an owner can publish, unpublish, delete, or view system diagnostics. Staff can prepare drafts and handle inquiries. All private routes verify Supabase identity and business membership.

For a new database, load the environment privately and run:

```sh
python -m backend.migrate
python -m backend.check_connection
```

Migrations are atomic, serialized, and checksum-tracked. An existing manually created untracked schema is refused for review; do not recreate/reset it. `001_demo.sql` defines the existing data; additive `002_listing_ai_tasks.sql` links new AI requests to listings for safe deletion. Both are already applied in the current Supabase demo. Provision the business/membership using parameterized administration or the Supabase SQL editor with the actual confirmed Auth UUID. Browser database roles have no application-table grants.

## Build and run

Python 3.12 and Node 22+:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
npm ci --prefix frontend
npm run build --prefix frontend
bash scripts/run-local.sh
```

The launcher loads the project's `.env`, verifies the CA path and TLS mode, checks PostgreSQL, then serves http://127.0.0.1:8000/. Stop the existing server before restarting. Rebuild after frontend changes; restart after backend/environment changes. The current demo is left running detached, with safe logs at `/private/tmp/frontdesk-ai-local.log`.

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

21 backend tests use isolated SQLite with foreign keys enabled and injected Auth/AI. Three frontend tests check dollars/cents, validation, selection and ordering. No lint/format script existed; the build includes strict TypeScript checks. Optional `scripts/check-browser.py` uses Playwright/Chromium, a temporary SQLite database and mocked Auth/Grok on loopback port 8001 to rehearse the full owner/public/delete workflow at desktop/mobile sizes. Install browser tooling outside the repository's tracked artifacts; run with the project root on `PYTHONPATH`. Automated tests never load `.env` or call paid xAI.

These mocks are not real integration evidence. The handoff records the separate two-request live verification and its authentication limitations. Real Safari sign-in must use the owner's credentials privately.

## Deployment and limits

The existing Docker/Render configuration serves the built frontend and backend as one web service. Supply secure runtime settings, apply migrations before starting updated code, and verify the hosted flow before claiming deployment. This task leaves the local app running and pushes source; it does not deploy to Render.

This is a bounded demo, not an open public service. It has a project attempt cap rather than full token-cost accounting or per-client rate limiting. Keep it on loopback for presentation. Retention jobs, load testing, user trials, real Safari automation, photos, and spring features remain outside this preparation. The [handoff](docs/local-demo-handoff.md) distinguishes completed checks from those limits.
