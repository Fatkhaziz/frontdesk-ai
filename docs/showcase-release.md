# Fall Release 1 dealership showcase

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

1. In GitHub Desktop, fetch the release branch `feat/dealership-ai-release-1`. Use the configured project checkout with its existing private `.env` and certificate, not a new download without settings.
2. In Terminal, change into that repository and run:

```sh
bash scripts/setup-showcase.sh --with-examples
```

The script builds the frontend, checks real Auth configuration, applies pending checksum-tracked migrations, checks existing-row preservation, adds four clearly fictional vehicles to the sole existing owner business, and starts the server at `http://127.0.0.1:8000/`. Existing vehicles, users, policies, credentials and the attempt counter are not reset. Re-running the seed does not duplicate or overwrite its example vehicles. If multiple owner businesses exist, seed separately with `python -m scripts.seed_showcase --confirm-synthetic --business-id ACTUAL_ID` instead of guessing.

The launcher enables AI mode for its process when existing xAI settings are present. It does not change `.env`, raise `AI_CALL_LIMIT`, buy credits, or make an inference request. If port 8000 is occupied, stop the earlier app process with Ctrl+C in its terminal first. Keep the app terminal running during the showcase. Running the website does not require an active Codex session; paid API usage occurs on AI actions.

3. Sign in using the existing confirmed Supabase owner credentials. Open **Listings → Open customer inventory**. The public path is `/shop/{business_id}`. Original individual listing pages also link to the inventory/comparison page.
4. Review **Owner knowledge** and **System status** before presenting. An AI-disabled state or exhausted attempt cap is not a successful live verification.

### Budget and live verification

The existing global attempt limit is preserved. Last observed before this release: 9 of 10 used; current value must be checked in System status. Account credit balance is separate. Do not assume a new release creates more attempts or more credits.

Use `python -m scripts.verify_showcase_live --business ACTUAL_ID` for a read-only preflight. The explicit execute flag performs one real customer-shopping request only after both remaining budgets and current pricing are supplied and checked. It does not reset the counter or silently retry. A model mismatch stops execution. Owner question suggestions still require their own real browser check.

Current published standard global prices for `grok-4.20-0309-non-reasoning` are $1.25 per million input tokens and $2.50 per million output tokens, checked November 24 at https://docs.x.ai/developers/pricing. Each showcase request has a 48,000-byte payload bound and 1,800-token output cap. Pricing, balance and total authorized spending must be checked before real verification. An attempt cap is not dollar accounting. Retain the original total $5 spending authorization.

## Presenter sequence

Open the owner dashboard and the customer inventory in two browser tabs. Prepare real AI checks before class rather than discovering configuration issues while presenting.

1. **Owner knowledge.** Click **Suggest customer questions with AI** once. Point out a missing-information question. Supply a true approved answer or mark **Staff must answer**. Save privately, review the saved revision, tick the approval checkbox and publish. Do not publish fictional warranty or history claims.
2. **Inventory.** Show the four vehicles labeled fictional examples. Their specifications are illustrative; this is not real inventory or an actual dealership offer.
3. **Find my fit.** Enter: "My vehicle-price budget is $25,000. I need 5 seats for commuting and I prefer lower fuel use." Send once. Point to the updated preferences and the follow-up. Model wording will vary; assess whether it respects the facts and budget.
4. **Refine.** Respond to its actual follow-up. To show an explicit change, say: "I can raise my vehicle-price budget to $30,000." Confirm the changed preference. A new send is another paid request.
5. **Compare.** Select two or three vehicles in Inventory. Click **Compare selected**. Show the specification table, missing MPG/cargo values and calculated price difference. These factual comparisons make no AI request. Click **Explain this comparison with AI** once to discuss trade-offs.
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
| `showcase_ai.py` `provider_call()` | Actual HTTPS POST to `https://api.x.ai/v1/chat/completions`, with model, system instructions and minimal structured context. |
| `showcase_ai.py` `run_ai()` | Reserve an attempt; persist task/evidence before the network; validate result; check current snapshots; save separate provider and application outcomes. |
| `main.py` `identity()` and `owner()` | Validate bearer through Supabase Auth and require active membership/owner role. Never trust a client business ID as proof of permission. |
| `db.py` | Parameterized PostgreSQL access, commit and rollback. |
| `migrate.py` and migration 005 | Apply additive schema changes under advisory lock with checksums. Never edit already-applied SQL. |
| Supabase | Hosted PostgreSQL and authentication. The local Mac serves the web app; Grok runs at xAI. No local model or training is used. |

## What is stored where

| Supabase table | Stored information |
| --- | --- |
| `auth.users` | Managed login identity. `encrypted_password` stores a salted bcrypt hash, not a readable password. |
| `memberships` | Auth subject, business, owner/staff role and active state. It is not a password table. |
| `listings` | Private vehicle facts/description, revisions, approval and published snapshot. Extended facts remain JSON text. |
| `dealer_knowledge` | Private question/answer cards and the separately published owner-reviewed snapshot. |
| `knowledge_events` | Knowledge publication/unpublication audit contract; current UI publishes reviewed snapshots. |
| `ai_tasks` | Operation, model, provider status, time, duration and typed usage metadata. |
| `assistant_runs` | New showcase task/request/business links, source snapshot, cited source IDs, provider response ID, tokens, latency and application outcome. |
| `ai_interaction_evidence` | Earlier business-profile Q&A evidence path; not the table for the new shopping assistant. |
| `shopping_inquiries` | Explicitly submitted contact/message, preference and vehicle snapshots, retry key and status. |
| `inquiries` / `business_inquiries` | Earlier vehicle/service request flows, retained. |
| `ai_budget` | Shared lifetime attempt count. Not a provider dollar balance. |
| `schema_migrations` | Applied migration filenames and SHA-256 checksums. |

HTTP logs contain request ID, route, status and duration in the app process console. The new AI table stores the matching request ID durably. Raw customer chat and raw provider output are not retained as evidence. Shopping inquiries and showcase evidence retain submitted/published snapshots when an individual listing is deleted; no automatic retention purge is implemented. Inputs/outputs still travel to xAI for inference; public business data is not private merely because its evidence is owner-only.

### Show the latest recorded API request

Run in Supabase SQL Editor:

```sql
SELECT t.created_at,t.kind,t.model,t.status,
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

Supabase **Authentication → Users** lists accounts. In SQL Editor, query `auth.users` and point to `encrypted_password`; this column contains a hash. Never show `.env`, bearer tokens, an xAI key or a database connection string on a projector.

```sql
SELECT id,email,encrypted_password
FROM auth.users
WHERE id = 'ACTUAL_AUTH_USER_UUID';
```

Official explanation: https://supabase.com/docs/guides/auth/password-security . Password hashing is a Supabase capability already in use, not a new custom password-storage implementation.

## Verification and honest limits

Automated suites use injected Auth and mocked provider completions. They test state transitions, rejection paths, source identity and constraints; they do not establish real Grok answer quality or semantic correctness. Prompts, source citations and numeric checks reduce specific failure modes, not every hallucination. Display the AI explanation as advisory and review facts. Known hard constraints may yield no verified match; unknown fees block claiming a total-budget fit.

The initial implementation passed 57 backend tests, 6 frontend tests, TypeScript/Vite production build, disposable PostgreSQL migration upgrades, original vehicle Chromium, new showcase Chromium and retained multi-business Chromium in GitHub Actions run 45521801895. The completed local suite now includes 60 backend tests and 9 frontend tests; the final commit must retain passing CI. Real Supabase migration 005, current Mac password sign-in and real new-provider responses are separately required. Do not replace these checks with a mocked rehearsal.

## Offline fallback

Build first, then run `python -m scripts.rehearse`. Open `http://127.0.0.1:8002/`, sign in with `owner-motors@example.invalid` / `rehearsal`, and open the customer inventory. Synthetic data and simulated sign-in are clearly labeled; AI is disabled. This demonstrates interface and factual comparison if network/provider access fails. It is not a substitute for showing a previously verified real API record or for declaring the AI acceptance complete.

## Not included in this release

No appointment reservation, phone receptionist, payments, external inventory/market scraping, autonomous changes, model training, full production hosting or verified cross-industry deployment. Existing cross-industry architecture is preserved for later work. Presentation scope is the dealership workflow above, not a claim that the full small-business platform is complete.
