# FrontDesk AI — feasibility demo

Presentation: November 5, 2026; backup November 12. React/TypeScript and FastAPI run as **one Render web service**. Supabase supplies PostgreSQL and Auth. xAI calls run exclusively on the backend. Baseline documents are in [docs](docs/).

For the current no-Grok demo, actual verification results and the remaining private browser checklist are in [the local demo handoff](docs/local-demo-handoff.md).

## Configure securely

Copy `.env.example` to `.env` locally, or set these names in Render's environment settings. Never commit `.env`.

| Name | Setup action |
| --- | --- |
| `DATABASE_URL` | Supabase Connect → session pooler PostgreSQL URL, including password. Use TLS certificate verification (`sslmode=verify-full`). Percent-encode password characters. |
| `SUPABASE_URL` | Project HTTPS URL. |
| `SUPABASE_PUBLISHABLE_KEY` | Project publishable key (legacy anon key also works). **Never use service_role or secret key here**: this key is intentionally returned to the browser. |
| `XAI_API_KEY` | Create an xAI API key with funded API access. Backend only. |
| `XAI_MODEL` | An exact ID from authenticated `GET https://api.x.ai/v1/models`. No default is assumed; every AI operation validates catalog membership before inference. |
| `AI_CALL_LIMIT` | Default 100; hard lifetime project call cap, including failures. Increase deliberately after reviewing usage. |
| `QUESTION_MODE` | Default `demo`: fixed price/mileage question matching, manual descriptions, no AI requests. Set `ai` deliberately to enable the real xAI paths. |

For this cloud's restricted network, allow `api.x.ai`, your exact `PROJECT.supabase.co` Auth host, and your Supabase database/pooler host (TCP 5432). Preserve existing package/GitHub access. Do not put credential values in chat.

## Supabase preparation

1. Create a project and enable email/password Auth. Create and confirm a test owner in the Auth dashboard; copy its user UUID.
2. Run `migrations/001_demo.sql` once in the Supabase SQL editor (or `psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f migrations/001_demo.sql`). Tables are backend-only; browser roles have no grants.
3. Provision a membership with the actual Auth UUID, using parameterized administration or the SQL editor:

```sql
INSERT INTO businesses(id,name) VALUES ('demo-dealer','Demo Motors');
INSERT INTO memberships(subject,business_id,role) VALUES ('ACTUAL-AUTH-USER-UUID','demo-dealer','owner');
```

Create another business/user to verify isolation. Staff membership may read/edit drafts and handle inbox items; only owners publish or see diagnostics. No open business-registration endpoint exists in this narrow demo.

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

The local launcher changes to the project folder, loads its `.env`, requires an absolute readable `sslrootcert` and `sslmode=verify-full`, and performs a read-only PostgreSQL preflight. Keep the Supabase CA in `.certs/prod-ca-2021.crt` locally; `.certs/` and `.env` are ignored by Git and Docker. In the database URL, encode path spaces as `%20`, never `+` (libpq treats plus signs literally). Quote the complete URL in `.env`. Stop the old server before restarting the launcher. Build the frontend before starting so the static asset route is registered.

Open http://127.0.0.1:8000/. `/docs` exposes FastAPI contracts; `/health` is process health, **not** proof of database/AI readiness. Owner diagnostics executes `SELECT 1`, reports the question mode, and shows the latest actual AI task. It reports null before any actual call. The saved-record panel is a fresh API database read, not browser storage. Supabase SQL editor can independently show `SELECT * FROM listings;`.

In `QUESTION_MODE=demo`, both public Q&A and description drafting are prevented from calling xAI even if a key is present. The banner and public assistant identify scripted behavior. Supported questions include `Price?`, `Mileage?`, and `Price and mileage?`; unrecognized or mixed questions offer staff handoff. Answers always use the approved snapshot. `Fill manual description from current facts` formats only the entered facts; save it, review the saved record, check approval, and publish as an owner. Unsaved changes disable approval. Grok drafting remains disabled until `QUESTION_MODE=ai` and a key/model are configured.

Only public Supabase configuration comes from `/api/config` at runtime, so Render needs no Vite build-time secrets or environment arguments. Tokens stay in memory; reload requires sign-in again and retrieves saved database records. Sign out/re-sign in after token expiration.

## Tests

```sh
python -m unittest discover -s tests -v
npm run build --prefix frontend
```

Twelve isolated tests exercise configuration, persistence, tenant/role denial, manual approval, stale approval, late AI output, approved-value answers, inquiry storage/idempotency, safe error logging, and demo mode without AI calls. SQLite and injected authentication/AI are explicitly **test doubles**, not Supabase/xAI integration proof. Production requires PostgreSQL; SQLite is enabled only with `TESTING=1`.

## Deploy

Connect this GitHub repository in Render, choose **Blueprint**, and use `render.yaml`. This builds the frontend into the Python image and starts one Docker web service, with no Render database. Supply all secure settings above. Apply the migration before rehearsal. After deployment verify login, diagnostics, persistence across reload, actual Grok draft and both customer paths. Record the Render URL and actual results. Do not claim a live integration from unit tests.

## Five-minute professor walkthrough

- 0:00–0:40: Sign in as confirmed owner. Click Owner diagnostics and Reload saved records. Explain Supabase data/Auth and the clearly labeled scripted demo mode; Grok is not configured or called.
- 0:40–1:20: Save a 2022 Camry, 42,000 miles, price 2,350,000 cents. Reload, sign in again, select the saved car; expand the saved database record.
- 1:20–2:05: Use the manual description formatter, save, review the **saved revision**, check approval, publish. No AI-generated text is claimed.
- 2:05–3:00: Open the public listing in a private browser window. Ask `Price?` and `Mileage?`. Show answers match published data. Ask `Accident history?`, submit voluntary test contact details, reload the owner inbox, and mark the inquiry pending.
- 3:00–4:10: Change price to 2,450,000 cents and save. Public page still shows the prior approved price. Approve/publish the new revision, reload public page, ask again. Demonstrate stale revision rejection through `/docs` with an old `expected_revision`.
- 4:10–5:00: Show diagnostics' actual database status, demo mode, disabled AI, and request-ID logs. Summarize test evidence and the remaining real-AI integration work.

## Current limits

Photo upload deferred until live core integration passes. No subscriptions, bookings, events, workers, Redis, social or phone features. AI call count is a conservative project-wide cap, not token-cost accounting; no per-client rate limiter yet. Inquiry retries are deduplicated sequentially, but concurrent identical requests may return an error and should retry. Add edge rate limiting before opening the service to broad public traffic. Demo records and AI results require manual cleanup after rehearsal; automated retention is not implemented. Browser/device and concurrency/load validation remain outstanding.

### Environment settings aliases and connection checks

The backend accepts `VITE_SUPABASE_URL` as a fallback for `SUPABASE_URL`, and `VITE_SUPABASE_PUBLISHABLE_KEY` as a fallback for `SUPABASE_PUBLISHABLE_KEY`. These are read at runtime; a frontend rebuild is unnecessary. The canonical backend names take precedence. Neither database nor xAI credentials use a `VITE_` prefix.

After settings have reached the running process:

```sh
python -m backend.check_connection
python -m backend.migrate
python -m backend.check_connection
```

The migration runner applies migrations atomically, serializes runners, records checksums, and skips already applied migrations. An existing manually created but untracked schema is refused for review rather than overwritten. The connection checker reports actual PostgreSQL connectivity and Supabase Auth settings access without printing configuration values; it does not claim owner login succeeded. Restart an existing server after changing environment settings.
