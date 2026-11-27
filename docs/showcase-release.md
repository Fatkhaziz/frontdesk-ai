# FrontDesk AI current showcase and acceptance guide

Current as of November 26, 2026. Workspace 2 and validation version 6 delivery update: [update notes](workspace-2-update.md). This replaces historical capped-attempt handoffs.

FrontDesk AI Practice, Showcase and Technical Evidence Guide

CIS 457 Senior Design I | November 26, 2026

Fatkhaziz Mukhamedov, Al Baraa Khaled, Mohammad Abdullah, Amar Al Balkhi

Use this guide to practice the website and explain the actual code, database and provider request. It is separate from the report submitted to faculty. Current code and evidence baseline: November 26, 2026.

## 1 Start the updated website — one launch command

First, use GitHub Desktop to fetch origin and pull main after the release PR is merged. Keep your existing configured frontdesk-ai checkout. Do not clone a second copy or copy private credentials into this document. The existing Mac folder is Desktop/Gannon/7th semester/Senior Design/frontdesk-ai.

Open the Terminal tab that is currently running the website. Click inside it and press Control and C together once to stop that server. This is Control, not Command. Wait until the prompt ending with % or $ returns. Leave the Codex conversation tab alone.

Paste these two lines into that same Terminal, then press Return:

cd "$HOME/Desktop/Gannon/7th semester/Senior Design/frontdesk-ai"
bash scripts/launch-showcase.sh

The script loads the existing private configuration, checks Auth/database connectivity, applies pending migration 006, preserves existing records and usage, builds the website and starts the app. It makes no AI inference during launch. Keep this Terminal open. If it reports a migration/configuration error, stop there and retain the safe error category; do not paste credentials into chat or reset the database.

Open Safari. Click the address bar once, type http://127.0.0.1:8000/ and press Return. Sign in privately with the existing owner email/password. Click System status and Refresh status. Check Auth ready, PostgreSQL connected, validation version 6 in Technical API diagnostics, and the practice-budget panel. The historical attempt count should remain at its real value; it must not reset to zero.

The attempt guard is now 200; it is not 200 free calls. A shared conservative ledger caps preparation at $1.00 of the owner-declared $4.97 allowance and preserves at least $3.50 while preparation mode is active. Failed attempts remain reserved. The provider’s actual remaining credit must be checked separately at https://console.x.ai/. No top-up, purchase or automatic retry is enabled by this launcher.

## 2 Open the two pages you need

Stay in the signed-in owner page. Click Listings in the top navigation, then click Open customer inventory at the top right. That link opens a second Safari tab. The first tab is your owner dashboard; the new tab is the customer inventory for the same business. You do not need a private window or repeated keyboard shortcuts to practice this workflow.

Use the visible business-specific link rather than guessing an ID. The previously configured customer URL was http://127.0.0.1:8000/shop/demo-dealer/; if the current link uses a different ID, use the link from your dashboard. The sample Compact Hatch and City Hybrid records are explicitly fictional showcase examples.

## 3 Perform the real AI acceptance check before class

Version 6 asks the model to insert approved values through short source references; the server supplies the exact listing quantities. Normal accepted output is labeled an AI explanation. If numeric wording cannot be verified but the structured needs, source scope and recommendations passed checks, ALL model prose is discarded and a confirmed listing summary is displayed. Its evidence is `accepted_with_limits`, retaining the original safe rejection category and canonical source IDs. This is useful limited delivery, not proof that the model explanation passed. Invalid preferences, foreign references, stale publications and provider failures remain blocked. No second paid request is made automatically.

Optional automated real check: launch with bash scripts/launch-showcase.sh --practice --verify-live. This sends up to three actual synthetic shopping requests (needs, budget change and fair-price), stops at the first rejection without retry, and saves accepted responses plus private raw diagnostics under Desktop/FrontDesk-AI-Live-Acceptance. It uses the same protected allowance. It does not test browser password sign-in. The default launch without --verify-live sends no inference. After this check, use the manual steps below to practice the interface and the owner question feature.

## Owner questions — one paid request

Do: Owner tab → Owner knowledge → Suggest customer questions with AI. Click once and wait. Review whether the suggestions concern the published business/inventory. Save private knowledge if useful. Do not publish an invented answer.

Check: A real response is visible; System status records knowledge_suggestions with provider succeeded and application accepted.

## Compare — no AI charge

Do: Customer tab → Inventory. Tick Compare this vehicle for Compact Hatch and City Hybrid. Click Compare selected. Read the listed prices, seats, MPG and missing values.

Check: The table shows the same selected published vehicles and exact price difference. Private edits do not appear.

## Natural needs — one paid request

Do: Click Find my fit. In Your message enter: “My vehicle-price budget is $25,000. I need five seats for commuting and prefer fuel economy. Compare my selected vehicles, explain missing information and ask one useful follow-up.” Click Send to AI once.

Check: A response is accepted. The visible budget is 25000 and minimum seats is 5. The answer cites relevant published sources and does not silently relax hard requirements.

## Follow-up — one paid request

Do: Answer the actual follow-up and add: “Raise my vehicle-price budget to $30,000 and retain five seats. Which selected option fits my priorities better now?” Click Send to AI once.

Check: The budget becomes 30000, the seat requirement remains 5, and the answer concerns the selected vehicles. Earlier accepted context is preserved.

## Fair-price question — one paid request

Do: Enter: “Is this a fair price? Explain what you can verify and what information you would still need.” Click Send to AI once.

Check: It discusses supported asking-price/specification/budget trade-offs and explains missing market/condition/fee evidence; it does not invent a verified appraisal.

## Save actual conversation — no AI charge

Do: Click Save conversation in the chat tools. Keep the downloaded JSON with your private rehearsal evidence.

Check: The file contains the accepted messages, source details and IDs from this tab. It is an actual export, not a reconstruction of earlier lost text.

## Verify durable evidence — no AI charge

Do: Owner tab → System status → Refresh status → Latest showcase AI requests. Expand Published source evidence for each new run.

Check: Match the operation/time and request/task/provider IDs. Provider succeeded and application accepted must both be present for a successful answer.

These are four deliberate preparation requests, with no automatic retries. The application reserves a conservative ceiling before each. The actual response text may vary, so inspect outcomes rather than expecting a memorized sentence. If a request fails, capture the request ID and saved rejection stage/reason from System status. Do not keep pressing Send or label a provider completion as a working conversation. The latest code was automatically tested here; these live checks still need the configured Mac.

## 4 Practice every implemented feature

| Feature | Practice action and expected behavior | Cost / caution |

| --- | --- | --- |

| Sign-in and access | Sign in with owner; confirm dashboard loads. Sign out; protected actions must require sign-in. A staff account, if one is configured, must not publish or view owner-only diagnostics. | No paid call |

| Find saved listings | Listings → Find a vehicle; search make/model/year. Use Show to filter Published or Private drafts. Clear the search to restore the list. | No paid call |

| Create a throwaway listing | + New listing → enter clearly fictional facts, year, price in dollars and mileage. Save vehicle details. Fill a description manually and Save description. | No paid call unless Generate with Grok is chosen |

| Optional AI description | Use Generate with Grok only when you deliberately want to verify that legacy feature; inspect/edit the wording before saving. | One additional paid request |

| Publish and private isolation | Open Review and publish, read the saved revision, tick the approval checkbox and Publish approved revision. View public page. Change the private price and save; reload public page and verify the approved price remains. | No paid call |

| Unpublish / delete | For the throwaway listing, expand Listing management. Unpublish hides it publicly. Delete listing opens a confirmation. Delete only the throwaway record you created for this test. | No paid call; deletion is permanent after confirmation |

| Owner knowledge | Add a question manually; enter a true answer/source note or route to staff. Save private knowledge; confirm public knowledge unchanged until owner publication. | Manual editing is free; Suggest customer questions with AI is paid |

| Customer comparison | Select two and then three published vehicles. Compare selected. Check missing values and units. Remove one or Clear selection. | No paid call |

| Requirements and AI explanation | Adjust vehicle-price versus total-cost budget; ask natural needs/follow-up; inspect sources. Explain this comparison with AI is another explicit paid action. | One request per send/explanation |

| Consented staff inquiry | Ask staff to follow up → review summary → synthetic contact class-test@example.invalid → consent → Send inquiry to staff. In owner Inquiries, refresh, expand context and set Pending; refresh again. | No paid call; status persists |

| Business settings | Inspect the existing private/public profile and service intake. Save only truthful intended changes. Other-domain templates are supporting fixtures, not claims of live salon/studio onboarding. | No paid call |

| Status and export | Refresh status, expand request sources/diagnostics and run read-only evidence SQL. Save actual conversation before closing/refreshing its tab. | No paid call |

## 5 What to show when they ask technical questions

| Question | Exactly where to open | What to explain |

| --- | --- | --- |

| Where is the latest Grok call? | Owner System status → Latest showcase AI requests; Supabase public.assistant_runs joined to public.ai_tasks. | A completion is not an inquiry. Match time, request_id, task_id and provider_response_id, plus tokens/latency and both outcomes. |

| Show me the API call in code | GitHub → backend/showcase_ai.py → provider_call. | Point to client.post and https://api.x.ai/v1/chat/completions. The key comes from server environment; do not show its value. |

| What happens before/after the call? | backend/shopping.py → assist / validate_answer; backend/showcase_ai.py → run_ai. | Before: resolve published context and reserve usage. After: validate schema, explicit constraints, citations, numeric claims and current publication; then display or reject. |

| Where is the password in the database? | Supabase SQL Editor → run Password evidence in the supplied SQL file. Database schema auth → users → encrypted_password. | The column holds a salted bcrypt hash for password accounts. Authentication → Users shows accounts. memberships holds authorization, not passwords. |

| Where is business data stored? | Supabase Table Editor → public → listings, business_profiles, dealer_knowledge and the inquiry tables. | Data is in the managed project’s PostgreSQL service; the Mac hosts application code for this demo. Confirm the project’s configured region in its infrastructure/settings; do not guess its physical location. |

| Why is ai_interaction_evidence empty? | Check the actual route. New shopping/owner-question runs use assistant_runs. | The earlier business-profile Q&A route uses ai_interaction_evidence. Empty rows are not proof that the newer route did or did not run. |

| Is it using RLS/MFA? | migrations/001–006; backend/main.py identity and owner. | Current browser table grants are revoked and backend scopes SQL. RLS policies, enforced privileged MFA and production least-privilege credentials remain planned hardening. |

| Is this local AI or an agent? | Architecture diagram and actual HTTPS call. | The application server is local now; managed Auth/data and Grok are remote. Agent behavior concerns authorized actions/autonomy, not whether a model is local. This model cannot autonomously write records. |

| What happens if Grok is unavailable? | Show factual comparison and a recorded failed outcome. | No fabricated response or automatic paid retry. The customer can compare known facts or explicitly contact staff. A mock rehearsal must be labeled. |

| Does it send staff an email? | Inquiries and source code, not a provider notification dashboard. | The current workflow persists staff work. A delivered email/SMS is a different integration and is not yet claimed. |

## 6 The short website script you can read aloud

## Owner knowledge

“AI helps the owner prepare for questions they may not have thought of. The owner supplies the true answers and decides what is approved.”

## Comparison

“These are the published facts for the selected vehicles. The server calculates the price difference. Missing information stays missing.”

## Personalization

“The customer can describe a budget, passenger needs and driving routine naturally. Grok interprets that request and explains the trade-offs. Our backend checks the requirements and sources.”

## Follow-up

“I can change the budget without starting over. The accepted requirements update, and the answer still concerns these selected vehicles.”

## Unknowns

“For a fair-price question, it can explain known asking prices and features. A verified market valuation still needs condition and comparable-sale evidence.”

## Handoff

“If a person is needed, the customer approves a separate staff request. It includes the selected vehicles and requirements. Chatting alone does not create a lead.”

## Proof

“Here is the actual request: our HTTP ID, task ID, provider response ID, time, tokens and source revision. Provider completion and application acceptance are separate.”

## 7 Full team presentation timing and notes

The deck has 20 main slides timed to 20 minutes, plus four backup slides for the five-minute Q&A. Suggested speaking assignments are preparation assignments, not retroactive implementation credit. Each member should review and understand their material before presenting. Export an actual PPTX copy from the presentation’s menu for Blackboard; the assignment explicitly rejects submitting only a link.

| Slide | Title | Suggested speaker | Time |

| --- | --- | --- | --- |

| 1 | FrontDesk AI — Fall Release 1 | Fatkhaziz | 0:30 |

| 2 | The problem is incomplete information and intake | Amar | 0:45 |

| 3 | Requirements come from identifiable sources | Al Baraa | 0:45 |

| 4 | Fall scope and final scope are different | Amar | 0:45 |

| 5 | The fall acceptance goals are specific | Amar | 0:45 |

| 6 | The architecture separates interface, authority and inference | Al Baraa | 1:30 |

| 7 | A private edit is not a public change | Al Baraa | 0:45 |

| 8 | Website: prepare the owner’s knowledge | Fatkhaziz | 1:00 |

| 9 | Website: understand needs, compare and refine | Fatkhaziz | 3:30 |

| 10 | Website: staff receive an explicit request | Fatkhaziz | 0:45 |

| 11 | Show the actual server-side API call | Al Baraa | 1:00 |

| 12 | Trace one request through three identifiers | Mohammad | 1:15 |

| 13 | Show the password location, without exposing a hash | Mohammad | 1:00 |

| 14 | Security controls have clear limits | Mohammad | 1:00 |

| 15 | Verification separates code from real service behavior | Amar | 0:45 |

| 16 | Current status and release gate | Fatkhaziz | 0:45 |

| 17 | Completion plan preserves the full faculty scope | Al Baraa | 1:15 |

| 18 | Responsibilities must produce reviewable artifacts | Fatkhaziz | 0:45 |

| 19 | AI assistance does not transfer responsibility | Mohammad | 0:45 |

| 20 | What this release demonstrates | Fatkhaziz | 0:30 |

| Total | Main presentation |  | 20:00 |

| Q&A | Four backup slides | All members | 5:00 |

## 1. FrontDesk AI — Fall Release 1

Our fall release connects owner preparation, approved business information, vehicle comparison and an AI shopping conversation. I will show the website, while the team explains the design and evidence. The final system remains a small-business platform; this milestone uses a dealership to demonstrate a concrete AI workflow. The report is dated November 26 and distinguishes implemented code, real-provider evidence and spring work.

## 2. The problem is incomplete information and intake

The owner’s problem is repeated intake, not simply a missing chatbot. The customer may describe a commute, passenger needs and a budget rather than ask for a specific specification. Staff then need the unresolved question and those requirements together. Our early empathy map identified missed inquiries, after-hours gaps and workload. These are design findings and hypotheses; we have not measured a revenue increase or a percentage reduction in missed calls. Present this as a review of the problem, not a claim that I implemented the application.

## 3. Requirements come from identifiable sources

Our earlier requirements record identifies Anwar El Daour at Universal Motors Group and records an October 4 interview conducted by me. It describes missed calls, repeated service and sales questions, paper scheduling and cost concerns. The professors’ annotated requirements require multiple business domains and more complete operations in the final system. The later discussion with Dr. Matovu focuses this fall release on a dealership and a more useful AI feature. Salon and studio examples are evaluation scenarios, not additional interviewed businesses.

## 4. Fall scope and final scope are different

The 20 percent milestone is a working vertical slice, not a claim that 20 percent of code lines or tests are complete. The fall workflow is deep enough to show a real business-information lifecycle and a customer decision process. The full requirements retain the additional domains, roles, bookings and dealership operations requested by faculty. We identify these as planned work instead of describing every requirement as already implemented.

## 5. The fall acceptance goals are specific

The updated specification adds stable IDs for the owner question workflow and personalized shopping. Acceptance is observable: a private answer must remain private until approval, selected vehicles must be the ones sent in the request, a changed budget must update accepted preferences, and the resulting task must be inspectable. We also test unknown facts and safe failures. These checks give us a clear definition of success beyond a visually convincing answer.

## 6. The architecture separates interface, authority and inference

The browser runs React and TypeScript. FastAPI handles authority, validation and application rules. Supabase Auth verifies identities; managed PostgreSQL stores application data. The FastAPI server sends paid requests to xAI using a private server key. Grok runs remotely, even though the demo’s application server currently runs on a Mac. A future hosted service replaces that Mac; users do not need a local language model. The backend remains responsible for publication, permissions, arithmetic and all database writes. The planned worker is for durable notifications, retention and synchronization. It is not currently a running completed feature. The implementation uses direct Psycopg SQL and versioned SQL files; earlier ORM/Alembic proposals are not the current code.

## 7. A private edit is not a public change

For example, if a published price is $23,500 and we save a private change to $24,500, customers still receive the approved $23,500 until republication. The approval request includes the expected saved revision, so a concurrent edit requires fresh review. The same principle applies to owner knowledge. An AI suggestion cannot approve or publish itself. This is one concrete place where business authority stays with a person.

## 8. Website: prepare the owner’s knowledge

Switch to the owner tab. Click Owner knowledge. During rehearsal, generate once and inspect the questions; during class, use the saved result or send one explicit live request if the budget and acceptance check are ready. Explain: AI helps an owner think of questions they may not have anticipated, but it does not invent official answers. Show the private and public revision numbers. Use a verified answer or a staff route; do not publish a fictional policy as a real business commitment. Return to slides only after the next two website steps.

## 9. Website: understand needs, compare and refine

In Listings click Open customer inventory; it opens a second tab. Select the two explicitly fictional vehicles with Compare this vehicle. Click Compare selected to show the table and deterministic price difference; this makes no paid call. Click Find my fit and send the stated request once. Wait, then point to the visible budget and seats. Expand Sources used and identify a published vehicle field/revision. Answer its actual follow-up or explicitly raise the vehicle-price budget to $30,000 while retaining the other needs. Explain that the model interprets the request and writes the explanation; the backend rechecks eligibility and arithmetic. If asked whether a price is fair, ask that as an additional deliberate turn: the assistant can discuss known price/budget/specification trade-offs, but cannot establish market value without comparable sales and condition evidence. Do not promise a particular phrase or a specific best vehicle in advance. Save conversation after an accepted real response. If a request fails, say it was not accepted and show the recorded category; do not present a screenshot of a mock as live success.

## 10. Website: staff receive an explicit request

The contact form is separate from AI chat. Submit only after showing what is being sent and confirming consent. In the owner inbox, refresh and expand the customer requirements and selected vehicles, then set the status to Pending. Explain that the database save and a notification are separate outcomes; this release does not claim an email or SMS was delivered. A normal answered chat does not automatically become a sales lead.

## 11. Show the actual server-side API call

Open backend/showcase_ai.py at provider_call in GitHub. Point to client.post and the exact HTTPS URL. The request includes a configured model, system instructions, a JSON user payload, maximum output tokens and JSON response mode. The Authorization value comes from a private environment variable; do not open or reveal its value. The browser posts to our FastAPI endpoint, not directly to xAI. A JSON response is still untrusted data. After it arrives, we validate shape, source membership, explicit preference changes, hard constraints and allowed numeric facts, then recheck that the published data has not changed.

## 12. Trace one request through three identifiers

In System status click Refresh status and open Latest showcase AI requests. Pick the actual accepted classroom or rehearsal request, not merely a historical successful provider status. In Supabase SQL Editor run the supplied read-only latest-showcase query. Match task_id between ai_tasks.id and assistant_runs.task_id, and match request_id with the browser response header. Provider succeeded means a completion came back; application accepted means our validation passed. A failed application outcome is not a successful conversation. ai_interaction_evidence is for the earlier business-profile Q&A route; inquiries are customer work and do not prove an API call. An empty evidence table may simply be the wrong route or no calls yet.

## 13. Show the password location, without exposing a hash

The user account belongs to Supabase Auth. For password-based users, the encrypted_password column stores a salted bcrypt hash, not a readable password. Memberships maps the verified user subject to a business, role and active state. It is not the password table. In SQL Editor run the supplied query that selects the account ID, whether a hash is present, its format prefix and length. Do not display the full hash. Authentication Users shows accounts, while Auth audit/login evidence is a different question from a paid xAI call. The app validates tokens with managed Auth and separately checks membership for business access. Source: Supabase password-security documentation.

## 14. Security controls have clear limits

Our threat model covers spoofing, tampering, repudiation, disclosure, denial of service and privilege escalation. Current controls include active membership checks, private/public revisions, explicit staff submission and safe correlation metadata. Direct application-table grants to browser API roles are revoked; the current migrations do not enable RLS, so we do not claim they do. Spending reservations protect the declared presentation allowance. Remaining hardening includes enforced privileged MFA, dedicated database privileges, scheduled retention and public-endpoint throttling. These limitations are part of the release plan rather than hidden behind a security label.

## 15. Verification separates code from real service behavior

The automated checks cover application logic and rendered interaction, and the database check uses an actual disposable PostgreSQL instance. They intentionally avoid spending real AI credit. The configured Mac must still verify this latest code against the actual owner account and provider. We should show actual saved request evidence and a real accepted response when calling a feature live verified. The relevant CI run and code revision are linked in the guide. I am presenting the acceptance review, not claiming I authored all of these tests.

## 16. Current status and release gate

This status is the honest November 26 baseline. Earlier real-provider runs prove that the integration reaches Grok, and owner suggestions succeeded, but later customer responses were rejected by application validation. The new fixes pass regressions and CI; we must load them and record accepted real turns before calling that repair live verified. Before presenting, replace this status with the actual outcome and IDs if the live check has passed. Do not replace the status merely because the server started or a test used a mock.

## 17. Completion plan preserves the full faculty scope

The proposed spring sequence starts with platform and business permissions plus resource scheduling. That foundation supports a vehicle and salesperson test drive, a salon stylist and chair, and a studio photographer and room. Then we add dealership operational cases, voice, notifications, retention and sandbox subscriptions. The final release is evaluated across all three domains, with concurrency, accessibility, answer quality and recovery evidence. Exact dates depend on the spring syllabus; the plan uses weeks one to five, six to ten and eleven to fourteen rather than inventing course release dates.

## 18. Responsibilities must produce reviewable artifacts

I led the feasibility demo and most recent implementation/integration. Al Baraa led initial design and worked with me on detailed design. Recent implementation contribution from Amar and Mohammad was limited, so we should not assign them retroactive code credit. The spring plan gives each person a named artifact and acceptance gate. The suggested speaking roles are preparation assignments; each member must review and be able to explain the material they present. Documentation, tests and a short demonstration will establish completion.

## 19. AI assistance does not transfer responsibility

Jim Buchanan’s presentation focused on human accountability when AI produces work. Our owner approval model and request evidence support that responsibility, but they do not remove the need for judgment. We must report failed tests honestly, protect contacts and avoid unverified safety, warranty or market-value claims. The same standard applies to our use of AI coding and drafting tools: we remain responsible for reviewing the code, citing sources and accurately attributing contributions. Sources: supplied Buchanan slides; ACM 2018 and IEEE June 2020 ethics codes.

## 20. What this release demonstrates

This release demonstrates a complete information path: owner preparation and approval, customer needs and comparison, a deliberate staff request and inspectable AI evidence. We distinguish implemented code from live acceptance and final-system plans. We are ready to trace a specific request or record rather than make broad claims about an AI label. We have set aside five minutes for questions.

## 21. Backup: data locations in Supabase

Open the project’s Table Editor and keep public selected for application tables. Switch to auth only to inspect managed identity safely. schema_migrations contains upgrade filenames/checksums, not API calls. ai_budget.calls counts attempts, not dollars; ai_spend tables hold conservative reservations, not the provider’s authoritative wallet.

## 22. Backup: fair-price and unknown-fact questions

Say: We can explain how the listed price and documented features relate to this customer’s needs. We do not have a verified market-comparison or vehicle-condition feed, so we cannot certify that the asking price is fair market value. We would need approved comparable sales, location, condition/history and fees before making that claim. The assistant should make that distinction while still helping with the known trade-offs.

## 23. Backup: local hosting and an AI agent

This implementation is an AI-assisted web application with controlled workflows. The model interprets and explains but cannot autonomously publish, book or write SQL. Calling an agent local-only is not a useful technical definition. The meaningful design question is what actions it can take, with what authority, confirmation and evidence. We can later add tightly authorized workflow tools without moving the model onto a customer device.

## 24. Backup: sources and technical references

Full URLs and access dates are in the report and individual submission. The sources explain external technologies and frameworks. Implementation evidence comes from the repository and actual test/request records, not from a provider’s marketing page. Formal compliance or production readiness is not claimed.

## 8 Presentation-day launch and backup

Before class, verify current provider credit and close unrelated sensitive tabs. Stop the practice server with Control+C. In the configured project folder run bash scripts/launch-showcase.sh --presentation. This explicitly changes the existing ledger’s phase; it does not reset historical attempts, reset reservations or buy credit. Sign in privately and confirm System status. Keep the server Terminal open and prevent the laptop sleeping during the presentation.

Keep the owner tab, customer tab, System status, supplied SQL queries, GitHub provider_call code and the exported slides ready. Open the actual accepted response and its matching evidence before class. Save local screenshots of the real response and evidence without passwords or personal contacts. The downloaded conversation is useful rehearsal backup; it is not substituted for live success.

If the network fails, state the failure plainly, show the factual comparison and previously captured real request evidence, and continue with the architecture. The isolated rehearsal can show interface behavior with synthetic data but must not be represented as a live Grok call. Do not claim a failed or unaccepted request worked.

## 9 Deadlines and remaining submission checks

| When | Action |

| --- | --- |

| November 26–27 | Load the merged code on the configured Mac and complete the four real AI acceptance actions. Record accepted outputs and request IDs. Update the report/slide status only from those results. |

| November 28–December 4 | Practice the complete feature checklist. Al Baraa reviews architecture/elicitation; Amar reviews acceptance cases; Mohammad reviews data/security/API evidence. Keep changes away from working main until reviewed. |

| December 5–10 | Freeze the report/slides, rehearse all four speakers, verify professor collaborator access and update actual December team contributions. |

| December 11 by 11:59 p.m. Eastern | One team member uploads the report and a file copy of the presentation to their respective team dropboxes. Check Blackboard’s submission receipt. |

| December 12 by 11:59 p.m. Eastern | Submit the individual ethics/reflection/assessment file after adding December observations. Do not submit an assessment dated through November 26 as if it covered future work. |

Faculty collaborator requirement: check GitHub repository Settings → Collaborators for tang002@gannon.edu and matovu001@gannon.edu. Invite their actual GitHub accounts and verify acceptance. No collaborator access is claimed merely because the repository is public. The GitHub connector available for this work does not expose an invitation action; account-level completion must be verified in the repository settings.

The attached individual assessment has completed current ratings and the adopted rubric, but it cannot truthfully assess December work before December occurs. The report and slides likewise state the current live gate instead of inventing a passed retest. These are the factual items to update before the deadline; no new design document is needed merely to change a verified status/date.

## References

[1] FrontDesk AI team, source repository and revision history. https://github.com/Fatkhaziz/frontdesk-ai Accessed November 26, 2026.

[7] Supabase, Password security. https://supabase.com/docs/guides/auth/password-security Accessed November 26, 2026.

[8] xAI, Chat Completions API and structured outputs. https://docs.x.ai/developers/model-capabilities/text/structured-outputs Accessed November 26, 2026.

[9] xAI, API pricing, configured non-reasoning model. https://docs.x.ai/developers/pricing Accessed November 26, 2026.
