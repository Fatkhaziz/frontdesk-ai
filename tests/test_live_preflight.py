"""Exercise the manual cost gate with synthetic settings and a mocked provider."""
import contextlib
import hashlib
import io
import json
import logging
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
import test_business as fixtures
from backend.db import connect, execute
from scripts import verify_live_qa as verification


class LivePreflight(unittest.TestCase):
    def setUp(self):
        self.logging_disable = logging.root.manager.disable
        fixtures.BusinessReception.setUp(self)
        fixtures.BusinessReception.save(self, fixtures.profile())
        fixtures.BusinessReception.publish(self)
        with connect() as c:
            execute(c, 'CREATE TABLE schema_migrations(name TEXT PRIMARY KEY,sha256 TEXT)')
            for name in ['003_business_reception.sql', '004_ai_interaction_evidence.sql']:
                execute(c, 'INSERT INTO schema_migrations VALUES(%s,%s)', (name, hashlib.sha256(Path('migrations',name).read_bytes()).hexdigest()))
        self.provider_env = patch.dict(os.environ, {'XAI_MODEL':verification.MODEL,'XAI_API_KEY':'synthetic-key','AI_CALL_LIMIT':'10'})
        self.provider_env.start()

    def tearDown(self):
        logging.disable(self.logging_disable)
        self.provider_env.stop()
        fixtures.BusinessReception.tearDown(self)

    def invoke(self, *args):
        with patch('sys.argv', ['verify_live_qa','--business','a',*args]), contextlib.redirect_stdout(io.StringIO()):
            return verification.main()

    def test_default_preflight_never_calls_provider(self):
        with patch('httpx.Client', side_effect=AssertionError('No network')):
            self.assertEqual(self.invoke(), 0)
        with connect() as c:
            self.assertEqual(execute(c,'SELECT calls FROM ai_budget').fetchone()['calls'], 0)

    def test_missing_insufficient_and_nonfinite_budget_never_calls_provider(self):
        for args in [[], ['--remaining-usd','0','--authorized-remaining-usd','5'], ['--remaining-usd','0.02','--authorized-remaining-usd','0.02'], ['--remaining-usd','5','--authorized-remaining-usd','NaN']]:
            with patch('httpx.Client', side_effect=AssertionError('No network')):
                with self.assertRaises(RuntimeError):
                    self.invoke('--execute-one-paid-request','--billing-checked',*args)

    def test_manual_confirmation_permits_exactly_one_mock_inference(self):
        real = httpx.Client
        calls = []
        def handler(request):
            calls.append(request.method)
            if request.method == 'GET':
                return httpx.Response(200,json={'data':[{'id':verification.MODEL}]})
            payload = json.loads(json.loads(request.content)['messages'][1]['content'])
            source = next(s for s in payload['sources'] if s['path'] == 'faqs/0')
            result = {'business_id':'a','revision':1,'handoff':False,'claims':[{'source_id':source['id'],'text':source['text']}]}
            return httpx.Response(200,json={'id':'mock-live-command','choices':[{'finish_reason':'stop','message':{'content':json.dumps(result)}}]})
        with patch('httpx.Client',side_effect=lambda **kwargs: real(transport=httpx.MockTransport(handler))), patch('builtins.input',return_value='SEND ONE'):
            self.assertEqual(self.invoke('--execute-one-paid-request','--billing-checked','--remaining-usd','1','--authorized-remaining-usd','1'),0)
        self.assertEqual(calls,['GET','POST'])
        self.assertEqual(os.environ['AI_CALL_LIMIT'],'10')
        with connect() as c:
            self.assertEqual(execute(c,'SELECT calls FROM ai_budget').fetchone()['calls'],1)
            self.assertEqual(execute(c,'SELECT application_outcome FROM ai_interaction_evidence').fetchone()['application_outcome'],'accepted')
