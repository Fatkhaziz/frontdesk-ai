"""Read-only showcase preflight; explicit flag sends ONE paid shopping request.

Load the existing .env privately. This does not raise the cap or test password
sign-in. Provider prices are pinned and must be rechecked before execution.
"""
import argparse
import json
import logging
import os
from decimal import Decimal

from backend.db import connect, execute
from backend.shopping import catalog, source_list, Preferences, SHOP_INSTRUCTION

MODEL='grok-4.20-0309-non-reasoning'
INPUT_RATE=Decimal('1.25')
OUTPUT_RATE=Decimal('2.50')
QUESTION='My vehicle-price budget is $25,000. I need 5 seats for commuting. Explain which published options match and what information is missing.'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--business',required=True)
    parser.add_argument('--remaining-usd',type=Decimal)
    parser.add_argument('--authorized-remaining-usd',type=Decimal)
    parser.add_argument('--billing-checked',action='store_true',help='Confirm current standard model rates, correct prepaid team, auto-recharge/overage disabled, and no concurrent paid work.')
    parser.add_argument('--execute-one-paid-request',action='store_true')
    args=parser.parse_args()
    logging.disable(logging.CRITICAL)
    data=catalog(args.business)
    if len(data['listings'])<2:
        raise RuntimeError('Publish at least two reviewed vehicles first.')
    with connect() as c:
        calls=execute(c,'SELECT calls FROM ai_budget WHERE id=1').fetchone()['calls']
        execute(c,'SELECT task_id FROM assistant_runs LIMIT 1').fetchall()
    limit=int(os.getenv('AI_CALL_LIMIT','10'))
    ceiling=(Decimal(48000+len(SHOP_INSTRUCTION.encode())+4096)*INPUT_RATE+Decimal(1800)*OUTPUT_RATE)/Decimal(1000000)
    print(f'Published vehicles: {len(data["listings"])}; current attempt count: {calls}/{limit}.')
    print(f'Priced model: {MODEL}; conservative estimated request ceiling: ${ceiling:.6f}. No retries or external tools.')
    print('Current billing/balance must be checked at https://console.x.ai/ and https://docs.x.ai/developers/pricing .')
    if not args.execute_one_paid_request:
        print('READ-ONLY PREFLIGHT. No xAI call made. Current Mac sign-in and real inference remain separate checks.')
        return 0
    values=[args.remaining_usd,args.authorized_remaining_usd]
    if not args.billing_checked or any(v is None or not v.is_finite() or v<ceiling for v in values) or not Decimal('0')<args.authorized_remaining_usd<=Decimal('5'):
        raise RuntimeError('Remaining credit and original authorization are required. No request sent.')
    if calls>=limit:
        raise RuntimeError('Attempt cap reached. No request sent and no cap was changed.')
    if os.getenv('XAI_MODEL')!=MODEL or not os.getenv('XAI_API_KEY'):
        raise RuntimeError('Priced model and existing provider key are required. No request sent.')
    import httpx
    with httpx.Client(timeout=15) as client:
        response=client.get('https://api.x.ai/v1/models',headers={'Authorization':'Bearer '+os.environ['XAI_API_KEY']})
        response.raise_for_status()
        if MODEL not in {m['id'] for m in response.json()['data']}:
            raise RuntimeError('Configured model is not available to this account. No inference sent.')
    os.environ['QUESTION_MODE']='ai'
    from backend.main import app
    from fastapi.testclient import TestClient
    response=TestClient(app).post('/api/shop/'+args.business+'/assist',json={'message':QUESTION})
    result=response.json()
    if response.status_code!=200 or result.get('mode')!='live_ai':
        print('Request was not accepted. Inspect the saved application outcome; do not retry automatically.')
        return 1
    print(json.dumps({k:result.get(k) for k in ['mode','request_id','task_id','preferences','recommended_ids']},indent=2))
    print('Answer:',result['answer'])
    print('Follow-up:',result['follow_up'])
    print('One real shopping request accepted. Inspect System status and provider usage. Real owner question generation and browser password sign-in are still separate checks.')
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except Exception as e:
        print('Showcase live check stopped ('+type(e).__name__+'). No automatic retry; inspect private configuration and the documented checks.')
        raise SystemExit(1) from None
