# FrontDesk AI live walkthrough and code reference

The fall demonstration uses the dealership workspace. The buyer compares published vehicles and talks to Grok in the storefront. The owner prepares answers before they are published. Keep these notes beside the browser.

## Open the live website

1. In GitHub Desktop, open the configured `frontdesk-ai` repository, select `main`, and fetch and pull.
2. In the Terminal tab running the previous server, press Control+C. Run these lines in the same tab:

   ```bash
   cd "$HOME/Desktop/Gannon/7th semester/Senior Design/frontdesk-ai"
   bash scripts/launch-showcase.sh
   ```

3. Leave Terminal open. Open [the dashboard](http://127.0.0.1:8000/) and sign in. Click **Open customer site** to open the buyer's tab. Keep the owner tab open for knowledge and inquiries.
4. Before sharing your screen, sign in to Supabase and open the [repository](https://github.com/Fatkhaziz/frontdesk-ai) in a third tab. The only AI calls in the walkthrough below are the actions you click. The standard launch builds and serves the website without calling Grok. In **Request log → Service and usage details** you can check the practice allowance.

## 1. Start with the owner

**Do.** Click **Owner knowledge → Suggest customer questions with AI**. Wait for the questions to appear. Pick one you can answer from information you have. For a question about accident history or warranty terms that you can't verify, click **Staff must answer**. For a question you can substantiate, fill **Owner-provided answer** and **Source or reference (optional)** and click **Approve this answer**. Click **Save private knowledge**, tick the review checkbox and click **Publish reviewed knowledge**. Open **See published answers** and expand the question to see the result.

**Say.** “Grok looks at this dealership's published inventory and the questions we've already covered. It suggests what buyers might ask. I decide what's accurate enough to publish and where a person needs to answer. Customers see the published FAQ and the assistant can use those same answers.”

**Point.** [KnowledgeSetup.tsx](../frontend/src/KnowledgeSetup.tsx) calls `POST /api/dealer/knowledge/suggest`. The `suggest` function in [shopping.py](../backend/shopping.py) authenticates the owner, builds context from the business's published records and calls `run_ai`. Suggestions return to the form as drafts. `PUT /api/dealer/knowledge` saves `public.dealer_knowledge.cards` and advances the private revision. `POST /api/dealer/knowledge/publish` copies the reviewed public fields into `published`, records `published_revision` and adds a row to `public.knowledge_events`. The public shop reads that snapshot. A staff referral exposes the question and referral without the private answer.

## 2. Compare actual inventory records

**Do.** In the customer tab, click **Inventory**. Check **Compare this vehicle** on **Compact Hatch** and **City Hybrid**. Click **Compare selected (2)**. Point to their asking prices, mileage, seats, documented MPG, cargo and the price difference. These two entries are labeled fictional examples.

**Say.** “The comparison comes from the latest published version of each selected car. The server subtracts the listed prices in cents. The Compact Hatch is cheaper and has more published cargo space. The City Hybrid has higher published combined MPG. A missing specification stays blank as ‘Not provided.’”

**Point.** [PublicShop.tsx](../frontend/src/PublicShop.tsx) sends the selected IDs and buyer preferences to `POST /api/shop/{business_id}/compare`. In [shopping.py](../backend/shopping.py), `catalog` reads `public.listings.published` and `published_revision` for that business. `comparison_result` computes the difference and `assessments` checks the buyer's needs against the facts. Open the resulting comparison next to those two records in Supabase. The compare action uses database facts and arithmetic.

## 3. Have a live conversation

Stay in the **same customer tab** so it keeps both selected cars. Click **AI chat**. Type a message in **Your message** and click **Send to AI**.

- **First turn.** “My vehicle-price budget is $25,000. I need five seats for commuting and prefer fuel economy. Which of these two cars fits better, and what would you ask me next?”
- **Follow-up.** Answer the assistant's actual question. Then try “Raise my vehicle-price budget to $30,000 and retain five seats. What changes?” Show the updated budget under **Your preferences**.
- **If asked about a fair price.** “Is the City Hybrid a fair price? What would you need to know before deciding?” Show the listed price, the comparison and any missing condition, fee or market evidence the assistant explains. This dealership's inventory alone cannot establish market value.

Read the actual reply and open **Sources used** on that message. In practice, you can also ask about carrying a stroller, a mileage cap for a long commute, or which published listings confirm AWD for winter driving. Those are customer prompts to type during the chat.

**Say.** “I gave it a budget and daily use in normal language. Grok writes the reply and suggests a follow-up. We check that the preferences came from what I said, and we insert the exact quantities from the published records. The next turn carries the previous preferences and recent dialogue.”

**Point.** The `ask` function in [PublicShop.tsx](../frontend/src/PublicShop.tsx) sends each message to `POST /api/shop/{business_id}/assist`, along with the selected IDs, current preferences and recent turns. The `assist` route in [shopping.py](../backend/shopping.py) builds a published source list for that business. The server sends those approved facts and the message in a single request through `provider_call` in [showcase_ai.py](../backend/showcase_ai.py). Point to `client.post` for the HTTPS call to [xAI Chat Completions](https://docs.x.ai/developers/rest-api-reference/inference/chat-completions). The model and API key come from the server's environment. Keep the key off screen.

**Explain the return path.** [shopping_delivery.py](../backend/shopping_delivery.py) resolves the model's source IDs against the published snapshot and inserts exact values. It checks independently sourced paragraphs and can omit an unverifiable paragraph while showing the rest of Grok's live reply. The backend checks recommendations and hard limits and verifies that the publication stayed current. The same response includes the updated comparison. The customer tab displays the reply, sources, follow-up and new preferences.

## 4. Hand the question to staff

**Do.** Under the chat, click **Ask staff to follow up**. Enter “Please confirm the maintenance history for these two example cars” and a test contact such as `practice@example.invalid`. Agree to send the details, then click **Send inquiry to staff**. Switch to the owner tab, click **Inquiries → Refresh inquiries**, open the request context and change the status to **Pending**.

**Say.** “This action gives staff the selected vehicles, the buyer's preferences and the request. We ask for consent before saving contact details.”

**Point.** `submit_followup` in [shopping.py](../backend/shopping.py) handles `POST /api/shop/{business_id}/inquiries` and saves the request to `public.shopping_inquiries`. The owner inbox uses `GET /api/inquiries`. The status control sends `PATCH /api/shopping/inquiries/{iid}`; the server scopes the update to the signed-in business. The contact comes from this separate form and stays in the staff workflow.

## When faculty want to see the request or password storage

**Trace the request you just made.** Open the small **Request log** link below the owner workspace and click **Refresh requests**. Find the most recent `shopping_assistant` or `knowledge_suggestions` row. Point to the request ID, task ID, provider response ID, model, latency and token usage. `provider_outcome` records the call to xAI. `application_outcome` records whether the application delivered a verified reply. `accepted_with_limits` means some wording was omitted. You can match the request ID to the `X-Request-ID` header of the POST in the browser's Network tab.

In Supabase SQL Editor, run the first query from [evidence-queries.sql](evidence-queries.sql). Match the request ID with `public.assistant_runs.request_id`. The query joins the cited source IDs and provider outcome to `public.ai_tasks` through `task_id` and `business_id`. For an exact match, add `WHERE r.request_id = 'PASTE THE REQUEST ID'` before `ORDER BY`. The source snapshot is in `assistant_runs.source_snapshot`. `public.ai_budget` tracks attempts. `public.ai_spend_reservations` records the conservative budget reserved by [spending.py](../backend/spending.py). The regular conversation stays in browser memory between turns and its recent messages travel to Grok for context. Supabase stores request metadata and the separately submitted inquiries.

**Point to password storage.** In Supabase SQL Editor, run query 3 from [evidence-queries.sql](evidence-queries.sql). It shows whether the `encrypted_password` column of `auth.users` contains a hash. Supabase Auth uses bcrypt. In **Authentication → Users**, show the corresponding user ID. Then show `public.memberships`, which associates the authenticated user's ID with a business and role. [main.tsx](../frontend/src/main.tsx) signs in through Supabase Auth. In [main.py](../backend/main.py), `identity` validates the token with Supabase before reading that membership. Owner-only endpoints additionally use `owner`. [Supabase password documentation](https://supabase.com/docs/guides/auth/password-security)

**Where it runs.** React runs in Safari. The demonstration's FastAPI process runs on the Mac at `127.0.0.1:8000`. Supabase runs the managed PostgreSQL database and Auth. Grok runs at xAI. The final deployment plan puts the application server on a hosted HTTPS service.

## Practice boundary

The owner question generator and each **Send to AI** use one AI request. Opening pages, publishing a reviewed answer, comparing and checking the request log use no inference. The configured practice allowance remains protected. The automated checks use a simulated provider. Verify the real conversation on the configured Mac by sending the first message and then one follow-up from the customer tab. If a turn fails, use that request's reference and owner log to diagnose it before repeating the call.
