"""Bounded server-side xAI gateway. Intent is durable before the network call.

Provider completion and application acceptance are deliberately separate. Never
store headers, credentials, raw chat or arbitrary provider output in evidence.
"""
import json
import os
import re
import time
import uuid

import httpx
from fastapi import HTTPException

from .ai import now
from .config import question_mode
from .db import connect, execute
from .ai_rejection import Rejection
from .spending import reserve_attempt


def provider_call(instruction, payload):
    """The actual paid API call; replaced by an explicit mock only in tests."""
    key, model = os.getenv('XAI_API_KEY'), os.getenv('XAI_MODEL')
    with httpx.Client(timeout=35, trust_env=True) as client:
        response = client.post(
            'https://api.x.ai/v1/chat/completions',
            headers={'Authorization': f'Bearer {key}'},
            json={'model': model, 'messages': [
                {'role': 'system', 'content': instruction},
                {'role': 'user', 'content': json.dumps(payload)}],
                'temperature': 0.2, 'max_tokens': 1800,
                'response_format': {'type': 'json_object'}},
        )
        response.raise_for_status()
        return response.json()


def run_ai(business, operation, request_id, sources, instruction, payload, validate, still_current):
    key, model = os.getenv('XAI_API_KEY'), os.getenv('XAI_MODEL')
    if question_mode() != 'ai' or not key or not model:
        raise HTTPException(503, 'Live AI is not enabled. Inventory and factual comparison still work without AI.')
    if len(json.dumps(payload).encode()) > 48000:
        raise HTTPException(422, 'Too much context. Shorten the message or reduce the selected inventory.')
    task = str(uuid.uuid4())
    with connect() as c:
        reserve_attempt(c, task, business, operation, instruction, payload)
        execute(c, 'INSERT INTO ai_tasks VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (task, business, operation, model, 'started', None, None, None, now()))
        execute(c, 'INSERT INTO assistant_runs(task_id,business_id,request_id,operation,source_snapshot,provider_outcome,application_outcome) VALUES(%s,%s,%s,%s,%s,%s,%s)',
                (task, business, request_id, operation, json.dumps(sources), 'started', 'pending'))
    started = time.monotonic()
    provider, application, provider_id, provider_model, usage, refs = 'failed', 'provider_error', None, None, {}, []
    stage, diagnostic = 'provider', None
    try:
        body = provider_call(instruction, payload)
        provider = 'succeeded'
        application = 'invalid_output'
        stage = 'envelope'
        if not isinstance(body, dict):
            raise Rejection(stage, 'invalid_envelope')
        raw_id = body.get('id')
        if isinstance(raw_id, str) and re.fullmatch(r'[\w.-]{1,200}', raw_id) and raw_id != key and not re.search(r'bearer|password|secret|xai-|sk-', raw_id, re.I):
            provider_id = raw_id
        raw_model = body.get('model')
        if isinstance(raw_model, str) and re.fullmatch(r'grok-[A-Za-z0-9._-]{1,120}', raw_model) and raw_model != key:
            provider_model = raw_model
        raw_usage = body.get('usage') or {}
        if isinstance(raw_usage, dict):
            usage = {k: v for k, v in raw_usage.items() if k in ('prompt_tokens', 'completion_tokens', 'total_tokens') and type(v) is int and v >= 0}
        choices = body.get('choices')
        if not isinstance(choices, list) or len(choices) != 1 or not isinstance(choices[0], dict):
            raise Rejection(stage, 'invalid_envelope')
        choice = choices[0]
        if choice.get('finish_reason') != 'stop':
            raise Rejection(stage, 'incomplete_output')
        message = choice.get('message')
        if not isinstance(message, dict) or not isinstance(message.get('content'), str):
            raise Rejection(stage, 'invalid_envelope')
        stage = 'json'
        # Reject duplicate JSON keys and non-finite numbers rather than silently
        # accepting whichever value a permissive decoder happens to retain.
        def unique_pairs(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise Rejection('json', 'invalid_json')
                result[key] = value
            return result
        def invalid_constant(value):
            raise Rejection('json', 'invalid_json')
        decoded = json.loads(message['content'], object_pairs_hook=unique_pairs, parse_constant=invalid_constant)
        stage = 'shape'
        result = validate(decoded)
        refs = result.get('source_ids', [])
        application = 'stale_source'
        stage = 'publication'
        if not still_current():
            raise Rejection(stage, 'stale_source')
        application = 'accepted'
        if result.get('answer_mode') == 'grounded_summary':
            saved = result['validation_rejection']
            diagnostic = Rejection(saved['stage'], saved['reason'], saved.get('field'), saved.get('source_id')).diagnostic(sources)
            application = 'accepted_with_limits'
        return {**result, 'task_id': task, 'request_id': request_id, 'mode': 'live_ai'}
    except Exception as exc:
        if isinstance(exc, Rejection):
            diagnostic = exc.diagnostic(sources)
        elif isinstance(exc, json.JSONDecodeError):
            diagnostic = Rejection('json', 'invalid_json').diagnostic(sources)
        elif isinstance(exc, httpx.TimeoutException):
            diagnostic = Rejection('provider', 'provider_timeout').diagnostic(sources)
        elif isinstance(exc, httpx.HTTPStatusError):
            reason = 'provider_rate_limit' if exc.response.status_code == 429 else 'provider_http_error'
            diagnostic = Rejection('provider', reason).diagnostic(sources)
        else:
            diagnostic = Rejection(stage, 'provider_error' if stage == 'provider' else 'internal_error').diagnostic(sources)
        if application == 'stale_source':
            raise HTTPException(409, 'Published information changed during the request. Refresh the inventory before trying again.') from None
        raise HTTPException(503, 'The AI response could not be accepted. No facts were changed. You can compare the published facts or contact staff.') from None
    finally:
        elapsed = int((time.monotonic() - started) * 1000)
        with connect() as c:
            execute(c, 'UPDATE ai_tasks SET model=%s,status=%s,duration_ms=%s,usage=%s,result=%s WHERE id=%s AND business_id=%s',
                    (provider_model or model, provider, elapsed, json.dumps({**usage, 'provider_response_id': provider_id, 'requested_model': model, 'provider_model': provider_model}), json.dumps({'rejection': diagnostic}) if diagnostic else None, task, business))
            execute(c, 'UPDATE assistant_runs SET source_ids=%s,provider_response_id=%s,token_usage=%s,latency_ms=%s,provider_outcome=%s,application_outcome=%s WHERE task_id=%s AND business_id=%s',
                    (json.dumps(refs if application in ('accepted', 'accepted_with_limits') else []), provider_id, json.dumps(usage), elapsed, provider, application, task, business))
