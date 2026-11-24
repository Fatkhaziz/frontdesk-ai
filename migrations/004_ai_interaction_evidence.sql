BEGIN;
CREATE UNIQUE INDEX ai_tasks_identity_business ON ai_tasks(id,business_id);
CREATE TABLE ai_interaction_evidence (
    task_id TEXT PRIMARY KEY REFERENCES ai_tasks(id) ON DELETE CASCADE,
    request_id TEXT NOT NULL,
    business_id TEXT NOT NULL REFERENCES businesses(id),
    published_revision INTEGER NOT NULL CHECK(published_revision > 0),
    approved_sources TEXT NOT NULL,
    selected_sources TEXT,
    provider_response_id TEXT,
    token_usage TEXT,
    latency_ms INTEGER,
    provider_outcome TEXT NOT NULL CHECK(provider_outcome IN ('started','succeeded','failed')),
    application_outcome TEXT NOT NULL CHECK(application_outcome IN ('pending','accepted','handoff','provider_error','invalid_output','stale_source')),
    FOREIGN KEY(task_id,business_id) REFERENCES ai_tasks(id,business_id) ON DELETE CASCADE
);
CREATE INDEX ai_evidence_request ON ai_interaction_evidence(request_id,business_id);
REVOKE ALL ON ai_interaction_evidence FROM anon, authenticated;
COMMIT;
