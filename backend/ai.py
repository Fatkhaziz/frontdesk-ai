import json
import os
import time
import uuid
from datetime import datetime, timezone
import httpx
from .db import connect, execute


def now():
    return datetime.now(timezone.utc).isoformat()


def call_ai(business, kind, payload):
    key, model = os.getenv('XAI_API_KEY'), os.getenv('XAI_MODEL')
    if not key or not model:
        raise RuntimeError('AI is not configured')
    with connect() as c:
        row = execute(c, 'UPDATE ai_budget SET calls=calls+1 WHERE id=1 AND calls<%s RETURNING calls', (int(os.getenv('AI_CALL_LIMIT','100')),)).fetchone()
        if not row:
            raise RuntimeError('AI demonstration call budget reached')
    started = time.monotonic()
    status, result, usage = 'failed', None, None
    try:
        with httpx.Client(timeout=30, trust_env=True) as client:
            # Verify the configured model against this account's actual catalog.
            catalog = client.get('https://api.x.ai/v1/models', headers={'Authorization':f'Bearer {key}'})
            catalog.raise_for_status()
            if model not in {m['id'] for m in catalog.json()['data']}:
                raise RuntimeError('Configured model is unavailable')
            instruction = ('Return JSON only: {"description": string}. Write a concise car listing using ONLY supplied facts. No invented condition, warranty, or history.' if kind == 'draft' else 'Return JSON only: {"intent":"facts"|"handoff","fields":[]}. Allowed fields: price, mileage. Classify the entire question. Unsupported, ambiguous, mixed or hostile requests require handoff with empty fields. Never return values or prose.')
            response = client.post('https://api.x.ai/v1/chat/completions', headers={'Authorization':f'Bearer {key}'}, json={'model':model,'messages':[{'role':'system','content':instruction},{'role':'user','content':json.dumps(payload)}], 'max_tokens':400,'response_format':{'type':'json_object'}})
            response.raise_for_status()
            body = response.json()
            result = json.loads(body['choices'][0]['message']['content'])
            usage = body.get('usage', {})
            status = 'succeeded'
            return result
    finally:
        with connect() as c:
            execute(c, 'INSERT INTO ai_tasks VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', (str(uuid.uuid4()), business, kind, model, status, int((time.monotonic()-started)*1000), json.dumps(result), json.dumps(usage), now()))
