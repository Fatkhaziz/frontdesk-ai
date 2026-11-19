BEGIN;
CREATE TABLE business_profiles (
    business_id TEXT PRIMARY KEY REFERENCES businesses(id),
    revision INTEGER NOT NULL CHECK(revision > 0),
    profile TEXT NOT NULL,
    published TEXT,
    published_revision INTEGER,
    approved_by TEXT,
    CHECK ((published IS NULL AND published_revision IS NULL) OR
           (published IS NOT NULL AND published_revision > 0 AND published_revision <= revision))
);
CREATE TABLE business_inquiries (
    id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL REFERENCES business_profiles(business_id),
    request_key TEXT NOT NULL,
    profile_revision INTEGER NOT NULL,
    service_id TEXT,
    service_name TEXT NOT NULL,
    message TEXT NOT NULL,
    contact TEXT NOT NULL,
    answers TEXT NOT NULL,
    answer_labels TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','pending','resolved')),
    created_at TEXT NOT NULL,
    UNIQUE(business_id, request_key)
);
CREATE TABLE business_profile_events (
    id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL REFERENCES business_profiles(business_id),
    actor TEXT NOT NULL,
    revision INTEGER NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('publish','unpublish')),
    created_at TEXT NOT NULL,
    UNIQUE(business_id, revision, action)
);
CREATE INDEX business_inquiries_inbox ON business_inquiries(business_id, created_at);
REVOKE ALL ON business_profiles,business_inquiries,business_profile_events FROM anon, authenticated;
COMMIT;
