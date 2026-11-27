"""Delivery contract: source-rendered quantities and explicit limited answers."""
import json
import unittest
from unittest.mock import patch

from backend.shopping import Preferences, ShoppingQuestion, catalog, source_list, validate_answer
from backend.ai_rejection import Rejection
from tests import test_shopping as fixtures


class ShoppingDelivery(unittest.TestCase):
    setUp = fixtures.Shopping.setUp
    tearDown = fixtures.Shopping.tearDown
    result = fixtures.Shopping.result
    envelope = fixtures.Shopping.envelope
    ask = fixtures.Shopping.ask

    def test_provider_uses_short_refs_but_customer_and_evidence_use_canonical_ids(self):
        sources = source_list(catalog('a'))
        aliases = {s['id']: f'S{i+1}' for i, s in enumerate(sources)}
        price = self.result()['source_ids'][0]
        mpg = next(s['id'] for s in sources if s['listing_id'] == self.ids[0] and s['id'].endswith(':mpg_combined'))
        result = self.result(answer=f'Its price is [[{aliases[price]}]]; documented economy is [[{aliases[mpg]}]]. Ownership cost still needs confirmation.', source_ids=[aliases[price]])
        with patch('backend.showcase_ai.provider_call', return_value=self.envelope(result)) as provider:
            r = self.client.post('/api/shop/a/assist', json={'message': 'Compare for commuting'})
        self.assertEqual(r.status_code, 200, r.text)
        provider.assert_called_once()
        self.assertEqual(r.json()['answer_mode'], 'ai_explanation')
        self.assertIn('$23,500.00 USD', r.json()['answer'])
        self.assertIn('45.0 combined MPG', r.json()['answer'])
        self.assertNotIn('[[', r.json()['answer'])
        self.assertEqual(set(r.json()['source_ids']), {price, mpg})
        supplied = provider.call_args.args[1]['sources']
        self.assertTrue(all(s['id'].startswith('S') and 'sha256' not in s for s in supplied))
        row = self.client.get('/api/assistant/evidence').json()[0]
        self.assertEqual(row['application_outcome'], 'accepted')
        self.assertEqual(set(row['source_ids']), {price, mpg})
        self.assertTrue(all(not s['id'].startswith('S') for s in row['source_snapshot']))

    def test_bad_numeric_prose_is_never_shown_or_recorded_as_normal_acceptance(self):
        bad = self.result(answer='UNVERIFIED-PROSE: The price is $9,999 and it is guaranteed safe.', follow_up='Will $9,999 work?')
        with patch('backend.showcase_ai.provider_call', return_value=self.envelope(bad)) as provider:
            r = self.client.post('/api/shop/a/assist', json={'message': 'Help me compare'})
        self.assertEqual(r.status_code, 200, r.text)
        provider.assert_called_once()
        delivered = r.json()
        self.assertEqual(delivered['answer_mode'], 'grounded_summary')
        self.assertNotIn('UNVERIFIED-PROSE', delivered['answer'])
        self.assertNotIn('$9,999', delivered['answer'] + delivered['follow_up'])
        self.assertNotIn('guaranteed safe', delivered['answer'])
        self.assertIn('$23,500.00 USD', delivered['answer'])
        row = self.client.get('/api/assistant/evidence').json()[0]
        self.assertEqual(row['provider_outcome'], 'succeeded')
        self.assertEqual(row['application_outcome'], 'accepted_with_limits')
        self.assertEqual(row['rejection']['reason'], 'unsupported_number')
        self.assertTrue(row['source_ids'])
        self.assertNotIn('UNVERIFIED-PROSE', json.dumps(row))

    def test_limited_turn_keeps_validated_needs_for_a_real_followup_path(self):
        old = {**Preferences().model_dump(), 'budget_cents': 2500000, 'budget_kind': 'vehicle', 'min_seats': 5}
        new = {**old, 'budget_cents': 3000000}
        first = self.ask(self.result(preferences=old, answer='It costs $99,999.'), message='My vehicle budget is $25,000. I need five seats.', selected_ids=self.ids)
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(first.json()['answer_mode'], 'grounded_summary')
        self.assertEqual(first.json()['preferences'], old)
        second = self.ask(self.result(preferences=new), message='Raise my vehicle budget to $30,000; retain five seats.', preferences=first.json()['preferences'], selected_ids=self.ids, history=[{'role': 'assistant', 'content': first.json()['answer']}])
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual(second.json()['answer_mode'], 'ai_explanation')
        self.assertEqual(second.json()['preferences'], new)
        self.assertEqual(self.client.get('/api/diagnostics').json()['ai_calls_used'], 2)

    def test_numeric_recovery_does_not_bypass_scope_preferences_or_stale_checks(self):
        for change in ({'source_ids': ['foreign:r1:price']}, {'recommended_ids': ['foreign']}, {'preferences': {**Preferences().model_dump(), 'min_seats': 12}}):
            with self.subTest(change=change):
                self.assertEqual(self.ask(self.result(answer='It costs $99,999.', **change)).status_code, 503)
        bad = self.envelope(self.result(answer='It costs $99,999.'))
        def unpublish(*args):
            self.client.post('/api/listings/' + self.ids[0] + '/unpublish')
            return bad
        with patch('backend.showcase_ai.provider_call', side_effect=unpublish):
            r = self.client.post('/api/shop/a/assist', json={'message': 'Help me compare'})
        self.assertEqual(r.status_code, 409)
        row = self.client.get('/api/assistant/evidence').json()[0]
        self.assertEqual(row['application_outcome'], 'stale_source')
        self.assertEqual(row['source_ids'], [])

    def test_unknown_source_tokens_and_literal_cross_unit_claims_are_not_approved(self):
        self.assertEqual(self.ask(self.result(answer='Its price is [[S9999]].')).status_code, 503)
        data = catalog('a'); sources = source_list(data)
        refs = [s['id'] for s in sources if s['listing_id'] == self.ids[0] and s['id'].endswith((':price', ':mpg_combined'))]
        with self.assertRaises(Rejection):
            validate_answer(self.result(answer='Its price is $45.', source_ids=refs), data, ShoppingQuestion(message='Compare'), sources)

    def test_total_budget_with_unknown_fees_is_not_reported_as_a_match(self):
        prefs = {**Preferences().model_dump(), 'budget_cents': 3000000, 'budget_kind': 'total'}
        r = self.ask(self.result(preferences=prefs, answer='The total price is $99,999.', recommended_ids=[]), message='My total budget is $30,000 including fees.', selected_ids=self.ids)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()['matches'], [])
        self.assertNotIn('Meets your recorded hard requirements', r.json()['answer'])
        self.assertIn('unconfirmed', r.json()['answer'])
