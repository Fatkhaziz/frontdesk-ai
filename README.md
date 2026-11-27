# FrontDesk AI

A small-business receptionist project. Fall Release 1 demonstrates a dealership: owner-assisted knowledge preparation, reviewed publication, published vehicle comparison, personalized AI shopping and explicit staff handoff. The final scope includes dealership, salon and photography workflows.

## Current release

**Workspace 2** introduces the dark left navigation, owner summary, expanded inventory layout and a focused customer conversation view. See [the update notes](docs/workspace-2-update.md). Both launch commands rebuild the current frontend, even when an optional live AI check fails.

Code implements the AI gateway and validation repairs, searchable owner listings, selected-vehicle comparison, accepted-conversation export and protected practice allowance. Automated checks use mocked providers. **The latest real customer first turn and follow-up still require acceptance on the configured Mac.** Earlier failed completions are not relabeled as successful answers.

- [Complete requirements, use cases and measurable targets](docs/requirements.md)
- [Current technical design and code/data map](docs/detailed-design.md)
- [Practice and live verification guide](docs/showcase-release.md)
- [Read-only password and AI evidence queries](docs/evidence-queries.sql)
- [20-minute presentation with speaking notes](docs/presentation-notes.md)
- [Presentation slide file copy](docs/FrontDesk_AI_End_of_Semester_Presentation.pdf)
- [Practice guide in Word](docs/FrontDesk_AI_Practice_Showcase_and_Technical_Guide.docx)
- [Team project report](docs/FrontDesk_AI_Team_Project_Report.docx)
- [Current requirements in Word](docs/FrontDesk_AI_Requirements_Use_Cases_and_Constraints.docx)
- [Current detailed design in Word](docs/FrontDesk_AI_Detailed_System_Design_v6.docx)

## Start in the existing configured Mac checkout

Pull the merged main branch. Stop the earlier server in its Terminal with Control+C. Keep the existing private `.env` and certificates; never commit them. Then run:

```bash
bash scripts/launch-showcase.sh
```

Open http://127.0.0.1:8000/ and sign in privately. Listings → Open customer inventory opens the matching public page. Keep the server Terminal open.

The launcher applies additive migration 006, checks existing-row preservation, builds and starts the app. It makes **no inference request**. Historical usage is preserved. The shared conservative ledger limits preparation to $1.00 from the owner-declared $4.97 remaining allowance and protects at least $3.50 while preparation mode is active. An attempt count is not the provider dollar balance. Verify actual credit separately. No purchases, top-ups, counter resets or automatic paid retries occur.

For a deliberate three-turn real integration check, use `bash scripts/launch-showcase.sh --practice --verify-live`. The check stops at the first failure, never retries, and saves synthetic raw responses privately on the Desktop for diagnosis. A failed optional check is reported and the newly built website still starts. It does not prove browser sign-in.

Before the presentation, the owner can deliberately launch:

```bash
bash scripts/launch-showcase.sh --presentation
```

This changes the existing ledger phase, without granting new credit or clearing reservations.

## Verification

```bash
.venv/bin/python -m unittest discover -s tests -v
npm test --prefix frontend
npm run build --prefix frontend
```

The release has 86 backend and 12 frontend tests. The [verification workflow](https://github.com/Fatkhaziz/frontdesk-ai/actions) checks Python 3.9/3.12, a disposable PostgreSQL upgrade preserving legacy records, and rendered desktop/mobile workflows with simulated Auth/Grok. CI does not establish real sign-in, live inference quality or production readiness.

The actual model call is `provider_call` in `backend/showcase_ai.py`. Newer evidence is `ai_tasks` joined to `assistant_runs`; older business-profile Q&A uses `ai_interaction_evidence`. Inquiries are separate customer work. Password hashes are managed by Supabase Auth in `auth.users.encrypted_password`; `memberships` contains business authorization, not passwords.

## Final-system scope

Four roles and departments, resource bookings, phone reception, reminders, subscription sandbox, full dealership operations and complete salon/studio workflows remain the spring plan. Current table access is restricted through backend checks and revoked browser-role grants; RLS policies, enforced MFA, retention jobs and public rate limiting are not claimed implemented. SQLite is an isolated test adapter, not the deployment database. The current Mac application host will be replaced by a hosted HTTPS service; Grok and Supabase are already external services.
