# Fall Release 1 dealership showcase




## Find my fit repair — prepared for one restart and controlled verification

The original failed task `f77bf375-db67-4be3-bb34-880eeff5781e` still has `invalid_output` and a null `ai_tasks.result`; its rejected text and exact reason cannot be recovered. Unpaid differential reproduction loaded the original validator and supplied a valid comparison of published $23,500/$26,500 prices: it rejected the correct $3,000 difference as `unsupported_number`. The repaired validator accepts that same grounded arithmetic. This establishes a real code defect, not proof that this particular lost Grok response failed for that reason.

- `backend/shopping.py` `source_list()` now supplies deterministic pairwise price differences with revision-specific input price references. `assist()` narrows provider inventory/sources to selected published vehicles when a selection exists and labels prices as USD dollars rather than exposing unlabeled integer cents. All publications are rechecked after the response; stale output is still rejected.
- `validate_answer()` checks cited source numbers and currency units, exact cited-price differences and budget gaps; MPG cannot become a dollar price. It validates both answer and follow-up, preserves earlier seats/features/priorities/budget meaning unless explicitly changed, and continues rejecting unsupported sources, foreign/unselected recommendations and invalid preferences. These checks are bounded checks, not a guarantee of complete factual or semantic correctness. No scripted substitution or automatic retry was added.
- `backend/ai_rejection.py` defines fixed stage/reason/field allowlists. `run_ai()` checks the provider envelope, duplicate JSON keys, nonfinite values, JSON parsing, structured fields, preferences, citations/claims and publication freshness. It stores only `{rejection:{stage,reason,field,source_id}}` in the existing `public.ai_tasks.result`. A source identifier is saved only if it is already in that request's approved snapshot. No exception message, unrestricted provider output, raw chat, contact, key or bearer is stored. No migration is needed.
- `/api/assistant/evidence` joins `assistant_runs` to that task result and returns sanitized `rejection` metadata; `SystemStatus.tsx` displays it beside the separate outcomes. Historical requests without metadata stay null and display that the reason was not recorded. `/api/diagnostics` now reports `showcase_validation_version:2` so a read-only check can establish the restarted code is loaded. `assistant_runs` remains the task/request/business/source/revision/provider/usage/latency/outcome record; no old evidence was backfilled or overwritten.
- The inaccurate private “real Toyotas” question and “real pricing” reason were corrected under revision/publication guards. Nine cards remain, private revision **6**, published revision **2**; an independent database hash confirmed the published snapshot was byte-for-byte unchanged. All corrected suggestions remain draft. The prior real rehearsal backup remains intact.

Fresh authenticated billing showed **$4.97**, automatic top-up disabled. At the checked global model rates and enforced bounds, each request has a conservative **$0.07342** ceiling: two controlled rehearsal requests ≤ **$0.14684**; all five remaining including the three class requests ≤ **$0.36710** ($0.37 rounded), within the original $5 authorization. Only the approved private cap was changed **16→17**. Historical usage remains **12**. No purchase, top-up, reset, migration or paid inference was performed during preparation.

After all changes and checks pass, perform one restart. Verify actual diagnostics show **12/17** and validation version **2**. Send one controlled selected-vehicle Find my fit request. Only if accepted, send one genuine history-bearing follow-up changing the budget to $30,000 while retaining five seats/fuel economy. Stop on either failure and inspect the new bounded rejection; do not retry or spend the three class attempts. Successful completion would leave **14/17**. Live retest, new screenshots and new durable outcomes are **pending**, not established by the mocked regressions. Private correction evidence is saved separately in `~/Desktop/FrontDesk-AI-Fix-Verification-2026-11-25/`.

## Actual live rehearsal — partial success, class reserve preserved

This is the latest state and supersedes the activation-pending notes below. On November 25 the restarted repository server reported **10 used / 16 total** with real Auth/PostgreSQL ready. Exactly **two** deliberate paid rehearsal requests were made, without retries. Final authenticated System status and an independent SELECT-only Supabase join confirm **12/16**: one rehearsal attempt unused and **all three class attempts reserved**. The server remains running at `http://127.0.0.1:8000/`.

| Actual rehearsal | Provider / application | Durable evidence |
| --- | --- | --- |
| Owner question suggestions | `succeeded` / `accepted`; seven questions, blank owner answers | Task `de2a8b27-72ea-4636-840c-3963a9ba11fb`; HTTP `e2d608f9-778b-4081-a31d-f6ea47506107`; provider `518f2c93-dc0a-4a11-b8ff-5ffc5f17be79`; 1,271 input + 309 output = **1,580 tokens**; **2,929 ms** |
| Find my fit, selected fictional Compact Hatch + City Hybrid; $25,000 vehicle-price budget, minimum five seats, fuel economy | `succeeded` / **`invalid_output`**; no accepted answer, extracted preferences or citations shown | Task `f77bf375-db67-4be3-bb34-880eeff5781e`; HTTP `be20c85d-b4b0-4586-bded-db04d7acf44a`; provider `ad23686e-0eee-4d1f-a277-a65b504ccdf0`; 12,350 input + 758 output = **13,108 tokens**; **4,738 ms** |
| Conversational budget-changing follow-up | **Not sent** | Failed first turn created no accepted conversation history (`PublicShop.tsx` `ask()` only appends after an accepted response). Spending another attempt could not demonstrate the requested successful continuation. No simulated continuation or retry was substituted. |

Both real responses reported `grok-4.20-0309-non-reasoning`. The accepted owner suggestions were saved additively as private knowledge revision **5**, nine total cards (two preserved plus seven new); published revision **2** was unchanged. Reloading owner knowledge verified persistence. Suggestions are drafts requiring human review: one calls existing Toyota listings “real,” which is not established by the published listing facts. It was not approved or published. Acceptance of the question schema does not prove every suggested premise is correct.

The independent SQL join of `public.ai_tasks` and `public.assistant_runs` found **71 input source entries per request**, no foreign/stale listing references against current same-business publication revisions, no private review-note text and no synthetic inquiry-contact text in either snapshot. Owner returned citations are empty by design because it suggests questions. Failed customer `source_ids` are cleared by `run_ai()` on rejection; an empty saved array does **not** establish that Grok itself omitted citations. The valid input snapshot does not prove that the rejected output used those sources correctly.

### Actual failure and missing diagnostic link

`backend/showcase_ai.py` → `run_ai()` records provider completion before parsing/checking the response, then stores `invalid_output` when parsing, shape, length, constraints, numeric or source validation raises. The customer saw the explicit rejection notice; no facts or published records were changed. The gateway intentionally discards arbitrary provider text, but also does **not** retain the specific validation error code. Neither `ai_tasks.result` nor `assistant_runs` can reconstruct the rejected answer or exact failed rule. Do not guess whether this was a numeric, citation, shape or preference failure, weaken validation to force acceptance, or call this a successful customer workflow. The provider observability page exposes aggregate performance/errors, not the application's rejection reason. A safe persisted validation-reason code is missing and needs follow-up work before a controlled retest.

The original November 24 accepted shopping run remains separate historical live evidence. The post-fix selected-vehicle answer and conversational budget update are **not live verified**. This rehearsal therefore does not establish full showcase readiness; earlier mocked tests remain separate evidence. No extra request was made to conceal or retry the failure.

### Real backup and cost

Private local backup: `~/Desktop/FrontDesk-AI-Rehearsal-2026-11-25/`. It contains `results.json`, `README.txt`, actual native PNG screenshots, observed UI evidence, independent SQL-result text and a SHA-256 manifest. Screenshots are genuine running-app captures, not recreated answers. Some owner screenshots include private draft wording; review before sharing. They are deliberately outside Git. No accepted customer transcript or successful follow-up screenshot exists for this rehearsal.

After these two requests the authenticated prepaid dashboard displayed **$4.97**, with automatic top-up still disabled and no new purchase. The two uncached-rate token estimates total approximately **$0.01969**; dashboard cents are not an exact invoice. The approved six-request conservative ceiling remains **$0.4376775** ($0.44 rounded) within the original $5 authorization. Do not spend the reserved class attempts on recovery. Keep the real failed request visible in System status and use the labeled backup for an honest presentation of current results.

## Earlier six-attempt preparation record — superseded by live results above

This section supersedes the earlier three-attempt allowance below. On November 25 the owner approved a lifetime cap of **16**, retaining the historical **10**: at most three rehearsal attempts, then three presentation attempts. The authenticated provider dashboard freshly displayed **$4.99** prepaid credit, one original $5 purchase and disabled automatic top-up. At the checked global short-context rates ($1.25/M input, $2.50/M output), the enforced 48,000-byte payload/1,800-token output bounds plus system instruction and 4,096 framing allowance give **$0.07294625/request × 6 = $0.4376775**, rounded reserve **$0.44**, within the original $5 authorization. No purchase or billing setting changed.

The local private `.env` now has `AI_CALL_LIMIT=16`; every other byte is unchanged. The observed running server (PID 62092, this checkout) still reports **10 used / 13 total**, drafting **Ready**, Auth ready and PostgreSQL connected. This is the successful earlier restart, not activation of 16. A new restart must load the cap and the provider-input fix described next. No rehearsal request has been sent in this follow-up; the three presentation requests remain unspent.

### Provider-input correction before rehearsal

`backend/shopping.py` → `suggest()` previously sent existing questions from the private `knowledge_state()['cards']`. It now takes `existing_questions` solely from `catalog()['knowledge']`, which reads the published snapshot. The private revision remains local for concurrency/staleness checks; private answers, unpublished question edits and inquiry contacts are excluded from provider input. This changes no stored business information or publication. A canary regression inspects the mocked provider payload: the published question is included and the private question/answer are absent.

The updated shopping suite passed **20 mocked-provider tests**; all **63 backend tests** passed; the production frontend build passed. Local frontend interaction tests cannot start because the existing `tsx` package entry is missing; no packages were installed. Earlier CI interaction tests remain historical mocked evidence, not a pass of this new live rehearsal. A first backend run suppressed logging and caused two logging assertions to fail; rerunning with normal logging passed all 63.

### Real rehearsal backup record — NOT YET EXECUTED

| Rehearsal action | Actual result / backup |
| --- | --- |
| Owner question suggestions | Pending restart; no new provider response, task or screenshot claimed |
| Find my fit with Compact Hatch + City Hybrid | Pending; no new answer or source references claimed |
| Follow-up changes $25,000 to $30,000, retains five seats/fuel economy | Pending; no live continuity result claimed |

After activation, refresh actual System status before proceeding. Use the exact three-request sequence below as rehearsal attempts 11–13. Inspect each answer and its durable `ai_tasks` / `assistant_runs` evidence, and save clearly labeled real-response screenshots and a transcript/evidence backup; do not substitute historical or mocked outputs. Stop after three attempts even if any fail. Inspect failures without automatic retries. Expected ending usage after three reservations is **13/16**, leaving **three presentation attempts**. Owner suggestion references can be empty because the output is questions; inspect its published input snapshot. Customer references must match current same-business publications. The existing historical shopping run remains distinct. Full semantic correctness, physical mobile behavior, separate AI comparison and fair-price behavior are not established by these tests.

Restart in the existing website Terminal after Ctrl+C:

```sh
cd '/Users/fatkhazizmukhamedov/Desktop/Gannon/7th semester/Senior Design/frontdesk-ai' && bash scripts/run-local.sh
```

The agent did not stop the server: automatic Terminal control was previously rejected and the command runner cannot bind loopback. No rejected Terminal-control attempt was repeated.

**Current live state:** http://127.0.0.1:8000/ is running in the user's existing Mac Terminal. Real owner sign-in, knowledge save/review/publication, private/public separation, six published vehicles, calculated comparisons, consented shopping inquiry submission/status and System status were verified in Safari. The server was not stopped or restarted; no dependency installation or migration was repeated in this follow-up.

Exactly one real Grok shopping request was sent after checking 9/10 attempts, the configured priced model, $5.00 rounded provider credit, disabled auto top-up and less than $0.01 prior spend across the original purchase period. The historical counter remains **10**, confirmed independently in System status and PostgreSQL. The owner subsequently approved a 13-attempt cap; its configuration and pending activation are documented below. No further AI request, retry, counter reset or purchase was made. Owner AI suggestions, another conversation turn, the separate AI comparison action and fair-price questions remain unverified live.

The real response extracted a $25,000 vehicle-price budget, five minimum seats and fuel-economy priority. It compared the fictional Compact Hatch and City Hybrid, returned six published price/seats/MPG references and a relevant follow-up, and identified missing ownership costs, reliability, safety ratings, accident history and taxes/fees. PostgreSQL confirmed 70 saved source entries, valid listing ownership/current publication revisions, and no private owner question or synthetic inquiry contact in that snapshot.

| Actual durable evidence | Recorded value |
| --- | --- |
| Business / operation | `demo-dealer` / `shopping_assistant` |
| AI task ID | `063167a2-f06a-49b4-910f-b2f0bd27e98a` |
| HTTP request ID | `0d0ab917-e36e-4824-9c0e-6ee447c8e52e` |
| Provider response ID | `53a7a876-83e0-427a-8bc5-0351d07f14a6` |
| Requested / reported model | Both `grok-4.20-0309-non-reasoning` |
| Tokens | 12,190 prompt + 473 completion = 12,663 total |
| Latency / outcomes | 5,463 ms; provider `succeeded`; application `accepted` |
| Tables / sources | Same-business `ai_tasks` ↔ `assistant_runs`; six cited listing field IDs at published revision 1, 70-entry snapshot |

The explicit **Approve this answer** action was verified live: saved knowledge revision 2 was reviewed and published. Editing the answer reset approval, and saved private revision 3 retained its review note while public revision 2 excluded that note. Only the factual explanation of the already-labeled fictional examples was published; no actual dealership policy was invented. The synthetic shopping inquiry `8a734eca-a7ed-4893-b8c9-b57a3a6134a1` retained the extracted preferences and both selected revision-1 vehicles. Its status changed Open → Pending and survived an inbox refresh; existing inquiries were unchanged.

Frontend fixes preserve selected IDs in Find my fit and separate inquiry activity from AI Thinking. Those paths have regression coverage; the sole real Grok response preceded the selected-ID fix, and a successful post-fix Grok response remains reserved for the presentation. [PR #4 CI](https://github.com/Fatkhaziz/frontdesk-ai/actions/runs/45531775835) passed 62 backend tests on Python 3.9/3.12, 11 frontend tests, the production build, disposable PostgreSQL and all three rendered mocked-Auth/Grok workflows. Automated results remain distinct from the live checks above.

This is the current fall scope following the November 24 discussion with Dr. Matovu. Demonstrate concrete AI use in one dealership: owner knowledge preparation, customer preference discovery, and explained vehicle comparison. The platform remains for small businesses. Additional business-domain completion is final-system work; existing salon/studio code is retained, not removed.

## Approved presentation allowance — configured, restart pending

The authenticated xAI billing dashboard now displays **$4.99 prepaid credit** (the provider UI's cents-level display), one original $5 purchase and auto top-up disabled. This is a fresh billing read, not a balance inferred from the attempt counter. The current global short-context price for the configured `grok-4.20-0309-non-reasoning` remains $1.25/M input tokens and $2.50/M output tokens; see [official pricing](https://docs.x.ai/developers/pricing). No purchase, billing-setting change or paid inference was made in this follow-up.

| Setting / bound | Before approval | Approved configuration |
| --- | --- | --- |
| Private `.env` `AI_CALL_LIMIT` | `10` | `13`; written locally, requires process restart |
| Historical `public.ai_budget.calls` | `10` | Retain `10`; increment normally for each new attempt |
| Additional attempts | None available | At most three, shared across all AI actions, including failures |
| Conservative input/output bound | 48,000-byte payload + system instruction + 4,096 framing-token allowance; 1,800 output tokens | Same bounds; same model/global endpoint; no tools or automatic retries |
| Conservative additional cost | No new inference charge in this follow-up | $0.07294625/request × 3 = **$0.21883875**; round reserve up to **$0.22** |
| Total spending authorization | Original $5 | Unchanged; existing prepaid credit only |

Exact approved local configuration change (every other byte and the file mode were preserved; credentials and certificate remain private):

```diff
-AI_CALL_LIMIT=10
+AI_CALL_LIMIT=13
```

This approved change does not reset/delete the counter, tasks, source snapshots, inquiries or prior response IDs. All three attempts are reserved for deliberate presentation actions; none are to be consumed by an automatic verification/retry loop. An unsuccessful attempt still uses an attempt. The estimate assumes the checked standard global model rates and enforced request bounds; provider billing is authoritative.

**Activation is pending, not verified:** the user explicitly authorized this change and restart after the fresh $4.99 credit check. The local `.env` now contains 13; the historical PostgreSQL counter remains 10 and there is still exactly one showcase run. `run-local.sh` loads `.env` into the process environment at startup; there is no runtime limit-update endpoint. The existing repository-owned server was preserved because the command runner cannot bind loopback (`PermissionError`) and automatic safety review rejected Terminal control. In the regular Mac Terminal running the project, press Ctrl+C and run `bash scripts/run-local.sh`. Then privately sign in and verify **System status → Refresh status** reports used 10, total 13 (three remaining). Until that observation, do not claim the allowance is active. The health endpoint returned `{"status":"running"}` before restart. No request was consumed to test activation.

### Unpaid browser evidence from the running application

- A new customer tab loaded the PR #4 bundle `index-4HDC96Ic.js`. With the Compact Hatch and City Hybrid selected, **Find my fit** submitted both correct `selected_ids` in its actual HTTP JSON payload. Safari Web Inspector showed the server response **429** with the configured-limit message. This confirms the post-fix browser payload/cap path, not a new Grok completion. The request fails before budget reservation/provider access; it does not add an AI task or replace the existing successful run.
- The real backend comparison returned $4,600 for those two examples and $6,000 after adding Utility AWD. Missing MPG/cargo remained “Not provided”. No AI action was used for either calculation.
- Safari Responsive Design Mode at **390×844** rendered the real local site: shopping navigation, collapsed/expandable requirements, chat controls, inventory and two-/three-vehicle comparison layouts. The comparison table is contained in its horizontal scroll region. This is browser viewport verification, not a physical iPhone test.
- The durable prior Grok run/model/IDs/usage remain the evidence listed above. The currently available browser initially contained the owner dashboard but no open customer-chat tab. Chat text is page memory and is not durably stored; do not claim that the original transcript can be reopened from the evidence record or replace it with a generated/mock response.
- A fresh owner knowledge request and inbox refresh returned **Invalid or expired sign-in**. An independent read-only query through the authenticated Supabase dashboard then confirmed current public r2/private r3 (the private note remains unpublished), the same Pending inquiry with its two vehicles/$25,000/five-seat preferences, ten calls, exactly one showcase run and the original model/request/task/provider IDs, 12,663 tokens, 5,463 ms, accepted outcome and six cited references. This verifies persistence without claiming that the expired application session was renewed. The current frontend disables automatic token refresh, so sign in shortly before presenting; a cached dashboard is not proof of a current authenticated route. Private application reauthentication is pending. No owner data was edited or republished during this follow-up.
- The earlier 62-backend/11-frontend/Chromium suites used mocked Auth/Grok. They are not evidence for a newly paid response, a renewed owner session or physical mobile behavior. No completed setup, migration, dependency installation or test suite was repeated for this documentation-only follow-up.

### Exact three-request presentation sequence

Privately sign in shortly before presenting; automatic token refresh is currently disabled. First verify **System status → Refresh status** shows 10 used / 13 total. Status refresh, inventory, calculated comparison and inquiry viewing are unpaid. Do not run verification scripts with execution enabled or click any other AI action.

1. **Request 11 — Owner knowledge → Suggest customer questions with AI**, once. Inspect the actual suggested questions; answers must come from the owner. Save privately if retaining the questions before navigating away. Do not publish the private review note or invent business policies. This will be the first live verification of owner suggestions; it has only mocked coverage so far.
2. **Request 12 — Listings → Open customer inventory** (`/shop/demo-dealer`). Select the fictional **Compact Hatch** and **City Hybrid**, then **Find my fit**. Send once: “My vehicle-price budget is $25,000. I need at least 5 seats for daily commuting and prefer fuel economy. Compare my selected fictional vehicles using only their published facts, explain missing information, and ask one useful follow-up.” Inspect extracted preferences, selected vehicles, actual answer, missing information and published source references. The earlier shopping request genuinely reached Grok; the selected-ID fix has unpaid browser payload verification but no successful post-fix Grok response yet.
3. **Request 13 — Reply to the actual follow-up**, incorporating: “I prefer the higher fuel economy. I can raise my vehicle-price budget to $30,000; keep my minimum at 5 seats. Which selected option fits best now, and what still needs staff confirmation?” Inspect whether the new budget replaces the earlier budget, other requirements persist, and references match published facts. This will be the first live second-turn/change-of-requirements check. Keep the customer tab open; the transcript is page memory.
4. **Unpaid evidence — System status → Refresh status → Latest showcase AI requests → Published source evidence.** Inspect the three new rows, without substituting the earlier run: actual operation/timestamp, model, HTTP request ID, AI task ID, provider response ID, token usage, latency, provider outcome, application outcome and source snapshot/revision. Owner suggestions return questions rather than factual answers, so an empty returned `source_ids` is expected; inspect their published input snapshot. Customer responses must show their approved cited references. The original real run remains a separate historical record. Expected final count is 13/13.

A failed attempt also consumes an attempt: stop and inspect its recorded outcome; do not retry automatically or add a fourth request. The separate **Explain this comparison with AI** and fair-price questions are outside this allowance and remain unverified live. No successful outcome is promised before inspecting the real result. Prompts and validation do not guarantee semantic correctness.

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

The owner approved **13 total attempts**, retaining the historical ten. The private setting is written but process activation/status verification is pending as described above. All three remaining requests are reserved for the exact presentation sequence; no automated paid verification, counter reset, further cap increase, purchase or top-up is authorized. Remaining credit does not authorize a fourth attempt. `python -m scripts.verify_showcase_live --business demo-dealer` is read-only without its explicit execution option; do not use the execution option during preparation.

Before the sole live request, the xAI dashboard showed $5.00 rounded credit, one original $5 purchase, disabled auto top-up and less than $0.01 spend for the period covering that purchase. Current published global short-context prices for `grok-4.20-0309-non-reasoning` were checked at https://docs.x.ai/developers/pricing: $1.25/M input and $2.50/M output. The 48,000-byte payload and 1,800-token output bounds gave a conservative CLI ceiling of $0.07294625. The observed token counts imply an uncached-rate estimate of $0.01642; this is not an invoice or a claim about the exact post-call balance. The original total $5 authorization was preserved.

## Presenter sequence

Use the exact three-request sequence above after activation is visibly verified. Surround those requests with the already verified unpaid inventory/comparison, private/public knowledge and Pending inquiry views. Clearly introduce the existing run as historical evidence, and the new owner suggestions and conversational follow-up as first live demonstrations. Keep the customer tab open to retain its actual transcript.

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

### Setup history and remaining limits

- PR #2's main commit `59ac213859808ab38ec8dc6d3aba27c1f9ac7862` was safely integrated through the GitHub connector with hash-verified Git objects when shell DNS failed. Existing branches and private configuration/certificates were preserved; no `AGENTS.md` was present in the ancestors or current repository tree.
- PR #3 fixed Python 3.9 nullable-annotation imports and recorded requested versus returned model evidence. Local 62-test backend regressions and the frontend production build passed. Full local frontend tests lacked cached dependencies; complete suites passed in CI. Those isolated SQLite/mock-provider results were never described as live Grok checks.
- Additive migration 005 was applied once in the existing Supabase dashboard under the advisory lock, after reviewing 001–004 checksums. Its exact checksum, table/column contracts, 19 foreign keys and zero anon/authenticated grants on new tables were verified. The same four deterministic fictional examples as `seed_showcase.py` were added. A single transaction required every pre-existing row across 12 application tables to remain unchanged or roll back. No migration/dependency setup was repeated in this browser continuation.
- The earlier managed-runner DNS/loopback restriction and Terminal-control rejection blocked automated startup during PR #3. The user subsequently started the real server in ordinary Mac Terminal. The current live sign-in/browser/database results above supersede that earlier startup/login blocker. The server and real customer-response tab were left running.
- The real response cited price/seats/MPG. Its body-style/cargo facts existed in the approved catalog snapshot but were not all included in its six cited field IDs. Numeric catalog checks and source-ID ownership are not a complete claim-to-citation proof; prose relevance, completeness and general semantic correctness still require review. Prompts do not guarantee correctness.
- Live owner AI generation, additional conversation turns, the separate AI-comparison action and fair-price questions remain blocked by 10/10. The selected-ID fix and inquiry activity separation are covered by automated regressions. A later unpaid capped HTTP request also confirmed the selected-ID payload; no second paid post-fix AI check was attempted. Current listing edit/delete and owner mobile workflows have rendered mocked-service regression coverage, not new real-data verification. Public shopping mobile layout was subsequently inspected against the real site at 390×844 in Safari Responsive Design Mode. No existing listing was edited/deleted for this check.

The running dashboard is **http://127.0.0.1:8000/** and inventory is **http://127.0.0.1:8000/shop/demo-dealer**. Keep the user's existing server terminal open. For a later restart after it is stopped, run `bash scripts/run-local.sh` from the configured checkout. No new download, credentials reset, database reset or Codex session is required. A full dashboard refresh requires private sign-in again because the current frontend keeps the Auth session in memory.

## Offline fallback

Build first, then run `python -m scripts.rehearse`. Open `http://127.0.0.1:8002/`, sign in with `owner-motors@example.invalid` / `rehearsal`, and open the customer inventory. Synthetic data and simulated sign-in are clearly labeled; AI is disabled. This demonstrates interface and factual comparison if network/provider access fails. It is not a substitute for showing a previously verified real API record or for declaring the AI acceptance complete.

## Not included in this release

No appointment reservation, phone receptionist, payments, external inventory/market scraping, autonomous changes, model training, full production hosting or verified cross-industry deployment. Existing cross-industry architecture is preserved for later work. Presentation scope is the dealership workflow above, not a claim that the full small-business platform is complete.
