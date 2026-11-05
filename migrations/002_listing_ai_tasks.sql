BEGIN;
CREATE TABLE listing_ai_tasks (
    task_id TEXT PRIMARY KEY REFERENCES ai_tasks(id) ON DELETE CASCADE,
    listing_id TEXT NOT NULL,
    business_id TEXT NOT NULL,
    FOREIGN KEY(listing_id,business_id) REFERENCES listings(id,business_id) ON DELETE CASCADE
);
CREATE INDEX listing_ai_tasks_listing ON listing_ai_tasks(listing_id,business_id);
REVOKE ALL ON listing_ai_tasks FROM anon, authenticated;
COMMIT;
