"""Three explicit real shopping turns; save synthetic responses privately, no retry.

Called only by launch-showcase.sh --practice --verify-live. The ordinary launch
never sends inference. This is provider/database integration, not browser Auth.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.db import connect, execute
from backend.shopping import catalog, Preferences
from backend import showcase_ai
from backend.spending import PRICED_MODEL, status

QUESTIONS = [
    'My vehicle-price budget is $25,000. I need five seats for commuting and prefer fuel economy. Compare my selected vehicles, explain missing information and ask one useful follow-up.',
    'Raise my vehicle-price budget to $30,000 and retain five seats. Which selected option fits my priorities better now?',
    'Is this a fair price? Explain what you can verify and what information you would still need.',
]


def verify(business, destination):
    data=catalog(business)
    cars=sorted(data['listings'],key=lambda l:(l['facts']['model'] not in ('Compact Hatch','City Hybrid'),l['facts']['model']))[:2]
    if len(cars)!=2:
        raise RuntimeError('At least two published vehicles are required; no request sent.')
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    journal={'created_at':datetime.now(timezone.utc).isoformat(),'business_id':business,'selected_ids':[l['id'] for l in cars],
             'note':'Actual fixed synthetic integration requests. Not a browser sign-in test. Raw model output is private diagnostic evidence, not accepted application content.', 'turns':[]}
    target=destination/'actual-results.json';history=[];prefs=Preferences().model_dump();provider=showcase_ai.provider_call
    def capture(instruction,payload):
        result=provider(instruction,payload)  # Calls the real gateway; no simulated completion.
        journal['turns'][-1]['provider_response']=result
        target.write_text(json.dumps(journal,indent=2));target.chmod(0o600)
        return result
    client=TestClient(app)
    with patch('backend.showcase_ai.provider_call',side_effect=capture):
        for question in QUESTIONS:
            turn={'question':question};journal['turns'].append(turn)
            r=client.post('/api/shop/'+business+'/assist',json={'message':question,'preferences':prefs,'history':history,'selected_ids':journal['selected_ids']})
            result=r.json();turn.update(http_status=r.status_code,request_id=r.headers.get('x-request-id'),application_response=result)
            if r.status_code!=200:
                with connect() as c:
                    e=execute(c,'SELECT t.result FROM ai_tasks t JOIN assistant_runs a ON a.task_id=t.id AND a.business_id=t.business_id WHERE a.request_id=%s',(turn['request_id'],)).fetchone()
                turn['safe_rejection']=json.loads(e['result']) if e and e['result'] else None
                journal['accepted']=False;target.write_text(json.dumps(journal,indent=2));target.chmod(0o600)
                print('Live acceptance STOPPED after a rejected request. No retry or follow-up sent. Private evidence:',target)
                return False
            prefs=result['preferences'];history += [{'role':'user','content':question},{'role':'assistant','content':(result['answer']+' '+result.get('follow_up',''))[:1600]}]
            history=history[-8:];turn['accepted']=True
            target.write_text(json.dumps(journal,indent=2));target.chmod(0o600)
    journal['accepted']=True;target.write_text(json.dumps(journal,indent=2));target.chmod(0o600)
    print('PASS: three real AI turns accepted (needs, changed budget, fair-price question). Evidence:',target)
    print('Browser password sign-in and owner-question generation remain separate UI checks.')
    return True


def main():
    if os.getenv('XAI_MODEL')!=PRICED_MODEL or not os.getenv('XAI_API_KEY'):
        raise RuntimeError('The existing priced provider configuration is required; no request sent.')
    with connect() as c:
        budget=status(c)
        if not budget.get('configured') or budget['mode']!='preparation':
            raise RuntimeError('Explicit preparation allowance is required; no request sent.')
        owners=execute(c,"SELECT DISTINCT business_id FROM memberships WHERE active=TRUE AND role='owner'").fetchall()
    if len(owners)!=1:
        raise RuntimeError('A single configured owner business is required; no request sent.')
    os.umask(0o077)
    folder=Path.home()/'Desktop'/'FrontDesk-AI-Live-Acceptance'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    return 0 if verify(owners[0]['business_id'],folder) else 1


if __name__=='__main__':
    raise SystemExit(main())
