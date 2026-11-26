import json
import unittest
from pathlib import Path
from unittest.mock import patch
from tests import test_shopping as fixtures
from scripts.acceptance_live import verify

class LiveAcceptance(unittest.TestCase):
    setUp=fixtures.Shopping.setUp
    tearDown=fixtures.Shopping.tearDown
    result=fixtures.Shopping.result
    envelope=fixtures.Shopping.envelope

    def test_three_turns_save_actual_accepted_evidence(self):
        calls=[]
        def provider(instruction,payload):
            calls.append(payload)
            prefs={**payload['preferences'],'budget_cents':3000000 if len(calls)>1 else 2500000,'budget_kind':'vehicle','min_seats':5}
            return self.envelope(self.result(preferences=prefs))
        target=Path(self.tmp.name)/'evidence'
        with patch('backend.showcase_ai.provider_call',side_effect=provider):
            self.assertTrue(verify('a',target))
        self.assertEqual(len(calls),3)
        self.assertEqual(len(calls[1]['history']),2)
        record=json.loads((target/'actual-results.json').read_text())
        self.assertTrue(record['accepted'])
        self.assertEqual(len(record['turns']),3)
        self.assertTrue(all(t['application_response']['task_id'] for t in record['turns']))

    def test_rejection_keeps_raw_synthetic_response_and_stops_without_retry(self):
        target=Path(self.tmp.name)/'evidence'
        prefs={**self.result()['preferences'],'budget_cents':2500000,'budget_kind':'vehicle','min_seats':5}
        bad=self.envelope(self.result(preferences=prefs,answer='Invented price $99,999.'))
        with patch('backend.showcase_ai.provider_call',return_value=bad) as provider:
            self.assertFalse(verify('a',target))
        self.assertEqual(provider.call_count,1)
        record=json.loads((target/'actual-results.json').read_text())
        self.assertFalse(record['accepted'])
        self.assertEqual(record['turns'][0]['safe_rejection']['rejection']['reason'],'unsupported_number')
        self.assertEqual(record['turns'][0]['provider_response'],bad)
