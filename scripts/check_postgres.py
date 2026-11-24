"""Disposable PostgreSQL integration only. Never load .env or use production data."""
import hashlib
import json
import logging
import os
import uuid
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

import httpx


def main():
    url = os.getenv('DATABASE_URL', '')
    if os.getenv('FRONTDESK_EPHEMERAL_POSTGRES') != '1' or urlsplit(url).hostname not in ('127.0.0.1', 'localhost'):
        raise RuntimeError('Use only the explicitly marked disposable loopback CI database')
    os.environ.update(QUESTION_MODE='ai', DRAFT_AI_ENABLED='0', XAI_API_KEY='mock-only', XAI_MODEL='mock-only', AI_CALL_LIMIT='10')
    logging.disable(logging.CRITICAL)
    from backend.db import connect, execute
    from backend.main import app, identity
    from backend.verify_integration import inspect_database
    from fastapi.testclient import TestClient
    from scripts.rehearse import sample_profile

    # Rehearse upgrading an old schema with records, not just creating an empty DB.
    with connect() as c:
        execute(c, 'CREATE TABLE schema_migrations(name TEXT PRIMARY KEY,sha256 TEXT NOT NULL)')
        for name in ['001_demo.sql', '002_listing_ai_tasks.sql']:
            text = Path('migrations', name).read_text()
            for statement in text.split(';'):
                if statement.strip() and statement.strip().upper() not in ('BEGIN','COMMIT'):
                    execute(c, statement)
            execute(c, 'INSERT INTO schema_migrations VALUES(%s,%s)', (name, hashlib.sha256(text.encode()).hexdigest()))
        execute(c, 'INSERT INTO businesses VALUES(%s,%s)', ('legacy','Synthetic legacy business'))
        execute(c, 'INSERT INTO listings(id,business_id,revision,facts,description) VALUES(%s,%s,1,%s,%s)', ('legacy-listing','legacy','{}','Preserved synthetic record'))
        execute(c, 'INSERT INTO ai_tasks VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)', ('legacy-task','legacy','draft','historical','failed',1,None,None,'2026-01-01'))
        execute(c, 'INSERT INTO listing_ai_tasks VALUES(%s,%s,%s)', ('legacy-task','legacy-listing','legacy'))
        execute(c, 'INSERT INTO inquiries VALUES(%s,%s,%s,%s,%s,%s,%s,%s)', ('legacy-inquiry','legacy','legacy-listing','legacy-key','synthetic@example.invalid','Preserve me','open','2026-01-01'))
        execute(c, 'UPDATE ai_budget SET calls=3 WHERE id=1')
    inspect_database(apply_pending=True)
    member = {'subject':'ci-owner','business_id':'ci-motors','role':'owner'}
    app.dependency_overrides[identity] = lambda: member
    client = TestClient(app)
    profiles = {}
    real_client = httpx.Client

    def provider(request):
        assert request.url.host == 'api.x.ai'
        payload = json.loads(json.loads(request.content)['messages'][1]['content'])
        assert 'PRIVATE-CANARY' not in json.dumps(payload)
        assert 'customer-private@example.invalid' not in json.dumps(payload)
        source = next(s for s in payload['sources'] if s['path'] == 'faqs/0')
        result = {'business_id':payload['business_id'],'revision':payload['revision'],'handoff':False,'claims':[{'source_id':source['id'],'text':source['text']}]}
        return httpx.Response(200,json={'id':'ci-response','usage':{'prompt_tokens':20,'completion_tokens':10,'total_tokens':30},'choices':[{'finish_reason':'stop','message':{'content':json.dumps(result)}}]})

    def ask(handler=provider):
        with patch('backend.business_qa.httpx.Client',side_effect=lambda **kwargs: real_client(transport=httpx.MockTransport(handler))):
            return client.post('/api/public/businesses/'+member['business_id']+'/questions',json={'question':'Could you explain the cancellation terms?'})

    try:
        for business, domain in [('ci-motors','dealership'),('ci-salon','salon'),('ci-studio','photography_studio')]:
            member['business_id'] = business
            with connect() as c:
                execute(c,'INSERT INTO businesses VALUES(%s,%s)',(business,business))
            profile = sample_profile(domain); profiles[business] = profile
            assert client.put('/api/business/profile',json={'expected_revision':0,'profile':profile}).status_code == 200
            assert client.post('/api/business/profile/publish',json={'expected_revision':1,'confirm_approval':True}).status_code == 200
            assert client.get('/api/inquiries').json() == []
            private = {**profile,'about':'PRIVATE-CANARY'}
            assert client.put('/api/business/profile',json={'expected_revision':1,'profile':private}).status_code == 200
            service = profile['services'][0]
            inquiry = {'request_key':str(uuid.uuid4()),'expected_revision':1,'service_id':service['id'],'message':'Explicit synthetic inquiry','contact':'customer-private@example.invalid','answers':{q['id']:'Synthetic answer' for q in service['questions']}}
            assert client.post('/api/public/businesses/'+business+'/inquiries',json=inquiry).status_code == 201
            response = ask(); answer = response.json()
            assert answer['mode'] == 'live_ai' and not answer['handoff'] and answer['revision'] == 1
            assert answer['answer'] == profile['faqs'][0]['answer']
            evidence = client.get('/api/ai/evidence').json()
            assert len(evidence) == 1 and evidence[0]['request_id'] == response.headers['x-request-id']
            assert evidence[0]['task_id'] == answer['task_id'] and evidence[0]['business_id'] == business
            assert evidence[0]['provider_response_id'] == 'ci-response' and evidence[0]['application_outcome'] == 'accepted'
            assert len(client.get('/api/inquiries').json()) == 1
        member['business_id'] = 'ci-motors'
        def invalid(request):
            return httpx.Response(200,json={'choices':[{'finish_reason':'stop','message':{'content':json.dumps({'business_id':'ci-studio','revision':1,'handoff':False,'claims':[]})}}]})
        assert ask(invalid).json()['reason'] == 'invalid_output'
        def stale(request):
            assert client.post('/api/business/profile/publish',json={'expected_revision':2,'confirm_approval':True}).status_code == 200
            return provider(request)
        assert ask(stale).json()['reason'] == 'stale_source'
        assert len(client.get('/api/inquiries').json()) == 1
        with connect() as c:
            assert execute(c,'SELECT calls FROM ai_budget WHERE id=1').fetchone()['calls'] == 8
            assert execute(c,'SELECT count(*) AS n FROM ai_interaction_evidence WHERE task_id=%s',('legacy-task',)).fetchone()['n'] == 0
        inspect_database(apply_pending=True)
        print('PASS: real disposable PostgreSQL upgrade preserved legacy records, cap and old metadata; three business profiles, private/public revisions, explicit inquiries, mocked-provider evidence, tenant isolation, invalid/stale rejection and idempotent migrations.')
    finally:
        app.dependency_overrides.clear()


if __name__ == '__main__':
    main()
