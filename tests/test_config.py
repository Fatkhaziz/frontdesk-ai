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
