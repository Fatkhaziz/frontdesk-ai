# FrontDesk AI presentation handoff

Verified November 5, 2026. Local app: http://127.0.0.1:8000/. Branch: `feat/feasibility-demo`. The server is detached; its credential-safe log is `/private/tmp/frontdesk-ai-local.log`. No spring features were added. Previous rehearsal notes are preserved in [the archive](archive/local-demo-handoff-before-dashboard.md).

## What is live

Existing Supabase Auth and PostgreSQL configuration, verified TLS, Grok listing drafting, and Grok classification of supported customer questions. Local configuration uses `QUESTION_MODE=ai`, `DRAFT_AI_ENABLED=1`, `XAI_MODEL=grok-4.20-0309-non-reasoning`, and the preserved `AI_CALL_LIMIT=10`. Only supported price/mileage question phrasings reach Grok; mixed, ambiguous, availability, accident-history and other unsupported questions immediately offer staff handoff. The backend checks Grok's fields against the supported scope and constructs every answer from the published database snapshot. It never displays generated price or mileage prose as a customer answer.

Exactly two paid requests were made during this final preparation: one draft and one classification. The persisted counter increased from 3 to 5; five attempts remain under the existing lifetime cap. Every request has a 200-token output limit and no automatic inference retry. This is a request cap, not a dollar-balance meter; no additional credit was purchased and no balance/top-up setting was changed. Automated tests and browser rehearsals mock AI.

The final draft correctly returned “2022 Toyota Camry with 42,000 miles. Available now. $23,500 USD.” The live classification used 278 tokens and returned the allowed price/mileage fields; the answer was “The price is $23,500.00 USD. The mileage is 42,000 miles.” while the private draft price was $24,500. An unsupported question saved a synthetic inquiry, confirmed in the real inbox. The fixture was restored to $23,500 and unpublished; existing records were untouched.

## Presentation records

Keep **2022 Toyota Camry — published revision 7**, $23,500, 42,000 miles, availability available, published November 4 at 11:32:56 p.m. New York time:

`6817e4f1-13b8-4fed-ae9b-1a0493ab96d2`

Public page: http://127.0.0.1:8000/listing/6817e4f1-13b8-4fed-ae9b-1a0493ab96d2

The list selects this latest published Camry by default. Selection is remembered across refresh in this browser tab; sign-in must be repeated. Only the selected listing ID is stored in session storage, never the session token or vehicle data. The listing is fetched again from the API after sign-in.

Delete these optional rehearsal copies through **Listings → select card → Listing management → Delete listing → confirm vehicle name**. None has been deleted automatically:

| Record | How to identify it in the UI | Exact ID |
| --- | --- | --- |
| Older Camry rehearsal | Published, saved/public revision 3, “Duplicate / rehearsal copy”; description begins “Demo rehearsal vehicle.” | `c7bffa96-c7e3-4919-872d-be1935abca4b` |
| Final verification fixture | Draft, saved revision 4, no public revision, “Duplicate / rehearsal copy”; its inbox item says “Final rehearsal: accident history?” | `484aa219-c744-4c82-af19-ae0aeeb4e5ce` |

The existing 2020 Toyota Rav4 ($21,500, 22,000 miles, published r1, `4726dab6-4450-43c8-bcab-a7466779a20e`) and 2026 BMW M2 ($62,000, 3,000 miles, draft r2, `42301746-3adf-4eb6-8304-8db9e6fad8f5`) are distinct vehicles, not proven duplicates. They were preserved; the incomplete BMW can be removed manually if you do not want it shown.

## Exact Safari walkthrough

1. Open the local home page and sign in with your existing verified owner account. **Listings** opens with the latest published Camry, unless this tab remembers another selection. Select the card marked **Latest published copy**, saved/public r7. Confirm the dollar price is `23500`.
2. In **1 Vehicle details**, review the structured facts. Click **Save vehicle details** to move to **2 AI description**. Click **Generate with Grok** only once if demonstrating a new paid call; wait for the success notice. You can edit the description, then click **Save description**. That saves privately and opens **3 Review and publish**.
3. Read the saved facts and description in the review panel. Tick **I reviewed the saved revision and approve these facts and description.** Click **Publish approved revision**, then **View public page ↗**. The generated description was never automatically public.
4. In the public tab, enter `Price and mileage?` and click **Ask question** once (one paid classification). Confirm $23,500 and 42,000 miles. Enter `Accident history?`, click **Ask question** (unsupported: no paid call), enter a synthetic contact such as `presentation@example.invalid`, then click **Send inquiry to staff**. Confirm the staff-inbox success message.
5. Return to the owner tab. Click **Inquiries → Refresh inquiries**. Find the Camry question and contact, then change **Status** to **Pending**. The newest inquiry is first.
6. Click **Listings**, select the presentation Camry, then **1 Vehicle details**. Change price to `24500` and click **Save vehicle details**. Refresh the public page: it must still show $23,500. In **2 AI description**, manually update the price in the wording, then **Save description → review checkbox → Publish approved revision**. Refresh the public page: it now shows $24,500. Restore `23500`, fix the wording, save/review/publish again if you want the starting state back. No Grok regeneration is required for this part.
7. Click **System status → Refresh status**. Show Auth ready, database connected, drafting ready, Live AI, backend running, used/limit, and the last successful model/token count/time. Expand **Technical API diagnostics** only if asked: provider response ID and usage demonstrate a real provider response. Status checks do not spend credits.
8. For a persistence check, refresh the owner page, sign in again, and confirm the selected listing and saved data return. Unsaved edits are intentionally discarded on reload. On a narrow Safari window, the vehicle cards scroll horizontally and the stage buttons remain visible.

If you prefer zero additional spending during the talk, use the saved approved description and show System status's existing live-request evidence. Avoid Generate/Ask on supported questions; accident-history handoff remains free. At five used calls, the full optional paid sequence above leaves three attempts available.

## Verification completed

- 21 backend unittest cases passed, including tenant/staff/anonymous authorization, delete not-found and related cleanup, transaction rollback, friendly validation, AI failure, saved/public snapshot separation, inquiry persistence/idempotency/order, and 20 unsupported/mixed/hostile questions denied without provider calls. SQLite foreign keys are enabled in tests.
- Three frontend Node tests passed: exact dollar-to-cents conversion/rejection, invalid facts, latest-published selection and ordering.
- TypeScript check and Vite production build passed. There is no existing separate lint/format script. `git diff --check` passed.
- Isolated Chromium desktop and 390px mobile rehearsal passed: mocked sign-in; default listing; friendly blank-make validation; cents conversion; refresh/re-login; mocked Grok/edit/save/approve; public snapshot isolation; chat/handoff/inquiry; inbox status; delete cancel/confirm/cleanup; no horizontal page overflow; zero browser runtime errors. The script never loads `.env` and uses isolated SQLite records and mocked Auth/AI. Run `PYTHONPATH=. python scripts/check-browser.py` with Playwright/Chromium installed, after building. In this session the existing tools were supplied through temporary PYTHONPATH and PLAYWRIGHT_BROWSERS_PATH locations.
- Real Supabase migration 002 applied after the unchanged tracked migration 001. Real app-route verification passed draft generation, explicit publication, private-price isolation, live classification, handoff/inquiry persistence, and restoration to an unpublished fixture. This used an owner identity injected only in an isolated TestClient process. The running server retains normal Supabase Auth; no authentication bypass was added to production.
- Secrets and certificate material are ignored and excluded from the commit. Actual Safari/password login remains the owner's private check; the browser rehearsal used mocked credentials.

## Delete semantics and limits

One transaction locks the tenant's listing, deletes its inquiries, deletes linked AI tasks (and cascade link records), deletes associated publication audit entries, and deletes the listing row containing saved revision/approval/public snapshot. Any failure rolls everything back. The project-wide AI attempt count is never refunded. Tests perform deletion only on isolated records; no existing Supabase record was deleted.

Migration 002 adds a backend-only link table so new AI requests can be removed with their listing. Older AI tasks had no listing reference and cannot safely be retroactively assigned, especially after descriptions were edited. Those unlinked legacy business-level logs are preserved, rather than guessing and deleting another listing's history. This limitation does not leave an accessible public page or inquiry after deletion.

The app remains a narrow loopback feasibility demo: no photos, spring booking/billing, open-ended chat, automatic staff notifications, or automatic retention. Customer Q&A supports a deliberately bounded set of price/mileage phrasings. Owner content review is still required. Real Safari login/keyboard interaction should be checked with the walkthrough above; Chromium automation is not a Safari compatibility claim.
