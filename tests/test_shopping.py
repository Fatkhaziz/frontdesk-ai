"""Showcase acceptance and failure tests. All provider completions are mocked."""
import copy
import json
import logging
import os
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from backend.main import app, identity
from backend.db import connect, execute
from backend.shopping import Preferences, source_list, catalog


class Shopping(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'TESTING': '1', 'DATABASE_URL': 'sqlite:///' + self.tmp.name + '/test.db',
                         'QUESTION_MODE': 'ai', 'XAI_API_KEY': 'mock-secret-never-log', 'XAI_MODEL': 'mock-model', 'AI_CALL_LIMIT': '30'})
        self.env.start()
        with connect() as c:
            for path in sorted(Path('migrations').glob('*.sql')):
                c.executescript(path.read_text().split('REVOKE')[0].split('-- Application data')[0] + 'COMMIT;')
            for b in ['a','b']:
                execute(c, 'INSERT INTO businesses VALUES(%s,%s)', (b, 'Synthetic Motors ' + b))
        self.member = {'subject': 'owner-a', 'business_id': 'a', 'role': 'owner'}
        app.dependency_overrides[identity] = lambda: self.member
        self.client = TestClient(app)
        self.facts = {'make':'Example','model':'Commuter','year':2022,'price':2350000,'mileage':42000,'availability':'available',
                      'seats':5,'body_style':'sedan','fuel_type':'hybrid','drivetrain':'fwd','mpg_combined':45}
        self.ids=[]
        for price, model, seats in [(2350000,'Commuter',5),(2650000,'Family',7)]:
            f={**self.facts,'price':price,'model':model,'seats':seats}
            r=self.client.post('/api/listings',json={'facts':f,'description':'Synthetic example, not a real offer.'})
            self.assertEqual(r.status_code,201)
            lid=r.json()['id'];self.ids.append(lid)
            self.assertEqual(self.client.post('/api/listings/'+lid+'/publish',json={'expected_revision':1,'confirm_approval':True}).status_code,200)

    def tearDown(self):
        app.dependency_overrides.clear();self.env.stop();self.tmp.cleanup()

    def result(self, **changes):
        sources=source_list(catalog('a'))
        price=next(s for s in sources if s['listing_id']==self.ids[0] and s['id'].endswith(':price'))
        return {'preferences':Preferences().model_dump(),'answer':'The listed vehicle price is $23,500. Taxes and fees are not established.',
                'follow_up':'Is your budget for the vehicle price or the total including taxes and fees?',
                'recommended_ids':[self.ids[0]],'source_ids':[price['id']],**changes}

    def envelope(self, result):
        return {'id':'mock-completion-123','usage':{'prompt_tokens':70,'completion_tokens':40,'total_tokens':110},
                'choices':[{'finish_reason':'stop','message':{'content':json.dumps(result)}}]}

    def ask(self,result=None,**body):
        with patch('backend.showcase_ai.provider_call',return_value=self.envelope(result or self.result())):
            return self.client.post('/api/shop/a/assist',json={'message':'Help me choose a car',**body})

    def test_comparison_uses_public_facts_and_exact_cent_arithmetic(self):
        self.client.patch('/api/listings/'+self.ids[0],json={'facts':{**self.facts,'price':9990000},'description':'PRIVATE-CANARY','expected_revision':1})
        r=self.client.post('/api/shop/a/compare',json={'listing_ids':self.ids,'preferences':{'budget_cents':2500000,'budget_kind':'vehicle'}})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json()['price_difference_cents'],300000)
        self.assertEqual([l['budget_difference_cents'] for l in r.json()['listings']],[150000,-150000])
        self.assertNotIn('PRIVATE-CANARY',r.text)
        self.assertEqual(r.json()['mode'],'calculated')

    def test_total_budget_unknown_fees_and_missing_specs_are_not_matches(self):
        r=self.client.post('/api/shop/a/compare',json={'listing_ids':self.ids,'preferences':{'budget_cents':3000000,'budget_kind':'total','drivetrain':'awd'}}).json()
        checks=r['listings'][0]['checks']
        self.assertTrue(any(c['label']=='Total cost including taxes and fees' and c['status']=='unknown' for c in checks))
        self.assertTrue(any(c['label']=='Drivetrain' and c['status']=='mismatch' for c in checks))

    def test_foreign_unpublished_and_duplicate_comparison_denied(self):
        self.assertEqual(self.client.post('/api/shop/b/compare',json={'listing_ids':self.ids}).status_code,404)
        self.assertEqual(self.client.post('/api/shop/a/compare',json={'listing_ids':[self.ids[0]]*2}).status_code,422)
        self.client.post('/api/listings/'+self.ids[1]+'/unpublish')
        self.assertEqual(self.client.post('/api/shop/a/compare',json={'listing_ids':self.ids}).status_code,404)

    def test_owner_knowledge_revision_approval_and_private_isolation(self):
        card={'id':'warranty','question':'What warranty is provided?','answer':'Contact staff for the written warranty terms.','status':'approved','source_note':'Owner-reviewed policy','reason':''}
        self.assertEqual(self.client.put('/api/dealer/knowledge',json={'expected_revision':0,'cards':[card]}).status_code,200)
        self.assertEqual(self.client.get('/api/shop/a').json()['knowledge'],[])
        self.assertEqual(self.client.post('/api/dealer/knowledge/publish',json={'expected_revision':1,'confirm_approval':False}).status_code,422)
        self.assertEqual(self.client.post('/api/dealer/knowledge/publish',json={'expected_revision':1,'confirm_approval':True}).status_code,200)
        card['answer']='PRIVATE-CANARY'
        self.client.put('/api/dealer/knowledge',json={'expected_revision':1,'cards':[card]})
        self.assertNotIn('PRIVATE-CANARY',self.client.get('/api/shop/a').text)
        self.assertEqual(self.client.post('/api/dealer/knowledge/publish',json={'expected_revision':1,'confirm_approval':True}).status_code,409)
        self.assertEqual(self.client.put('/api/dealer/knowledge',json={'expected_revision':0,'cards':[]}).status_code,409)

    def test_roles_and_business_scoping(self):
        self.ask()
        self.member={'subject':'owner-b','business_id':'b','role':'owner'}
        self.assertEqual(self.client.get('/api/assistant/evidence').json(),[])
        self.assertEqual(self.client.get('/api/dealer/knowledge').json()['revision'],0)
        self.member['role']='staff'
        self.assertEqual(self.client.get('/api/dealer/knowledge').status_code,403)
        self.assertEqual(self.client.get('/api/assistant/evidence').status_code,403)
        app.dependency_overrides.clear()
        self.assertEqual(self.client.get('/api/assistant/evidence').status_code,401)
        self.assertEqual(self.client.get('/api/shop/a').status_code,200)

    def test_live_path_records_correlated_metadata_not_chat_or_secrets(self):
        r=self.ask(message='Help me choose for my commute')
        self.assertEqual(r.status_code,200,r.text)
        record=self.client.get('/api/assistant/evidence').json()[0]
        self.assertEqual(record['provider_response_id'],'mock-completion-123')
        self.assertEqual(record['request_id'],r.headers['x-request-id'])
        self.assertEqual(record['task_id'],r.json()['task_id'])
        self.assertEqual(record['application_outcome'],'accepted')
        self.assertEqual(record['token_usage']['total_tokens'],110)
        self.assertNotIn('my commute',json.dumps(record))
        self.assertNotIn('mock-secret-never-log',json.dumps(record))

    def test_natural_budget_update_and_backend_filtered_matches(self):
        prefs={**Preferences().model_dump(),'budget_cents':2500000,'budget_kind':'vehicle'}
        r=self.ask(self.result(preferences=prefs),message='My vehicle budget is $25k')
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(r.json()['matches'],[self.ids[0]])
        self.assertEqual(r.json()['preferences']['budget_cents'],2500000)

    def test_over_budget_recommendation_or_invented_preferences_rejected(self):
        prefs={**Preferences().model_dump(),'budget_cents':2500000,'budget_kind':'vehicle'}
        for result in [self.result(preferences=prefs,recommended_ids=[self.ids[1]]),self.result(preferences={**prefs,'budget_cents':4000000}),self.result(preferences={**prefs,'body_style':'suv'})]:
            r=self.ask(result,message='My vehicle budget is $25k')
            self.assertEqual(r.status_code,503,r.text)
        records=self.client.get('/api/assistant/evidence').json()
        self.assertTrue(all(r['provider_outcome']=='succeeded' and r['application_outcome']=='invalid_output' for r in records))

    def test_foreign_sources_invented_numbers_and_truncated_output_rejected(self):
        for result in [self.result(source_ids=['foreign-business:price']),self.result(answer='This vehicle costs $9,999.'),self.result(recommended_ids=['foreign-vehicle'])]:
            self.assertEqual(self.ask(result).status_code,503)
        envelope=self.envelope(self.result());envelope['choices'][0]['finish_reason']='length'
        with patch('backend.showcase_ai.provider_call',return_value=envelope):
            self.assertEqual(self.client.post('/api/shop/a/assist',json={'message':'Help me'}).status_code,503)

    def test_provider_failure_is_durable_and_budget_never_silently_resets(self):
        with patch('backend.showcase_ai.provider_call',side_effect=RuntimeError('secret-error')):
            r=self.client.post('/api/shop/a/assist',json={'message':'Help me'})
        self.assertEqual(r.status_code,503);self.assertNotIn('secret-error',r.text)
        record=self.client.get('/api/assistant/evidence').json()[0]
        self.assertEqual(record['provider_outcome'],'failed');self.assertEqual(record['application_outcome'],'provider_error')
        with connect() as c:execute(c,'UPDATE ai_budget SET calls=30')
        with patch('backend.showcase_ai.provider_call') as call:
            self.assertEqual(self.client.post('/api/shop/a/assist',json={'message':'Help me'}).status_code,429)
            call.assert_not_called()

    def test_stale_publication_rejects_but_private_edit_does_not(self):
        def update_public(*args):
            self.client.post('/api/listings/'+self.ids[0]+'/unpublish')
            return self.envelope(self.result())
        # Build the envelope before the source is unpublished.
        envelope=self.envelope(self.result())
        def stale(*args):
            self.client.post('/api/listings/'+self.ids[0]+'/unpublish');return envelope
        with patch('backend.showcase_ai.provider_call',side_effect=stale):
            self.assertEqual(self.client.post('/api/shop/a/assist',json={'message':'Help me'}).status_code,409)
        self.assertEqual(self.client.get('/api/assistant/evidence').json()[0]['application_outcome'],'stale_source')

    def test_contacts_not_sent_to_provider(self):
        with patch('backend.showcase_ai.provider_call') as provider:
            for q in ['My email is a@example.invalid','password is something','my phone is 1234567890']:
                self.assertEqual(self.client.post('/api/shop/a/assist',json={'message':q}).status_code,422)
            provider.assert_not_called()

    def test_required_features_and_old_constraints_cannot_disappear(self):
        prefs={**Preferences().model_dump(),'budget_cents':2500000,'budget_kind':'vehicle','required_features':['Heated seats']}
        self.assertEqual(self.ask(self.result(preferences=prefs),message='Help me choose',preferences=prefs).status_code,503)
        # Neither example fixture provides a verified heated-seat feature.
        relaxed={**prefs,'required_features':[]}
        self.assertEqual(self.ask(self.result(preferences=relaxed),message='Help me choose',preferences=prefs).status_code,503)

    def test_actual_gateway_request_is_bounded_and_has_no_retry(self):
        import httpx
        from backend.showcase_ai import provider_call
        real_client=httpx.Client;seen=[]
        def handler(request):
            seen.append(request)
            self.assertEqual(str(request.url),'https://api.x.ai/v1/chat/completions')
            payload=json.loads(request.content)
            self.assertEqual(payload['max_tokens'],1800)
            self.assertEqual(payload['model'],'mock-model')
            self.assertEqual(payload['response_format'],{'type':'json_object'})
            self.assertEqual(request.headers['Authorization'],'Bearer mock-secret-never-log')
            return httpx.Response(503,json={'error':'Provider unavailable'})
        with patch('backend.showcase_ai.httpx.Client',side_effect=lambda **kwargs:real_client(transport=httpx.MockTransport(handler))):
            with self.assertRaises(httpx.HTTPStatusError):provider_call('System instruction',{'facts':'approved'})
        self.assertEqual(len(seen),1)

    def test_example_seed_is_idempotent_and_preserves_existing_rows_and_cap(self):
        from scripts.seed_showcase import seed
        with connect() as c:
            execute(c,'INSERT INTO memberships(subject,business_id,role,active) VALUES(%s,%s,%s,TRUE)',('owner-a','a','owner'))
            execute(c,'UPDATE ai_budget SET calls=9')
        seed('a');seed('a')
        self.assertEqual(len(self.client.get('/api/listings').json()),6)
        with connect() as c:
            self.assertEqual(execute(c,'SELECT calls FROM ai_budget').fetchone()['calls'],9)
        self.assertEqual(self.client.get('/api/public/'+self.ids[0]).json()['facts']['price'],2350000)

    def test_suggestions_are_private_and_do_not_invent_answers(self):
        result={'questions':[{'question':'Is a history report available?','reason':'No history record is supplied.','topic':'Condition'}]}
        with patch('backend.showcase_ai.provider_call',return_value=self.envelope(result)):
            r=self.client.post('/api/dealer/knowledge/suggest',json={'expected_revision':0})
        self.assertEqual(r.status_code,200,r.text)
        self.assertEqual(self.client.get('/api/dealer/knowledge').json()['cards'],[])
        self.assertEqual(self.client.get('/api/shop/a').json()['knowledge'],[])
        self.assertEqual(self.client.get('/api/assistant/evidence').json()[0]['operation'],'knowledge_suggestions')

    def test_explicit_followup_context_idempotency_and_staff_status(self):
        body={'request_key':str(uuid.uuid4()),'message':'Please confirm warranty terms.','contact':'synthetic@example.invalid','consent':True,'preferences':{'budget_cents':2500000},'listing_ids':self.ids}
        r=self.client.post('/api/shop/a/inquiries',json=body)
        self.assertEqual(r.status_code,201,r.text)
        self.assertEqual(self.client.post('/api/shop/a/inquiries',json=body).json()['id'],r.json()['id'])
        inquiry=self.client.get('/api/inquiries').json()[0]
        self.assertEqual(inquiry['context']['preferences']['budget_cents'],2500000)
        self.assertEqual(len(inquiry['context']['listings']),2)
        self.assertEqual(self.client.patch('/api/shopping/inquiries/'+r.json()['id'],json={'status':'pending'}).status_code,200)
        self.member['business_id']='b'
        self.assertEqual(self.client.get('/api/inquiries').json(),[])
        self.assertEqual(self.client.patch('/api/shopping/inquiries/'+r.json()['id'],json={'status':'resolved'}).status_code,404)
        self.assertEqual(self.client.post('/api/shop/a/inquiries',json={**body,'consent':False}).status_code,422)


    def test_provider_reported_model_is_recorded_separately_from_requested_alias(self):
        envelope = {**self.envelope(self.result()), 'model': 'grok-resolved-version'}
        with patch('backend.showcase_ai.provider_call', return_value=envelope):
            response = self.client.post('/api/shop/a/assist', json={'message': 'Help me compare'})
        self.assertEqual(response.status_code, 200)
        record = self.client.get('/api/assistant/evidence').json()[0]
        self.assertEqual(record['model'], 'grok-resolved-version')
        self.assertEqual(record['requested_model'], 'mock-model')
        self.assertEqual(record['provider_model'], 'grok-resolved-version')
        with connect() as c:
            task = execute(c, 'SELECT model,usage FROM ai_tasks WHERE id=%s', (record['task_id'],)).fetchone()
        self.assertEqual(task['model'], 'grok-resolved-version')
        self.assertEqual(json.loads(task['usage'])['requested_model'], 'mock-model')

    def test_missing_provider_model_remains_unknown(self):
        self.assertEqual(self.ask().status_code, 200)
        record = self.client.get('/api/assistant/evidence').json()[0]
        self.assertEqual(record['requested_model'], 'mock-model')
        self.assertIsNone(record['provider_model'])


if __name__=='__main__':unittest.main()
