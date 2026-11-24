"""Safe service/schema checks; never loads .env or makes inference requests.

python -m backend.verify_integration [--apply-pending] [--database-only]
The apply flag is explicit. Existing application rows and the budget are hashed
privately before/after migration; no row values or digests are printed.
"""
import argparse
import hashlib
import json
import logging
import sqlite3
from pathlib import Path

import httpx
from .config import supabase_config
from .db import connect, execute
from .migrate import migrate

ROOT = Path(__file__).resolve().parent.parent


def schema_contract():
    with sqlite3.connect(':memory:') as c:
        for path in sorted((ROOT / 'migrations').glob('*.sql')):
            c.executescript(path.read_text().split('REVOKE')[0].split('-- Application data')[0] + '\nCOMMIT;')
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return {table: [row[1] for row in c.execute('PRAGMA table_info(' + table + ')')] for table in tables}


def snapshot_rows(c, tables):
    result = {}
    for table in tables:
        # Names come only from the checked-in contract, never from a request.
        rows = execute(c, 'SELECT * FROM public.' + table + ' ORDER BY 1').fetchall()
        digest = hashlib.sha256()
        for row in rows:
            digest.update(json.dumps(dict(row), sort_keys=True, default=str).encode())
        result[table] = (len(rows), digest.hexdigest())
    return result


def inspect_database(apply_pending=False):
    contract = schema_contract()
    with connect() as c:
        execute(c, 'SET TRANSACTION READ ONLY')
        existing = {r['table_name'] for r in execute(c, "SELECT table_name FROM information_schema.tables WHERE table_schema='public'").fetchall()}
        before = snapshot_rows(c, sorted(existing & contract.keys()))
        if 'schema_migrations' in existing:
            applied = {r['name']: r['sha256'] for r in execute(c, 'SELECT name,sha256 FROM public.schema_migrations').fetchall()}
        else:
            applied = {}
        for filename, digest in applied.items():
            path = ROOT / 'migrations' / filename
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise RuntimeError('Migration checksum review required')
    print('PostgreSQL: connected; existing checksums reviewed; application row baseline saved privately.')
    if apply_pending:
        migrate()  # Atomic transaction, advisory lock, refusal of untracked schemas.
    with connect() as c:
        execute(c, 'SET TRANSACTION READ ONLY')
        schemas = [r['schema_name'] for r in execute(c, 'SELECT schema_name FROM information_schema.schemata ORDER BY schema_name').fetchall()]
        rows = execute(c, "SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='public' ORDER BY table_name,ordinal_position").fetchall()
        actual = {}
        for row in rows:
            actual.setdefault(row['table_name'], []).append(row['column_name'])
        for table, columns in contract.items():
            if not set(columns) <= set(actual.get(table, [])):
                raise RuntimeError('Required table/column missing')
        if before != snapshot_rows(c, before.keys()):
            raise RuntimeError('Existing row preservation check failed; investigate privately')
        foreign_keys = execute(c, "SELECT conrelid::regclass::text AS child,pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE contype='f' AND connamespace='public'::regnamespace ORDER BY conrelid::regclass::text,conname").fetchall()
        grants = execute(c, "SELECT table_name,grantee FROM information_schema.role_table_grants WHERE table_schema='public' AND grantee IN ('anon','authenticated')").fetchall()
        if any(row['table_name'] in contract for row in grants):
            raise RuntimeError('Unexpected browser role grant on application tables')
        calls = execute(c, 'SELECT calls FROM public.ai_budget WHERE id=1').fetchone()['calls']
        migrations = [r['name'] for r in execute(c, 'SELECT name FROM public.schema_migrations ORDER BY name').fetchall()]
    print('Visible schemas:', ', '.join(schemas))
    for table in contract:
        print('public.' + table + ': ' + ', '.join(actual[table]))
    print('Foreign keys inspected:', len(foreign_keys))
    print('Browser table grants: none. Existing application rows: unchanged. AI attempts used:', calls)
    print('Applied migrations:', ', '.join(migrations))
    return actual


def check_auth():
    url, key = supabase_config()
    if not url or not key:
        raise RuntimeError('Auth configuration missing')
    with httpx.Client(timeout=15) as client:
        settings = client.get(url + '/auth/v1/settings', headers={'apikey': key})
        settings.raise_for_status()
        rejected = client.get(url + '/auth/v1/user', headers={'apikey': key, 'Authorization': 'Bearer integration-invalid'})
        if rejected.status_code not in (401, 403):
            raise RuntimeError('Invalid bearer was not rejected')
    print('Supabase Auth: settings reachable; invalid bearer rejected. Real user sign-in NOT tested.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply-pending', action='store_true')
    parser.add_argument('--database-only', action='store_true', help='For isolated PostgreSQL CI; does not claim Auth verification')
    args = parser.parse_args()
    logging.getLogger('httpx').setLevel(logging.WARNING)
    failed = False
    if not args.database_only:
        try:
            check_auth()
        except Exception as exc:
            print('Supabase Auth check failed (' + type(exc).__name__ + '); no credentials or response body printed.')
            failed = True
    try:
        inspect_database(args.apply_pending)
    except Exception as exc:
        print('PostgreSQL/schema check failed (' + type(exc).__name__ + '); no connection or row values printed.')
        failed = True
    return int(failed)


if __name__ == '__main__':
    raise SystemExit(main())
