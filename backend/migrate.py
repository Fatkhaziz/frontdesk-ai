"""Run with python -m backend.migrate. Never logs connection strings or SQL data."""
import hashlib
from pathlib import Path
from .db import connect, execute


def migrate():
    with connect() as c:
        # Serializes migration runners on PostgreSQL, released at transaction end.
        execute(c, 'SELECT pg_advisory_xact_lock(783234911)')
        execute(c, 'CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, sha256 TEXT NOT NULL)')
        for path in sorted((Path(__file__).resolve().parent.parent / 'migrations').glob('*.sql')):
            sql = path.read_text()
            digest = hashlib.sha256(sql.encode()).hexdigest()
            prior = execute(c, 'SELECT sha256 FROM schema_migrations WHERE name=%s', (path.name,)).fetchone()
            if prior:
                if prior['sha256'] != digest:
                    raise RuntimeError('An applied migration has changed')
                print(path.name + ': already applied')
                continue
            # Existing manually provisioned schemas need explicit review, never overwrite.
            if path.name == '001_demo.sql':
                exists = execute(c, "SELECT to_regclass('public.listings') AS existing").fetchone()
                if exists['existing']:
                    raise RuntimeError('Existing untracked schema: review before migration adoption')
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            for statement in statements:
                if statement.upper() in ('BEGIN', 'COMMIT'):
                    continue
                execute(c, statement)
            execute(c, 'INSERT INTO schema_migrations VALUES (%s,%s)', (path.name, digest))
            print(path.name + ': applied')

if __name__ == '__main__':
    try:
        migrate()
    except Exception as exc:
        # Driver errors may contain database host/user details; do not expose them.
        print('Migration failed (' + type(exc).__name__ + '). Check configuration, connectivity, privileges and schema state securely.')
        raise SystemExit(1) from None
