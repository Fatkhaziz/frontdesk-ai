BEGIN;
CREATE TABLE dealer_knowledge (
    business_id TEXT PRIMARY KEY REFERENCES businesses(id),
    revision INTEGER NOT NULL CHECK(revision > 0),
    cards TEXT NOT NULL,
    published TEXT,
    published_revision INTEGER,
    approved_by TEXT,
    CHECK ((published IS NULL AND published_revision IS NULL) OR
           (published IS NOT NULL AND published_revision > 0 AND published_revision <= revision))
);
CREATE TABLE knowledge_events (
    id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL REFERENCES businesses(id),
    actor TEXT NOT NULL,
    revision INTEGER NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('publish','unpublish')),
    created_at TEXT NOT NULL
);
CREATE TABLE assistant_runs (
    task_id TEXT PRIMARY KEY REFERENCES ai_tasks(id) ON DELETE CASCADE,
    business_id TEXT NOT NULL REFERENCES businesses(id),
    request_id TEXT NOT NULL,
    operation TEXT NOT NULL,
    source_snapshot TEXT NOT NULL,
    source_ids TEXT,
    provider_response_id TEXT,
    token_usage TEXT,
    latency_ms INTEGER,
    provider_outcome TEXT NOT NULL,
    application_outcome TEXT NOT NULL,
    FOREIGN KEY(task_id,business_id) REFERENCES ai_tasks(id,business_id) ON DELETE CASCADE
);
CREATE INDEX assistant_runs_request ON assistant_runs(business_id,request_id);
CREATE TABLE shopping_inquiries (
    id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL REFERENCES businesses(id),
    request_key TEXT NOT NULL,
    contact TEXT NOT NULL,
    message TEXT NOT NULL,
    context TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','pending','resolved')),
    created_at TEXT NOT NULL,
    UNIQUE(business_id,request_key)
);
REVOKE ALL ON dealer_knowledge,knowledge_events,assistant_runs,shopping_inquiries FROM anon, authenticated;
COMMIT;
