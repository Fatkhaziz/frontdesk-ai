"""Local launcher, called after scripts/run-local.sh loads the project .env."""
import os
from pathlib import Path
from psycopg.conninfo import conninfo_to_dict
from .db import connect, execute
from .config import supabase_config, question_mode
from .errors import error_category


def main():
    try:
        options = conninfo_to_dict(os.environ.get('DATABASE_URL', ''))
        if options.get('sslmode') != 'verify-full':
            raise RuntimeError('Local database requires sslmode=verify-full')
        cert = Path(options.get('sslrootcert', ''))
        if not cert.is_absolute() or not cert.is_file() or not os.access(cert, os.R_OK):
            raise RuntimeError('TLS root certificate file must be an absolute readable path')
        url, key = supabase_config()
        if not url or not key:
            raise RuntimeError('Supabase public configuration is missing')
        mode = question_mode()
        with connect() as c:
            execute(c, 'SELECT 1').fetchone()
        print('Local preflight passed: project environment loaded; CA readable; TLS verify-full; PostgreSQL connected.', flush=True)
        print('Question mode: ' + mode, flush=True)
    except Exception as exc:
        print('Local preflight failed: ' + type(exc).__name__ + ' (' + error_category(exc) + '). Check local settings privately.', flush=True)
        return 1
    import uvicorn
    uvicorn.run('backend.main:app', host='127.0.0.1', port=8000, access_log=False)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
