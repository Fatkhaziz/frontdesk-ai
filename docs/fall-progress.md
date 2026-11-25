# Fall progress and practice guide

> November 24 scope update: the current dealership AI showcase, setup, acceptance criteria and evidence map are in [showcase-release.md](showcase-release.md). This document retains earlier baseline or full-system design details; three live business examples are no longer required for the fall showcase.

> Historical November 19 snapshot. The [November 24 Fall Release 1 handoff](fall-release-1.md) supersedes implementation status, answering behavior, tests and verification instructions below.


Updated November 19, 2026. FrontDesk AI serves small businesses. Dealership and salon examples now share one configuration and inquiry workflow. This remains a fall feasibility prototype toward the semester's 20% milestone; the final system's platform administration, scheduling, voice and broader dealership operations remain future work.

## What this continuation implements

- A business owner edits hours, time zone, services, service prices, intake questions and approved FAQs.
- Private revisions remain separate from public snapshots. Publication requires explicit approval of the current saved revision. Stale saves and stale request forms are rejected.
- Public business pages show only published information. FAQ answers use normalized exact matching, without a paid AI call. Unknown questions offer voluntary staff follow-up.
- Service forms use that business's published questions. A successful request is committed to its staff inbox; repeat submissions with the same key and payload return the original inquiry.
- Staff can handle inquiries but cannot edit or publish business settings. All private API queries use the authenticated membership's business ID. Another business's inquiry cannot be updated.
- Existing vehicle drafts, Grok generation, approval, public listings, inquiries and deletion remain available. General business pages do not claim Grok-backed conversational understanding.

The implementation is deliberately smaller than the final specification. There is no platform administrator interface, self-service business registration, department grants, calendar booking, resource availability or notification delivery in this continuation. A service duration is descriptive and does not reserve a time.

## Evidence and limits

Executed here: 28 backend tests, 5 frontend tests, strict TypeScript checks and the Vite build. Backend tests use isolated SQLite, injected authentication and mocked AI. Frontend interaction tests use a simulated DOM. They cover separate business facts/forms, approval and publication, staff permissions, inquiry persistence, repeated submission, required answers and business isolation. Original migrations 001 and 002 are unchanged.

Not verified here: real Supabase authentication, PostgreSQL migration 003, paid Grok requests or rendered browser layout. This workspace could not launch a local Chromium test because Unix sockets are restricted; the separate cloud browser could not reach the local server. The checked-in Playwright scripts are available for a Mac browser run. These limits must not be described as passed integration checks.

## Practice without paid calls or live data

After dependencies and the frontend build are ready, run this from the repository root:

```sh
.venv/bin/python -m scripts.rehearse
```

Keep that Terminal window open. In Safari, click the address bar, type `http://127.0.0.1:8002/`, then press Return. This is an explicitly labeled rehearsal using temporary SQLite and simulated sign-in. It does not read `.env`. Data resets when this process stops. It disables paid AI even if the surrounding shell contains an API key.

Use `owner-motors@example.invalid` and password `rehearsal` for the dealership. Use `owner-salon@example.invalid` and the same password for the salon. Use `staff-salon@example.invalid` with the same password to check staff restrictions. These are fictional rehearsal accounts; they do not sign into Supabase or the normal app.

1. Sign in as the dealership owner. Click **Business settings**. Show its hours, service question and cancellation FAQ.
2. Change the FAQ answer. Click **Save private settings**. The published answer remains unchanged until approval.
3. Tick **I reviewed the saved settings and approve this revision for customers**. Click **Publish approved settings**, then **View business page**. The latter opens a customer page in a separate tab.
4. On that page, click the cancellation question and **Check approved answer**. Select the vehicle service, answer its vehicle question, enter a message and `practice@example.invalid`, then click **Send inquiry to staff**.
5. Return to the dashboard tab. Click **Inquiries**, then **Refresh inquiries**. Find the message and change its status to **Pending**.
6. Sign out and sign in as the salon owner. Its service form asks about a stylist, its hours and cancellation policy differ, and the dealership inquiry is absent.
7. Sign in as salon staff. Settings are read-only; the salon inbox remains available.

This rehearsal proves the application flow with synthetic data. To demonstrate real Supabase or Grok, use the normal application after the integration checks below.

## Update the normal Mac demo

Preserve existing local edits. Fetch the review branch, install dependencies, build, then privately load the existing `.env` and run `python -m backend.migrate` and `python -m backend.check_connection` from the project virtual environment. Do not overwrite `.env`, reset the database, change certificate verification or edit applied migrations. Run `bash scripts/run-local.sh` after applying migrations. This launcher uses port 8000; follow the actual startup URL if the existing local command uses a different port.

Verify real sign-in and the original vehicle flow, then publish one business profile and submit/retrieve a service inquiry. Separate real salon verification needs a second confirmed Auth user and its own business membership. Do not claim separate live businesses solely from changing one business's type. Use the two-business rehearsal if that second account is not yet provisioned.

Optional browser tooling, when available on the Mac:

```sh
python -m pip install playwright
python -m playwright install chromium
PYTHONPATH=. python scripts/check-browser.py
# In another project Terminal while the fresh rehearsal is running:
PYTHONPATH=. python scripts/check-business-browser.py
```

These browser scripts use synthetic data and simulated Auth/AI. Actual owner sign-in and provider evidence remain separate checks. Keep paid AI disabled for rehearsal and do not increase the existing lifetime cap or add credits.

## Where to show the technology

| Question | Concrete evidence |
| --- | --- |
| What runs the website? | React and TypeScript render the interface; Vite builds it. Python FastAPI validates requests and controls access. |
| Where is live business data? | Supabase hosts PostgreSQL. `business_profiles` stores private and approved profile snapshots; `business_inquiries` stores service requests and intake answers; `business_profile_events` records publication actions. These tables appear only after migration 003. |
| Where are existing cars and requests? | `listings` holds vehicle drafts and approved snapshots. `inquiries` holds vehicle follow-up requests. `audit_events` records vehicle publication. |
| Where are users and permissions? | Supabase Authentication manages users in `auth.users`; `memberships` links the authenticated subject to a business and owner/staff role. |
| Where is the password? | Supabase stores a salted bcrypt password hash in `auth.users.encrypted_password`, not a readable password. Authentication Users shows the user; a read-only SQL query can show whether a hash exists. |
| Where are Grok calls logged? | `ai_tasks` stores kind, model, status, duration, result, usage and time. The `usage` JSON includes provider response ID, provider model and token counts. `listing_ai_tasks` links supported requests to a listing. `ai_budget` counts attempts; it is not an API-call log or dollar balance. |
| Where are HTTP request logs? | FastAPI logs request ID, method, route, status and duration to the server console. These differ from saved AI task records and customer inquiries. |
| Is everything AI? | Vehicle drafting and bounded price/mileage classification can use live Grok when enabled. New business FAQs use exact approved-question matching. Staff inquiries are database records, not AI inference logs. |
| Is it hosted publicly? | The normal demo runs on the Mac while its Supabase database is hosted. Public web hosting still needs deployment and verification. |

Password reference: https://supabase.com/docs/guides/auth/password-security

For a read-only proof without displaying password hashes:

```sql
SELECT id, email, email_confirmed_at,
       COALESCE(length(encrypted_password), 0) > 0 AS password_hash_present
FROM auth.users
ORDER BY created_at DESC
LIMIT 10;
```

For recent AI requests, open Supabase Table Editor, select schema `public`, then select `ai_tasks`. Inspect `usage` for the response ID and token counts. Or use:

```sql
SELECT id, kind, model, status, duration_ms, usage, created_at
FROM public.ai_tasks
ORDER BY created_at DESC
LIMIT 10;
```

An existing successful row is sufficient to explain logging. Reading these records does not spend credits. Do not generate another request solely to populate a slide.

## Next class work

Review the revised requirements and detailed design together with the feedback mapping. Use the new prototype to explain how two business types share software while keeping separate rules and inquiries. Attach executed test evidence to the fall progress report. Record real November team/mentor activity and confirm the next Blackboard assignment's actual instructions and deadline before submitting; no new class due date has been verified here. Keep spring implementation out of the current work.
