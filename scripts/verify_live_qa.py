"""User-initiated, one-request live check. Default: read-only preflight, no AI call.
Load .env privately in the shell. No credentials or customer content are printed.
"""
import argparse
import hashlib
import json
import logging
import os
from decimal import Decimal
from pathlib import Path

from backend.business import public_profile
from backend.business_qa import input_bytes, MAX_INPUT_BYTES, MAX_OUTPUT_TOKENS, safe_question
from backend.db import connect, execute

MODEL = 'grok-4.20-0309-non-reasoning'
INPUT_RATE = Decimal('1.25')
OUTPUT_RATE = Decimal('2.50')
QUESTION = 'Could you explain your cancellation policy?'


def estimate_cost(byte_count):
    # Conservative estimate: one input token per UTF-8 byte plus framing allowance.
    # Provider tokenization/billing remains authoritative, not this estimate.
    return (Decimal(byte_count + 4096) * INPUT_RATE + Decimal(MAX_OUTPUT_TOKENS) * OUTPUT_RATE) / Decimal(1000000)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--business', required=True, help='Published business ID, not a contact or secret')
    parser.add_argument('--remaining-usd', type=Decimal, help='Current prepaid balance read privately from the provider dashboard')
    parser.add_argument('--authorized-remaining-usd', type=Decimal, help='Unused portion of the original $5 authorization; account balance alone is insufficient')
    parser.add_argument('--billing-checked', action='store_true', help='Attest current prices match, no auto-top-up/overage charge would occur, and no other paid work is running')
    parser.add_argument('--execute-one-paid-request', action='store_true')
    args = parser.parse_args()
    logging.disable(logging.CRITICAL)
    if os.getenv('XAI_MODEL') != MODEL:
        raise RuntimeError('Configured model differs from the priced model. Stop and review current pricing; do not change model automatically.')
    with connect() as c:
        # Refuse missing/modified migrations before any provider call.
        for filename in ['003_business_reception.sql', '004_ai_interaction_evidence.sql', '005_shopping_assistant.sql']:
            row = execute(c, 'SELECT sha256 FROM schema_migrations WHERE name=%s', (filename,)).fetchone()
            expected = hashlib.sha256(Path('migrations', filename).read_bytes()).hexdigest()
            if not row or row['sha256'] != expected:
                raise RuntimeError('Required migration is missing or differs. Stop for schema review.')
        profile = public_profile(c, args.business)
        calls = execute(c, 'SELECT calls FROM ai_budget WHERE id=1').fetchone()['calls']
    limit = int(os.getenv('AI_CALL_LIMIT', '10'))
    byte_count = input_bytes(args.business, profile, QUESTION)
    cost = estimate_cost(byte_count)
    ceiling = estimate_cost(MAX_INPUT_BYTES)
    if calls >= limit or byte_count > MAX_INPUT_BYTES or not safe_question(QUESTION):
        raise RuntimeError('Attempt budget or input preflight failed; no provider request made.')
    print(f'Published revision: {profile["revision"]}; attempts: {calls}/{limit}; input: {byte_count} bytes; output cap: {MAX_OUTPUT_TOKENS} tokens.')
    print(f'Estimated conservative cost: ${cost:.6f}; rates: $1.25/M input, $2.50/M output; global endpoint, no tools or retries.')
    print(f'Budget checks reserve the full estimated ceiling ${ceiling:.6f}, allowing for a publication change before execution.')
    print('Recheck https://docs.x.ai/developers/pricing and the correct team at https://console.x.ai/ before proceeding.')
    if not args.execute_one_paid_request:
        print('READ-ONLY PREFLIGHT. No provider request made. Execute requires both remaining budgets, billing attestation and an interactive confirmation.')
        return 0
    balances = [args.remaining_usd, args.authorized_remaining_usd]
    if not args.billing_checked or any(b is None or not b.is_finite() or b < ceiling for b in balances) or not Decimal('0') < args.authorized_remaining_usd <= Decimal('5') or ceiling > Decimal('0.05'):
        raise RuntimeError('Budget/billing checks failed; no provider request made.')
    if not os.getenv('XAI_API_KEY'):
        raise RuntimeError('Provider key is missing; no request made.')
    import httpx
    with httpx.Client(timeout=15) as client:
        catalog = client.get('https://api.x.ai/v1/models', headers={'Authorization': 'Bearer ' + os.environ['XAI_API_KEY']})
        catalog.raise_for_status()
        if MODEL not in {item['id'] for item in catalog.json()['data']}:
            raise RuntimeError('Priced model is unavailable to this account; stop without inference.')
    if input(f'Type SEND ONE to authorize one paid request estimated at ${cost:.6f}, up to ${ceiling:.6f}: ') != 'SEND ONE':
        print('Cancelled. No provider request made.')
        return 0
    # Process-local override only; never edits .env or raises the cap.
    os.environ['QUESTION_MODE'] = 'ai'
    os.environ['DRAFT_AI_ENABLED'] = '0'
    from fastapi.testclient import TestClient
    from backend.main import app
    response = TestClient(app).post('/api/public/businesses/' + args.business + '/questions', json={'question': QUESTION})
    value = response.json()
    # Print only identifiers and outcomes; inspect published answer in owner evidence.
    print(json.dumps({k: value.get(k) for k in ['request_id', 'task_id', 'mode', 'handoff', 'revision', 'reason']}))
    print('One application request completed. Inspect /api/ai/evidence and provider usage; do not retry automatically.')
    return 0 if response.status_code == 200 and value.get('mode') == 'live_ai' else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print('Live verification stopped safely (' + type(exc).__name__ + '). No automatic retry. Inspect configuration privately.')
        raise SystemExit(1) from None
