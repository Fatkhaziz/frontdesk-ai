"""Real transactions, mocked network: a rejected reservation never calls xAI."""
import os
import json
from unittest.mock import patch
from fastapi import HTTPException
from backend.db import connect, execute
from backend import spending
import unittest
from tests import test_shopping as fixtures


class Spending(unittest.TestCase):
    result = fixtures.Shopping.result
    envelope = fixtures.Shopping.envelope
    ask = fixtures.Shopping.ask
    def setUp(self):
        fixtures.Shopping.setUp(self)
        self.budget_env = patch.dict(os.environ, {
            'AI_PREPARATION_BUDGET_USD':'1.00', 'AI_AUTHORIZED_REMAINING_USD':'4.97',
            'AI_PRESENTATION_RESERVE_USD':'3.50', 'XAI_MODEL':spending.PRICED_MODEL})
        self.budget_env.start()

    def tearDown(self):
        self.budget_env.stop()
        fixtures.Shopping.tearDown(self)

    def test_all_reservations_survive_new_configuration_without_reset(self):
        self.assertEqual(self.ask().status_code, 200)
        with connect() as c:
            before=spending.status(c)
            self.assertGreater(before['conservative_reserved_usd'],0)
            self.assertGreaterEqual(before['conservative_remaining_usd'],3.50)
        with patch.dict(os.environ, {'AI_PREPARATION_BUDGET_USD':'.90'}):
            with connect() as c:
                after=spending.status(c)
        self.assertEqual(before,after)

    def test_cap_rejection_rolls_back_money_and_never_calls_provider(self):
        with connect() as c:
            spending.initialize(c)
            execute(c,'UPDATE ai_budget SET calls=30 WHERE id=1')
        with patch('backend.showcase_ai.provider_call') as provider:
            response=self.client.post('/api/shop/a/assist',json={'message':'Help me choose'})
        self.assertEqual(response.status_code,429)
        provider.assert_not_called()
        with connect() as c:
            self.assertEqual(spending.status(c)['conservative_reserved_usd'],0)
            self.assertEqual(execute(c,'SELECT COUNT(*) AS n FROM ai_spend_reservations').fetchone()['n'],0)

    def test_preparation_budget_cannot_use_presentation_reserve(self):
        with connect() as c:
            spending.initialize(c)
            execute(c,'UPDATE ai_spend_budget SET preparation_reserved_micro_usd=1000000 WHERE id=1')
        with patch('backend.showcase_ai.provider_call') as provider:
            r=self.client.post('/api/shop/a/assist',json={'message':'Help me choose'})
        self.assertEqual(r.status_code,429)
        provider.assert_not_called()
        with connect() as c:
            self.assertEqual(execute(c,'SELECT calls FROM ai_budget WHERE id=1').fetchone()['calls'],0)

    def test_failure_is_reserved_and_pricing_model_mismatch_is_blocked(self):
        with patch('backend.showcase_ai.provider_call',side_effect=RuntimeError('private-provider-error')):
            self.assertEqual(self.client.post('/api/shop/a/assist',json={'message':'Help me choose'}).status_code,503)
        with connect() as c:
            reserved=spending.status(c)['conservative_reserved_usd']
            self.assertGreater(reserved,0)
        with patch.dict(os.environ,{'XAI_MODEL':'unpriced-model'}), patch('backend.showcase_ai.provider_call') as provider:
            self.assertEqual(self.client.post('/api/shop/a/assist',json={'message':'Help me choose'}).status_code,503)
            provider.assert_not_called()
        with connect() as c:
            self.assertEqual(spending.status(c)['conservative_reserved_usd'],reserved)

    def test_budget_diagnostics_are_owner_only(self):
        self.assertTrue(self.client.get('/api/diagnostics').json()['spending']['configured'])
        self.member['role']='staff'
        self.assertEqual(self.client.get('/api/diagnostics').status_code,403)
