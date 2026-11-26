# FrontDesk AI End-of-Semester Presentation

20 minutes plus five minutes Q&A. Native deck: https://chatgpt.com/space/page_1d9251afc0c88191932865b643c87aab

Status as of November 26, 2026. Export an actual PPTX for submission.

## 1. FrontDesk AI — Fall Release 1

Speaker: Fatkhaziz; seconds: 30

- Owner-approved knowledge and a personalized shopping conversation

- Fall showcase: dealership • Final platform: multiple small-business domains

- Fatkhaziz Mukhamedov • Al Baraa Khaled • Mohammad Abdullah • Amar Al Balkhi

Our fall release connects owner preparation, approved business information, vehicle comparison and an AI shopping conversation. I will show the website, while the team explains the design and evidence. The final system remains a small-business platform; this milestone uses a dealership to demonstrate a concrete AI workflow. The report is dated November 26 and distinguishes implemented code, real-provider evidence and spring work.

## 2. The problem is incomplete information and intake

Speaker: Amar; seconds: 45

- Owners repeat answers and lose context across calls and messages.

- Customers know their budget and use case, but may not know which listing fits.

- Staff need the customer’s question, requirements and selected options together.

The owner’s problem is repeated intake, not simply a missing chatbot. The customer may describe a commute, passenger needs and a budget rather than ask for a specific specification. Staff then need the unresolved question and those requirements together. Our early empathy map identified missed inquiries, after-hours gaps and workload. These are design findings and hypotheses; we have not measured a revenue increase or a percentage reduction in missed calls. Present this as a review of the problem, not a claim that I implemented the application.

## 3. Requirements come from identifiable sources

Speaker: Al Baraa; seconds: 45

- Recorded stakeholder: Anwar El Daour, owner, Universal Motors Group.

- Earlier notes record Al Baraa’s October 4 interview about calls, scheduling and cost.

- Faculty feedback expands the final scope; Matovu’s November 24 discussion prioritizes concrete AI for fall.

Our earlier requirements record identifies Anwar El Daour at Universal Motors Group and records an October 4 interview conducted by me. It describes missed calls, repeated service and sales questions, paper scheduling and cost concerns. The professors’ annotated requirements require multiple business domains and more complete operations in the final system. The later discussion with Dr. Matovu focuses this fall release on a dealership and a more useful AI feature. Salon and studio examples are evaluation scenarios, not additional interviewed businesses.

## 4. Fall scope and final scope are different

Speaker: Amar; seconds: 45

The 20 percent milestone is a working vertical slice, not a claim that 20 percent of code lines or tests are complete. The fall workflow is deep enough to show a real business-information lifecycle and a customer decision process. The full requirements retain the additional domains, roles, bookings and dealership operations requested by faculty. We identify these as planned work instead of describing every requirement as already implemented.

## 5. The fall acceptance goals are specific

Speaker: Amar; seconds: 45

- FR-25: AI suggests likely questions; the owner supplies and approves answers.

- FR-14 / FR-26: compare published options against explicit customer needs.

- FR-06 / FR-11: preserve consented handoff context and trace the actual AI request.

The updated specification adds stable IDs for the owner question workflow and personalized shopping. Acceptance is observable: a private answer must remain private until approval, selected vehicles must be the ones sent in the request, a changed budget must update accepted preferences, and the resulting task must be inspectable. We also test unknown facts and safe failures. These checks give us a clear definition of success beyond a visually convincing answer.

## 6. The architecture separates interface, authority and inference

Speaker: Al Baraa; seconds: 90

The browser runs React and TypeScript. FastAPI handles authority, validation and application rules. Supabase Auth verifies identities; managed PostgreSQL stores application data. The FastAPI server sends paid requests to xAI using a private server key. Grok runs remotely, even though the demo’s application server currently runs on a Mac. A future hosted service replaces that Mac; users do not need a local language model. The backend remains responsible for publication, permissions, arithmetic and all database writes. The planned worker is for durable notifications, retention and synchronization. It is not currently a running completed feature. The implementation uses direct Psycopg SQL and versioned SQL files; earlier ORM/Alembic proposals are not the current code.

## 7. A private edit is not a public change

Speaker: Al Baraa; seconds: 45

- Save creates a private revision.

- Owner review publishes the exact saved revision and snapshot.

- Later edits leave the current public snapshot unchanged.

For example, if a published price is $23,500 and we save a private change to $24,500, customers still receive the approved $23,500 until republication. The approval request includes the expected saved revision, so a concurrent edit requires fresh review. The same principle applies to owner knowledge. An AI suggestion cannot approve or publish itself. This is one concrete place where business authority stays with a person.

## 8. Website: prepare the owner’s knowledge

Speaker: Fatkhaziz; seconds: 60

- Owner knowledge → Suggest customer questions with AI.

- Answer a question from a real business source, or route it to staff.

- Save privately → review the saved revision → publish deliberately.

Switch to the owner tab. Click Owner knowledge. During rehearsal, generate once and inspect the questions; during class, use the saved result or send one explicit live request if the budget and acceptance check are ready. Explain: AI helps an owner think of questions they may not have anticipated, but it does not invent official answers. Show the private and public revision numbers. Use a verified answer or a staff route; do not publish a fictional policy as a real business commitment. Return to slides only after the next two website steps.

## 9. Website: understand needs, compare and refine

Speaker: Fatkhaziz; seconds: 210

- Select Compact Hatch and City Hybrid, then open Find my fit.

- “My vehicle-price budget is $25,000. I need five seats and prefer fuel economy.”

- Then raise the budget to $30,000; inspect preferences, trade-offs and sources.

In Listings click Open customer inventory; it opens a second tab. Select the two explicitly fictional vehicles with Compare this vehicle. Click Compare selected to show the table and deterministic price difference; this makes no paid call. Click Find my fit and send the stated request once. Wait, then point to the visible budget and seats. Expand Sources used and identify a published vehicle field/revision. Answer its actual follow-up or explicitly raise the vehicle-price budget to $30,000 while retaining the other needs. Explain that the model interprets the request and writes the explanation; the backend rechecks eligibility and arithmetic. If asked whether a price is fair, ask that as an additional deliberate turn: the assistant can discuss known price/budget/specification trade-offs, but cannot establish market value without comparable sales and condition evidence. Do not promise a particular phrase or a specific best vehicle in advance. Save conversation after an accepted real response. If a request fails, say it was not accepted and show the recorded category; do not present a screenshot of a mock as live success.

## 10. Website: staff receive an explicit request

Speaker: Fatkhaziz; seconds: 45

- Ask staff to follow up → review the summary and selected vehicles.

- Use a synthetic contact for rehearsal and tick consent before submission.

- Owner tab: Inquiries → Refresh inquiries → inspect context → Pending.

The contact form is separate from AI chat. Submit only after showing what is being sent and confirming consent. In the owner inbox, refresh and expand the customer requirements and selected vehicles, then set the status to Pending. Explain that the database save and a notification are separate outcomes; this release does not claim an email or SMS was delivered. A normal answered chat does not automatically become a sales lead.

## 11. Show the actual server-side API call

Speaker: Al Baraa; seconds: 60

- backend/shopping.py  →  run_ai(...)

- backend/showcase_ai.py  →  provider_call(...)

- client.post('https://api.x.ai/v1/chat/completions', ...)

- Then validate output and recheck the published snapshot.

Open backend/showcase_ai.py at provider_call in GitHub. Point to client.post and the exact HTTPS URL. The request includes a configured model, system instructions, a JSON user payload, maximum output tokens and JSON response mode. The Authorization value comes from a private environment variable; do not open or reveal its value. The browser posts to our FastAPI endpoint, not directly to xAI. A JSON response is still untrusted data. After it arrives, we validate shape, source membership, explicit preference changes, hard constraints and allowed numeric facts, then recheck that the published data has not changed.

## 12. Trace one request through three identifiers

Speaker: Mohammad; seconds: 75

- HTTP request_id: our incoming request and safe server log.

- task_id: ai_tasks joined to assistant_runs.

- provider_response_id: xAI’s returned identifier, when supplied.

- Show time, model, tokens, latency, sources and both outcomes.

In System status click Refresh status and open Latest showcase AI requests. Pick the actual accepted classroom or rehearsal request, not merely a historical successful provider status. In Supabase SQL Editor run the supplied read-only latest-showcase query. Match task_id between ai_tasks.id and assistant_runs.task_id, and match request_id with the browser response header. Provider succeeded means a completion came back; application accepted means our validation passed. A failed application outcome is not a successful conversation. ai_interaction_evidence is for the earlier business-profile Q&A route; inquiries are customer work and do not prove an API call. An empty evidence table may simply be the wrong route or no calls yet.

## 13. Show the password location, without exposing a hash

Speaker: Mohammad; seconds: 60

- Managed account: Authentication → Users

- Database location: auth.users.encrypted_password

- Application authorization: public.memberships

- Use the supplied SELECT that returns hash presence and format only.

The user account belongs to Supabase Auth. For password-based users, the encrypted_password column stores a salted bcrypt hash, not a readable password. Memberships maps the verified user subject to a business, role and active state. It is not the password table. In SQL Editor run the supplied query that selects the account ID, whether a hash is present, its format prefix and length. Do not display the full hash. Authentication Users shows accounts, while Auth audit/login evidence is a different question from a paid xAI call. The app validates tokens with managed Auth and separately checks membership for business access. Source: Supabase password-security documentation.

## 14. Security controls have clear limits

Speaker: Mohammad; seconds: 60

- Owner approval, business-scoped SQL and composite foreign keys.

- Published-only prompts, bounded output and no autonomous database writes.

- Atomic spending reservations and no automatic paid retries.

- MFA policy, purge jobs and public rate limiting still need final deployment work.

Our threat model covers spoofing, tampering, repudiation, disclosure, denial of service and privilege escalation. Current controls include active membership checks, private/public revisions, explicit staff submission and safe correlation metadata. Direct application-table grants to browser API roles are revoked; the current migrations do not enable RLS, so we do not claim they do. Spending reservations protect the declared presentation allowance. Remaining hardening includes enforced privileged MFA, dedicated database privileges, scheduled retention and public-endpoint throttling. These limitations are part of the release plan rather than hidden behind a security label.

## 15. Verification separates code from real service behavior

Speaker: Amar; seconds: 45

- 79 backend regressions; 12 frontend interaction tests; production build.

- PostgreSQL upgrade preserves legacy records; Python 3.9/3.12 checks pass.

- Rendered desktop/mobile workflows use simulated Auth and Grok.

- Real sign-in and accepted model turns are separate live acceptance gates.

The automated checks cover application logic and rendered interaction, and the database check uses an actual disposable PostgreSQL instance. They intentionally avoid spending real AI credit. The configured Mac must still verify this latest code against the actual owner account and provider. We should show actual saved request evidence and a real accepted response when calling a feature live verified. The relevant CI run and code revision are linked in the guide. I am presenting the acceptance review, not claiming I authored all of these tests.

## 16. Current status and release gate

Speaker: Fatkhaziz; seconds: 45

- Implemented: knowledge approval, inventory, comparison, chat gateway, inquiries and evidence.

- Fixed: false rejection of valid citations, specification differences and natural seat wording.

- Latest code still needs an accepted real first turn and follow-up on the configured Mac.

This status is the honest November 26 baseline. Earlier real-provider runs prove that the integration reaches Grok, and owner suggestions succeeded, but later customer responses were rejected by application validation. The new fixes pass regressions and CI; we must load them and record accepted real turns before calling that repair live verified. Before presenting, replace this status with the actual outcome and IDs if the live check has passed. Do not replace the status merely because the server started or a test used a mock.

## 17. Completion plan preserves the full faculty scope

Speaker: Al Baraa; seconds: 75

The proposed spring sequence starts with platform and business permissions plus resource scheduling. That foundation supports a vehicle and salesperson test drive, a salon stylist and chair, and a studio photographer and room. Then we add dealership operational cases, voice, notifications, retention and sandbox subscriptions. The final release is evaluated across all three domains, with concurrency, accessibility, answer quality and recovery evidence. Exact dates depend on the spring syllabus; the plan uses weeks one to five, six to ten and eleven to fourteen rather than inventing course release dates.

## 18. Responsibilities must produce reviewable artifacts

Speaker: Fatkhaziz; seconds: 45

- Fatkhaziz: primary implementation/integration; joint detailed design.

- Al Baraa: initial design; joint detailed design and recorded elicitation.

- Next: distribute domain rules, scheduling and delivery work with tests and reviews.

- Every member presents actual work and demonstrates understanding.

I led the feasibility demo and most recent implementation/integration. Al Baraa led initial design and worked with me on detailed design. Recent implementation contribution from Amar and Mohammad was limited, so we should not assign them retroactive code credit. The spring plan gives each person a named artifact and acceptance gate. The suggested speaking roles are preparation assignments; each member must review and be able to explain the material they present. Documentation, tests and a short demonstration will establish completion.

## 19. AI assistance does not transfer responsibility

Speaker: Mohammad; seconds: 45

- Who can stop it? Operator controls, unpublish and usage limits.

- Who checked it? Exact-revision review and application validation.

- Whose name is on it? Recorded approver and accountable development team.

- ACM / IEEE: privacy, honesty, competence, fairness and accurate credit.

Jim Buchanan’s presentation focused on human accountability when AI produces work. Our owner approval model and request evidence support that responsibility, but they do not remove the need for judgment. We must report failed tests honestly, protect contacts and avoid unverified safety, warranty or market-value claims. The same standard applies to our use of AI coding and drafting tools: we remain responsible for reviewing the code, citing sources and accurately attributing contributions. Sources: supplied Buchanan slides; ACM 2018 and IEEE June 2020 ethics codes.

## 20. What this release demonstrates

Speaker: Fatkhaziz; seconds: 30

- AI helps an owner prepare knowledge and a customer narrow options.

- Published facts, permissions and transactions remain under application control.

- The next release adds complete multi-business workflows.

- Questions — 5 minutes

This release demonstrates a complete information path: owner preparation and approval, customer needs and comparison, a deliberate staff request and inspectable AI evidence. We distinguish implemented code from live acceptance and final-system plans. We are ready to trace a specific request or record rather than make broad claims about an AI label. We have set aside five minutes for questions.

## 21. Backup: data locations in Supabase

Speaker: Q&A; seconds: 0

- auth.users: identity and password hash. memberships: business access.

- listings / business_profiles / dealer_knowledge: private and published content.

- ai_tasks + assistant_runs: newer AI request metadata and sources.

- inquiries / business_inquiries / shopping_inquiries: explicitly submitted staff work.

Open the project’s Table Editor and keep public selected for application tables. Switch to auth only to inspect managed identity safely. schema_migrations contains upgrade filenames/checksums, not API calls. ai_budget.calls counts attempts, not dollars; ai_spend tables hold conservative reservations, not the provider’s authoritative wallet.

## 22. Backup: fair-price and unknown-fact questions

Speaker: Q&A; seconds: 0

- Known: asking price, budget difference and documented comparable specifications.

- Unknown without evidence: market valuation, condition, history and out-the-door fees.

- A useful AI explanation can discuss the supported part and ask a follow-up.

- The system does not promise financing approval or a guaranteed best purchase.

Say: We can explain how the listed price and documented features relate to this customer’s needs. We do not have a verified market-comparison or vehicle-condition feed, so we cannot certify that the asking price is fair market value. We would need approved comparable sales, location, condition/history and fees before making that claim. The assistant should make that distinction while still helping with the known trade-offs.

## 23. Backup: local hosting and an AI agent

Speaker: Q&A; seconds: 0

- The Mac currently hosts the web application for development/showcase.

- Supabase stores managed data remotely; Grok inference runs at xAI.

- The final app is intended to use a hosted HTTPS service.

- Whether software is an agent depends on its actions and autonomy, not where a model runs.

This implementation is an AI-assisted web application with controlled workflows. The model interprets and explains but cannot autonomously publish, book or write SQL. Calling an agent local-only is not a useful technical definition. The meaningful design question is what actions it can take, with what authority, confirmation and evidence. We can later add tightly authorized workflow tools without moving the model onto a customer device.

## 24. Backup: sources and technical references

Speaker: Q&A; seconds: 0

- Repository: github.com/Fatkhaziz/frontdesk-ai; updated report/specifications in docs.

- Supabase password-security docs; xAI structured outputs and pricing docs.

- OWASP ASVS / LLM Top 10; NIST CSF 2.0 / AI RMF; WCAG 2.2; Microsoft STRIDE.

- ACM 2018; IEEE June 2020; Jim Buchanan, Gannon, November 17, 2026.

Full URLs and access dates are in the report and individual submission. The sources explain external technologies and frameworks. Implementation evidence comes from the repository and actual test/request records, not from a provider’s marketing page. Formal compliance or production readiness is not claimed.