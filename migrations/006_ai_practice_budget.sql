BEGIN;
-- A conservative reservation ledger, not the provider's authoritative balance.
CREATE TABLE IF NOT EXISTS ai_spend_budget (
    id INTEGER PRIMARY KEY CHECK(id=1),
    total_micro_usd INTEGER NOT NULL CHECK(total_micro_usd>0),
    preparation_micro_usd INTEGER NOT NULL CHECK(preparation_micro_usd>0),
    presentation_reserve_micro_usd INTEGER NOT NULL CHECK(presentation_reserve_micro_usd>=0),
    reserved_micro_usd INTEGER NOT NULL DEFAULT 0,
    preparation_reserved_micro_usd INTEGER NOT NULL DEFAULT 0,
    mode TEXT NOT NULL DEFAULT 'preparation' CHECK(mode IN ('preparation','presentation')),
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ai_spend_reservations (
    task_id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL REFERENCES businesses(id),
    operation TEXT NOT NULL,
    mode TEXT NOT NULL,
    reserved_micro_usd INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
REVOKE ALL ON ai_spend_budget, ai_spend_reservations FROM anon, authenticated;
COMMIT;
