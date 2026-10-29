"""PostgreSQL in deployment; SQLite is an explicit isolated test adapter only."""
import os
from contextlib import contextmanager

@contextmanager
def connect():
    url = os.getenv('DATABASE_URL', '')
    if not url:
        raise RuntimeError('DATABASE_URL is required')
    if url.startswith('sqlite:///') and os.getenv('TESTING') == '1':
        import sqlite3
        c = sqlite3.connect(url[10:])
        c.row_factory = sqlite3.Row
    else:
        import psycopg
        from psycopg.rows import dict_row
        c = psycopg.connect(url, row_factory=dict_row, connect_timeout=10)
    try:
        yield c
        c.commit()
    except BaseException:
        c.rollback()
        raise
    finally:
        c.close()

def execute(c, sql, args=()):
    if c.__class__.__module__.startswith('sqlite3'):
        sql = sql.replace('%s', '?')
    return c.execute(sql, args)
