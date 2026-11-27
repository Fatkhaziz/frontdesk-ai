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
            return {**self.envelope(self.result(preferences=prefs)), 'raw_provider_only': 'PRIVATE-DIAGNOSTIC'}
        root=Path(self.tmp.name)/'captures'
        target=root/'20261127T020000Z'
        with patch('backend.showcase_ai.provider_call',side_effect=provider):
            self.assertTrue(verify('a',target))
        self.assertEqual(len(calls),3)
        self.assertEqual(len(calls[1]['history']),2)
        record=json.loads((target/'actual-results.json').read_text())
        self.assertTrue(record['accepted'])
        self.assertEqual(len(record['turns']),3)
        self.assertTrue(all(t['application_response']['task_id'] for t in record['turns']))
        with patch.dict('os.environ', {'FRONTDESK_LOCAL_SHOWCASE': '1'}), \
             patch('backend.showcase_rehearsal.captures_directory', return_value=root), \
             patch('backend.showcase_ai.provider_call') as provider:
            saved=self.client.get('/api/assistant/saved-rehearsal')
            self.assertEqual(saved.status_code,200,saved.text)
            replay=saved.json()['run']['turns']
            self.assertEqual([t['outcome'] for t in replay], ['accepted']*3)
            self.assertEqual([t['answer'] for t in replay], [t['application_response']['answer'] for t in record['turns']])
            self.assertEqual(replay[1]['budget_cents'], 3000000)
            self.assertTrue(replay[0]['sources'])
            self.assertNotIn('PRIVATE-DIAGNOSTIC', saved.text)
            self.member['business_id']='b'
            self.assertIsNone(self.client.get('/api/assistant/saved-rehearsal').json()['run'])
            self.member['role']='staff'
            self.assertEqual(self.client.get('/api/assistant/saved-rehearsal').status_code,403)
            from backend.main import app
            app.dependency_overrides.clear()
            self.assertEqual(self.client.get('/api/assistant/saved-rehearsal').status_code,401)
            provider.assert_not_called()

    def test_rejection_keeps_raw_synthetic_response_and_stops_without_retry(self):
        root=Path(self.tmp.name)/'captures'
        target=root/'20261127T020000Z'
        prefs={**self.result()['preferences'],'budget_cents':2500000,'budget_kind':'vehicle','min_seats':5}
        bad=self.envelope(self.result(preferences=prefs,source_ids=['foreign:price']))
        with patch('backend.showcase_ai.provider_call',return_value=bad) as provider:
            self.assertFalse(verify('a',target))
        self.assertEqual(provider.call_count,1)
        record=json.loads((target/'actual-results.json').read_text())
        self.assertFalse(record['accepted'])
        self.assertEqual(record['turns'][0]['safe_rejection']['rejection']['reason'],'unapproved_source')
        self.assertEqual(record['turns'][0]['provider_response'],bad)
        with patch.dict('os.environ', {'FRONTDESK_LOCAL_SHOWCASE': '1'}), patch('backend.showcase_rehearsal.captures_directory', return_value=root):
            replay=self.client.get('/api/assistant/saved-rehearsal').json()['run']['turns'][0]
        self.assertEqual(replay['outcome'], 'invalid_output')
        self.assertEqual(replay['rejection']['reason'], 'unapproved_source')
        self.assertNotIn('answer', replay)

    def test_limited_summary_is_not_reported_as_full_live_success_or_retried(self):
        target=Path(self.tmp.name)/'evidence'
        prefs={**self.result()['preferences'],'budget_cents':2500000,'budget_kind':'vehicle','min_seats':5}
        with patch('backend.showcase_ai.provider_call',return_value=self.envelope(self.result(preferences=prefs,answer='Invented price $99,999.'))) as provider:
            self.assertFalse(verify('a',target))
        provider.assert_called_once()
        record=json.loads((target/'actual-results.json').read_text())
        self.assertFalse(record['accepted'])
        self.assertTrue(record['turns'][0]['delivered_with_limits'])
        self.assertEqual(record['turns'][0]['application_response']['answer_mode'],'grounded_summary')
