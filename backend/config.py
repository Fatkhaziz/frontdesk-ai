"""Runtime public configuration; database and provider secrets never leave backend."""
import os


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
