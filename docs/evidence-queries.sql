-- FrontDesk AI: administrator-run READ-ONLY evidence. Never paste keys or passwords.
-- 1. Latest newer showcase requests. A failed application outcome is not a successful answer.
SELECT t.created_at, t.kind, t.model, t.id AS task_id, r.request_id,
       r.provider_response_id, r.provider_outcome, r.application_outcome,
       r.latency_ms, r.token_usage, r.source_ids, t.result AS safe_diagnostic
FROM public.ai_tasks AS t
JOIN public.assistant_runs AS r ON r.task_id=t.id AND r.business_id=t.business_id
ORDER BY t.created_at DESC LIMIT 10;

-- 2. Latest earlier business-profile Q&A (different route/table).
SELECT t.created_at, e.task_id, e.request_id, e.provider_response_id,
       e.published_revision, e.provider_outcome, e.application_outcome, e.token_usage
FROM public.ai_interaction_evidence AS e
JOIN public.ai_tasks AS t ON t.id=e.task_id AND t.business_id=e.business_id
ORDER BY t.created_at DESC LIMIT 10;

-- 3. Password storage evidence: intentionally does NOT select the full hash or email.
-- Correlate the id with Authentication > Users. OAuth-only users may have no password hash.
SELECT id, created_at,
       (encrypted_password IS NOT NULL AND length(encrypted_password)>0) AS password_hash_present,
       CASE WHEN length(encrypted_password)>0 THEN left(encrypted_password,4) ELSE NULL END AS hash_format_prefix,
       length(encrypted_password) AS stored_hash_length
FROM auth.users ORDER BY created_at DESC LIMIT 5;

-- 4. Authorization mapping; this is NOT the password table.
SELECT subject, business_id, role, active FROM public.memberships ORDER BY business_id, subject;

-- 5. Schema upgrades; these are NOT AI requests.
SELECT name, sha256 FROM public.schema_migrations ORDER BY name;

-- 6. Current conservative allowance, NOT the provider's actual dollar balance.
SELECT mode, total_micro_usd / 1000000.0 AS declared_starting_allowance_usd,
       preparation_micro_usd / 1000000.0 AS preparation_ceiling_usd,
       presentation_reserve_micro_usd / 1000000.0 AS protected_reserve_usd,
       reserved_micro_usd / 1000000.0 AS conservatively_reserved_usd
FROM public.ai_spend_budget WHERE id=1;
SELECT calls AS historical_attempts FROM public.ai_budget WHERE id=1;
