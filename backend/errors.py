"""Error categories suitable for logs; never include driver messages or values."""
def error_category(exc):
    message = str(exc).lower()
    for fragment, category in (
        ('root certificate file', 'tls_ca_unreadable'),
        ('certificate verify failed', 'tls_verification_failed'),
        ('password authentication failed', 'database_password_rejected'),
        ('could not translate host name', 'hostname_resolution_failed'),
        ('timeout', 'connection_timeout'),
        ('permission denied', 'permission_denied'),
    ):
        if fragment in message:
            return category
    return 'unclassified'
