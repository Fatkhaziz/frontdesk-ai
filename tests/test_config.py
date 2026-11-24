import base64
import json
import os
import unittest
from unittest.mock import patch
from backend.config import supabase_config

class PublicConfig(unittest.TestCase):
    def test_runtime_aliases(self):
        with patch.dict(os.environ, {'VITE_SUPABASE_URL':'https://example.supabase.co/','VITE_SUPABASE_PUBLISHABLE_KEY':'sb_publishable_test'}, clear=True):
            self.assertEqual(supabase_config(), ('https://example.supabase.co','sb_publishable_test'))

    def test_canonical_names_take_precedence(self):
        with patch.dict(os.environ, {'SUPABASE_URL':'https://primary.supabase.co','VITE_SUPABASE_URL':'https://other.supabase.co','SUPABASE_PUBLISHABLE_KEY':'sb_publishable_primary','VITE_SUPABASE_PUBLISHABLE_KEY':'sb_publishable_other'}, clear=True):
            self.assertEqual(supabase_config(), ('https://primary.supabase.co','sb_publishable_primary'))

    def test_reject_private_keys(self):
        payload = base64.urlsafe_b64encode(json.dumps({'role':'service_role'}).encode()).decode().rstrip('=')
        for key in ['sb_secret_test', 'header.'+payload+'.signature']:
            with patch.dict(os.environ, {'VITE_SUPABASE_PUBLISHABLE_KEY':key}, clear=True):
                with self.assertRaises(RuntimeError):
                    supabase_config()


class DatabaseCA(unittest.TestCase):
    def test_missing_path_resolves_only_matching_valid_project_certificate(self):
        import ssl
        import tempfile
        from pathlib import Path
        from backend.config import database_options
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / '.certs').mkdir()
            cert = root / '.certs' / 'test-ca.pem'; cert.write_text('invalid PEM')
            with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://localhost/test?sslmode=verify-full&sslrootcert=/old/location/test-ca.pem'}):
                with self.assertRaises(ssl.SSLError): database_options(root)
                with patch('ssl.create_default_context') as validate:
                    options = database_options(root)
                    self.assertEqual(options['sslmode'], 'verify-full')
                    self.assertEqual(options['sslrootcert'], str(cert.resolve()))
                    validate.assert_called_once_with(cafile=str(cert.resolve()))
                cert.unlink()
                self.assertEqual(database_options(root)['sslrootcert'], '/old/location/test-ca.pem')

    def test_existing_configured_certificate_is_not_replaced(self):
        import tempfile
        from pathlib import Path
        from backend.config import database_options
        with tempfile.NamedTemporaryFile() as cert:
            with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://localhost/test?sslmode=verify-full&sslrootcert=' + cert.name}):
                with patch('ssl.create_default_context', side_effect=AssertionError('Do not replace configured trust')):
                    self.assertEqual(database_options()['sslrootcert'], cert.name)
