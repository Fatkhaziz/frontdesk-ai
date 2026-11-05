# Live Grok update — November 4, 2026 evening

This update supersedes the earlier no-Grok configuration and checklist below. The local server remains on http://127.0.0.1:8000/, using the existing Supabase configuration and TLS verification. Branch: `feat/feasibility-demo`. No deployment or schema changes.

Local settings: `XAI_MODEL=grok-4.20-0309-non-reasoning`, `DRAFT_AI_ENABLED=1`, `QUESTION_MODE=demo`, `AI_CALL_LIMIT=10`. The replacement key authenticated successfully to the model catalog. Secrets remain in ignored `.env`; no key values were printed or committed. The ten-call lifetime cap includes failures; it is a call guard, not a provider dollar balance. Each call has a 200-token output cap and no automatic inference retry.

Exactly one live inference succeeded through `POST /api/listings/{id}/draft`, with real Supabase persistence and real xAI. Listing `6817e4f1-13b8-4fed-ae9b-1a0493ab96d2` is an unpublished 2022 Toyota Camry draft. The persisted counter moved from 0 to 1. Provider usage: 283 input tokens, 26 output tokens, 309 total. Diagnostics includes `kind=draft`, `status=succeeded`, the provider model and response ID, usage, result and timestamp. A preceding disabled route check returned 503 without contacting xAI or incrementing the counter.

The first live draft incorrectly rendered the stored cents price as “2,350,000.” It remains private and must be corrected/reviewed before publication. The request adapter now sends explicitly labeled `price_usd` dollars, verified using a mocked provider request; no second paid inference was made. Raw diagnostics retain the original response as evidence. This fix has not been verified against another live inference.

Verification used an isolated FastAPI TestClient with the existing owner identity injected only in that process. The running server has normal Supabase authentication, and anonymous private API requests return 401. Real Safari/password login was not automated. Fourteen isolated tests pass using mocked AI; TypeScript/Vite build passes. Running HTTP checks returned 200 for home/health and scripted public price Q&A, with `questionMode=demo` and `aiEnabled=true`.

In Safari, sign in at the home page, select a saved car (or click **New car**, enter facts, then **Save draft**) and click **Generate description with Grok** for a new paid draft. Click **Owner diagnostics** to inspect `last_actual_ai_request`; `status=succeeded`, the exact model, provider response ID and nonzero usage confirm a provider response. To inspect existing live evidence without spending again, click **Owner diagnostics** without generating. Review/correct the description before **Approve and publish saved revision**.

Customer Q&A is scripted: supported price/mileage questions use approved facts and unknown questions offer staff handoff. It consumes no xAI calls. Only listing drafting is live Grok. Server log: `/private/tmp/frontdesk-ai-local.log`; server launched detached with the project launcher.

---

# Local dealership demo handoff

Verified November 4, 2026. Local URL: http://127.0.0.1:8000/.

## Configuration and original failure

The original `/api/diagnostics` and `/api/listings` requests returned HTTP 503 because libpq could not read the CA certificate. The absolute certificate path contains spaces; form-style URL encoding had converted spaces to `+`, which libpq treated literally. The local `.env` now uses `%20`, an absolute path under `.certs/`, and `sslmode=verify-full`. Credentials and the certificate remain local and are excluded from Git and Docker.

The original error was reproduced in an isolated read-only API process with the old encoding: both routes returned 503 and safe backend logs identified `OperationalError`, category `tls_ca_unreadable`, origin `connect`. Corrected configuration returned 200. No raw driver messages, credentials, or tokens were logged. New failures include a request ID, exception type, safe category, SQLSTATE and function name in backend logs.

Run from the project directory after building:

```sh
npm run build --prefix frontend
bash scripts/run-local.sh
```

The launcher loads the project `.env` regardless of the shell's starting directory. It verifies the absolute readable CA path, requires `verify-full`, and checks PostgreSQL before serving on loopback port 8000. Stop the existing server before launching another instance. Rebuild after frontend changes. Restart after changing `.env`.

The delivered app was left running as a detached local process. Its credential-safe log is `/private/tmp/frontdesk-ai-local.log`.

## Demonstration behavior

`QUESTION_MODE=demo` is the default and is explicitly set in the local `.env`. The UI labels question matching as scripted and not AI. It answers a small set of exact price/mileage questions from the approved snapshot. Unknown or mixed questions offer staff handoff. Demo mode blocks both real AI question classification and description generation, even if xAI credentials are present. No paid API requests were made; the persisted AI call counter remained unchanged.

Descriptions can be entered manually or formatted from the entered vehicle facts. Saving produces a private draft. A business owner must review the saved revision and explicitly approve publication. Unsaved changes disable the approval checkbox and publish button. Public pages and answers use only the approved snapshot; edits remain private until a new approval. The existing live xAI behavior is available only after deliberately selecting `QUESTION_MODE=ai` and configuring the key/model.

## Checks actually passed

- Twelve isolated backend tests, using SQLite and injected Auth/AI: configuration, tenant isolation, role checks, private drafts, manual approval, stale revisions, AI failure behavior, inbox isolation/idempotency, demo behavior without AI calls, and safe correlated error logs.
- TypeScript check and Vite production build.
- Local PostgreSQL configuration: absolute readable CA, `sslmode=verify-full`, successful read, active TLS on the actual client-to-Supabase connection. The pooler's internal database hop is separate from this client TLS check.
- Existing confirmed active owner membership for `demo-dealer` verified by a read-only query. No Auth users or credentials were changed.
- Application-route rehearsal against real Supabase: diagnostics/listings/inbox 200; new Camry creation and retrieval with a separate connection; private draft protection; explicit manual approval; signed-out published read; hidden unpublished edits; stale approval rejection; republication; scripted questions; unknown-fact handoff; inquiry persistence, retry deduplication and staff status updates.
- The authenticated route rehearsal used an injected owner identity only inside an isolated TestClient process. It did not bypass authentication on the running server or test password sign-in. Existing data was preserved; migrations were not repeated.
- Running HTTP server: exact built HTML and JS/CSS with correct MIME types; runtime demo configuration; anonymous private API requests return 401; published facts and question/handoff endpoints work.
- Real Chromium browser with no authenticated session: sign-in screen and demo disclosure render; Camry public page shows $23,500 and 42,000 miles; price/mileage questions answer correctly; accident history offers handoff; synthetic inquiry submitted through the UI is present in the real Supabase owner inbox; page reload preserves published facts; zero runtime errors.

Retained rehearsal listing:

http://127.0.0.1:8000/listing/c7bffa96-c7e3-4919-872d-be1935abca4b

It is a 2022 Toyota Camry at $23,500 with 42,000 miles, available, published revision 3. The manual description identifies it as a demo rehearsal vehicle. Two synthetic inquiries were retained: an API rehearsal inquiry marked pending and a browser-submitted accident-history inquiry marked open. Existing vehicles and inquiries were not modified.

## Remaining private browser check and presentation

1. At the local home page, enter your existing demo owner email/password privately in the website. Click **Owner diagnostics** (expect connected, demo mode and AI disabled), then **Reload saved records** (expect no error). This real owner login and dashboard check still needs your credentials; Safari has not been automated.
2. Click **New car**. Defaults are 2022 Toyota Camry, price `2350000` cents and mileage `42000`. Click **Fill manual description from current facts**, then **Save draft**. Expand **Review saved database record**. Refresh, sign in again, and reopen that saved draft to prove persistence. A matching Camry was already rehearsed and retained if you prefer to inspect it first.
3. Review the saved facts/description, tick approval and publish. Open **Open public listing** in a private window. Show the approved price/mileage and the explicit demo-mode banner.
4. In the owner tab, change price to `2450000`, update the manual description and save. Refresh the private public window: it must still show $23,500. Approve and republish; refresh again to show $24,500. Restore $23,500 and republish if desired.
5. In the private window ask **Price?**, **Mileage?**, and **Accident history?**. Explain that question matching and description formatting are scripted, not Grok. Submit synthetic contact information such as `presentation@example.invalid`. In the owner tab, click **Reload saved records**, show the staff inquiry inbox, and mark the inquiry pending.

## Review state

Work remains uncommitted on `feat/feasibility-demo`. Changes are limited to local startup/error diagnostics, demo-mode configuration and matching, the existing dealership UI, tests, and setup/handoff documentation. No schema changes or paid API calls were needed. Local `.env`, `.certs/`, virtual environment, node modules, built assets, and temporary browser tools are excluded from the proposed source changes. Private owner sign-in remains the final user check before claiming the whole workflow passed in Safari.

| Changed files | Purpose |
| --- | --- |
| `backend/local.py`, `scripts/run-local.sh` | Load local settings consistently, validate TLS/CA, check connectivity and start on loopback. |
| `backend/errors.py`, `backend/main.py` | Safe correlated error logs, runtime mode reporting, guarded AI paths and approved-snapshot demo answers. |
| `backend/config.py`, `backend/demo.py`, `.env.example` | Explicit demo/live mode and deterministic supported-question matching. |
| `frontend/src/main.tsx`, `frontend/src/style.css` | Demo disclosure, manual descriptions, safe approval state, identifiable saved cars and staff handoff UI. |
| `tests/test_workflow.py` | Demo/no-paid-call, manual approval/privacy and safe-error regression coverage. |
| `.gitignore`, `.dockerignore` | Exclude the local CA directory as well as existing credential exclusions. |
| `README.md`, `docs/local-demo-handoff.md` | Current local setup, presentation sequence, evidence and remaining personal checks. |
