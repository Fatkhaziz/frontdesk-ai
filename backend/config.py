"""Runtime public configuration; database and provider secrets never leave backend."""
import os


def question_mode():
    mode = os.getenv('QUESTION_MODE', 'demo')
    if mode not in ('demo', 'ai'):
        raise RuntimeError('QUESTION_MODE must be demo or ai')
    return mode


def ai_enabled():
    enabled = os.getenv('DRAFT_AI_ENABLED', '1' if question_mode() == 'ai' else '0') == '1'
    return enabled and bool(os.getenv('XAI_API_KEY') and os.getenv('XAI_MODEL'))


def supabase_config():
    url = os.getenv('SUPABASE_URL') or os.getenv('VITE_SUPABASE_URL', '')
    key = os.getenv('SUPABASE_PUBLISHABLE_KEY') or os.getenv('VITE_SUPABASE_PUBLISHABLE_KEY', '')
    # A service-role JWT or a new secret key must never be sent to a browser.
    if key.startswith('sb_secret_'):
        raise RuntimeError('Use a Supabase publishable key, not a secret key')
    if key.count('.') == 2:
        import base64
        import json
        try:
            payload = key.split('.')[1]
            role = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4))).get('role')
        except (ValueError, TypeError, UnicodeError):
            raise RuntimeError('Invalid public Supabase key') from None
        if role != 'anon':
            raise RuntimeError('Only an anon or publishable Supabase key may be public')
    return url.rstrip('/'), key


def database_options(project_root=None):
    """Resolve a relocated project CA without editing secrets or weakening TLS.

    An existing configured CA always wins. Only a missing path whose basename
    exists in this checkout's .certs directory may relocate; invalid PEM fails.
    The connection URL and certificate contents are never returned to clients.
    """
    from pathlib import Path
    import ssl
    from psycopg.conninfo import conninfo_to_dict
    options = conninfo_to_dict(os.getenv('DATABASE_URL', ''))
    configured = options.get('sslrootcert')
    if configured and not Path(configured).is_file():
        root = Path(project_root) if project_root else Path(__file__).resolve().parent.parent
        directory = (root / '.certs').resolve()
        candidate = directory / Path(configured).name
        if candidate.is_file() and candidate.resolve().parent == directory:
            ssl.create_default_context(cafile=str(candidate))
            options['sslrootcert'] = str(candidate)
    return options
