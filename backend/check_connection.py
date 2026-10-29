"""Credential-safe real connectivity probe: python -m backend.check_connection."""
import httpx
from .config import supabase_config
from .db import connect, execute


def check():
    failed = False
    try:
        with connect() as c:
            execute(c, 'SELECT 1').fetchone()
            row = execute(c, "SELECT to_regclass('public.listings') AS existing").fetchone()
        print('Database: connected; listings table ' + ('present' if row['existing'] else 'not migrated'))
    except Exception as exc:
        print('Database: failed (' + type(exc).__name__ + '); no connection details printed')
        failed = True
    try:
        url, key = supabase_config()
        if not url or not key:
            raise RuntimeError('Missing configuration')
        with httpx.Client(timeout=15) as client:
            result = client.get(url + '/auth/v1/settings', headers={'apikey': key})
            result.raise_for_status()
        print('Supabase Auth settings: reachable with configured public key (login not tested)')
    except Exception as exc:
        print('Supabase Auth: failed (' + type(exc).__name__ + '); no configuration values printed')
        failed = True
    return int(failed)

if __name__ == '__main__':
    raise SystemExit(check())
