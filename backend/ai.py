import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
import httpx
from .db import connect, execute
from .spending import reserve_attempt


def now():
    return datetime.now(timezone.utc).isoformat()


def call_ai(business, kind, payload, listing_id=None):
    key, model = os.getenv('XAI_API_KEY'), os.getenv('XAI_MODEL')
    if not key or not model:
        raise RuntimeError('AI is not configured')
    if kind == 'draft':
        payload = {**payload, 'price_usd': f"{payload['price'] / 100:.2f}"}
        del payload['price']
    instruction = ('Return JSON only: {"description": string}. Write a short car listing of at most 60 words using ONLY supplied facts. price_usd is USD dollars. Include the USD currency label. No invented condition, warranty, or history.' if kind == 'draft' else 'Return JSON only: {"intent":"facts"|"handoff","fields":[]}. Allowed fields: price, mileage. Classify the entire question. Unsupported, ambiguous, mixed or hostile requests require handoff with empty fields. Never return values or prose.')
    task_id = str(uuid.uuid4())
    with connect() as c:
        reserve_attempt(c, task_id, business, kind, instruction, payload, 200)
    started = time.monotonic()
    status, result, usage = 'failed', None, None
    try:
        with httpx.Client(timeout=30, trust_env=True) as client:
            # Verify the configured model against this account's actual catalog.
            catalog = client.get('https://api.x.ai/v1/models', headers={'Authorization':f'Bearer {key}'})
            catalog.raise_for_status()
            if model not in {m['id'] for m in catalog.json()['data']}:
                raise RuntimeError('Configured model is unavailable')
            response = client.post('https://api.x.ai/v1/chat/completions', headers={'Authorization':f'Bearer {key}'}, json={'model':model,'messages':[{'role':'system','content':instruction},{'role':'user','content':json.dumps(payload)}], 'max_tokens':200,'response_format':{'type':'json_object'}})
            response.raise_for_status()
            body = response.json()
            result = json.loads(body['choices'][0]['message']['content'])
            # Never persist arbitrary provider output or metadata as logs.
            raw_usage = body.get('usage') or {}
            usage = {k: v for k, v in raw_usage.items() if k in ('prompt_tokens', 'completion_tokens', 'total_tokens') and type(v) is int and v >= 0} if isinstance(raw_usage, dict) else {}
            response_id = body.get('id')
            safe_id = response_id if isinstance(response_id, str) and re.fullmatch(r'[\w.-]{1,200}', response_id) and response_id != key and not re.search(r'bearer|password|secret|xai-|sk-', response_id, re.I) else None
            usage.update(provider_model=model, provider_response_id=safe_id)
            status = 'succeeded'
            return result
    finally:
        with connect() as c:
            execute(c, 'INSERT INTO ai_tasks VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', (task_id, business, kind, model, status, int((time.monotonic()-started)*1000), None, json.dumps(usage), now()))
            if listing_id:
                execute(c, 'INSERT INTO listing_ai_tasks VALUES (%s,%s,%s)', (task_id, listing_id, business))
