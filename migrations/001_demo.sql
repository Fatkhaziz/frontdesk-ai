BEGIN;
CREATE TABLE businesses (id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE memberships (subject TEXT PRIMARY KEY, business_id TEXT NOT NULL REFERENCES businesses(id), role TEXT NOT NULL CHECK(role IN ('owner','staff')), active BOOLEAN NOT NULL DEFAULT TRUE);
CREATE TABLE listings (id TEXT PRIMARY KEY, business_id TEXT NOT NULL REFERENCES businesses(id), revision INTEGER NOT NULL CHECK(revision>0), facts TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', approved_revision INTEGER, approved_by TEXT, published TEXT, published_revision INTEGER, UNIQUE(id,business_id));
CREATE TABLE inquiries (id TEXT PRIMARY KEY, business_id TEXT NOT NULL, listing_id TEXT NOT NULL, request_key TEXT NOT NULL, contact TEXT NOT NULL, message TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','pending','resolved')), created_at TEXT NOT NULL, FOREIGN KEY(listing_id,business_id) REFERENCES listings(id,business_id), UNIQUE(business_id,request_key));
CREATE TABLE ai_tasks (id TEXT PRIMARY KEY, business_id TEXT NOT NULL REFERENCES businesses(id), kind TEXT NOT NULL, model TEXT NOT NULL, status TEXT NOT NULL, duration_ms INTEGER, result TEXT, usage TEXT, created_at TEXT NOT NULL);
CREATE TABLE audit_events (id TEXT PRIMARY KEY, business_id TEXT NOT NULL REFERENCES businesses(id), actor TEXT NOT NULL, listing_id TEXT NOT NULL, revision INTEGER NOT NULL, action TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE ai_budget (id INTEGER PRIMARY KEY CHECK(id=1), calls INTEGER NOT NULL DEFAULT 0);
INSERT INTO ai_budget(id,calls) VALUES(1,0);
-- Application data is accessible only through the backend connection.
REVOKE ALL ON businesses,memberships,listings,inquiries,ai_tasks,audit_events,ai_budget FROM anon, authenticated;
COMMIT;
