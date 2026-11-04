import json
import logging
import os
import time
import traceback
import uuid
from pathlib import Path
from typing import Literal
import httpx
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from .db import connect, execute
from .config import supabase_config, question_mode, ai_enabled
from .ai import call_ai, now
from .demo import fields_for_question
from .errors import error_category

app = FastAPI(title='FrontDesk AI feasibility demo')
log = logging.getLogger('frontdesk')
logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)

@app.middleware('http')
async def trace(request: Request, next_handler):
    rid = str(uuid.uuid4())
    start = time.monotonic()
    try:
        response = await next_handler(request)
    except Exception as exc:
        frames = traceback.extract_tb(exc.__traceback__)
        origin = frames[-1].name if frames else 'unknown'
        log.error('request_id=%s error_type=%s category=%s sqlstate=%s origin=%s',
                  rid, type(exc).__name__, error_category(exc), getattr(exc, 'sqlstate', None), origin)
        response = JSONResponse({'detail':'Service unavailable; check configuration', 'request_id':rid}, status_code=503)
    response.headers['X-Request-ID'] = rid
    response.headers['Cache-Control'] = 'no-store'
    log.info('request_id=%s method=%s route=%s status=%s duration_ms=%d', rid, request.method, request.scope.get('route').path if request.scope.get('route') else 'unmatched', response.status_code, (time.monotonic()-start)*1000)
    return response


def identity(request: Request):
    token = request.headers.get('authorization','')
    if not token.startswith('Bearer '):
        raise HTTPException(401, 'Sign in required')
    url, key = supabase_config()
    if not url or not key:
        raise HTTPException(503, 'Authentication is not configured')
    # Supabase Auth validates the token, including expiry and project membership.
    with httpx.Client(timeout=10) as client:
        r = client.get(url+'/auth/v1/user', headers={'Authorization':token,'apikey':key})
    if r.status_code != 200:
        raise HTTPException(401, 'Invalid or expired sign-in')
    user = r.json()
    if not user.get('email_confirmed_at'):
        raise HTTPException(403, 'Verify your email')
    with connect() as c:
        member = execute(c, 'SELECT * FROM memberships WHERE subject=%s AND active=TRUE',(user['id'],)).fetchone()
    if not member:
        raise HTTPException(403, 'Ask the administrator to provision your business membership')
    return dict(member)


def owner(member=Depends(identity)):
    if member['role'] != 'owner':
        raise HTTPException(403, 'Owner required')
    return member

class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Facts(Strict):
    make: str = Field(min_length=1,max_length=80)
    model: str = Field(min_length=1,max_length=80)
    year: int = Field(ge=1886,le=2100)
    price: int = Field(ge=0,le=1000000000,description='USD cents')
    mileage: int = Field(ge=0,le=10000000)
    availability: Literal['available','reserved','sold'] = 'available'

class Car(Strict):
    facts: Facts
    description: str = Field(default='',max_length=3000)

class Edit(Car):
    expected_revision: int = Field(gt=0)

class Revision(Strict):
    expected_revision: int = Field(gt=0)

class Approval(Revision):
    confirm_approval: Literal[True]

class Question(Strict):
    question: str = Field(min_length=1,max_length=1000)

class Inquiry(Strict):
    request_key: uuid.UUID
    contact: str = Field(min_length=3,max_length=300)
    message: str = Field(min_length=1,max_length=1000)

class Status(Strict):
    status: Literal['open','pending','resolved']


def record(c, lid, member=None, public=False):
    sql, args = 'SELECT * FROM listings WHERE id=%s', [lid]
    if member:
        sql += ' AND business_id=%s'; args.append(member['business_id'])
    if public:
        sql += ' AND published IS NOT NULL'
    row = execute(c, sql, args).fetchone()
    if not row:
        raise HTTPException(404, 'Listing not found')
    return dict(row)


def serialize(row):
    return {**row,'facts':json.loads(row['facts']),'published':json.loads(row['published']) if row['published'] else None}

@app.get('/health')
def health():
    return {'status':'running'}

@app.get('/api/config')
def config():
    url, key = supabase_config()
    return {'supabaseUrl':url,'supabaseKey':key,'questionMode':question_mode(),'aiEnabled':ai_enabled()}

@app.get('/api/listings')
def listings(m=Depends(identity)):
    with connect() as c:
        return [serialize(dict(r)) for r in execute(c,'SELECT * FROM listings WHERE business_id=%s ORDER BY id',(m['business_id'],)).fetchall()]

@app.post('/api/listings',status_code=201)
def create(body:Car,m=Depends(identity)):
    lid = str(uuid.uuid4())
    with connect() as c:
        execute(c,'INSERT INTO listings(id,business_id,revision,facts,description) VALUES(%s,%s,1,%s,%s)',(lid,m['business_id'],body.facts.model_dump_json(),body.description))
        return serialize(record(c,lid,m))

@app.get('/api/listings/{lid}')
def get_listing(lid:str,m=Depends(identity)):
    with connect() as c:
        return serialize(record(c,lid,m))


def update_draft(lid,body,m):
    with connect() as c:
        record(c,lid,m)
        r = execute(c,'UPDATE listings SET facts=%s,description=%s,revision=revision+1,approved_revision=NULL,approved_by=NULL WHERE id=%s AND business_id=%s AND revision=%s RETURNING id',(body.facts.model_dump_json(),body.description,lid,m['business_id'],body.expected_revision)).fetchone()
        if not r: raise HTTPException(409,'Draft changed; reload and review')
        return serialize(record(c,lid,m))

@app.patch('/api/listings/{lid}')
def edit(lid:str,body:Edit,m=Depends(identity)):
    return update_draft(lid,body,m)

@app.post('/api/listings/{lid}/draft')
def draft(lid:str,body:Revision,m=Depends(identity)):
    if not ai_enabled():
        raise HTTPException(503,'AI drafting is disabled. Enter a manual description, save, review and approve it.')
    with connect() as c: row = record(c,lid,m)
    if row['revision'] != body.expected_revision: raise HTTPException(409,'Stale revision')
    try:
        result = call_ai(m['business_id'],'draft',json.loads(row['facts']))
        if set(result) != {'description'} or not isinstance(result['description'],str) or not result['description'].strip(): raise ValueError()
        body2 = Edit(facts=json.loads(row['facts']),description=result['description'],expected_revision=body.expected_revision)
    except Exception:
        raise HTTPException(503,'AI draft unavailable; existing draft preserved')
    return update_draft(lid,body2,m)

@app.post('/api/listings/{lid}/publish')
def publish(lid:str,body:Approval,m=Depends(owner)):
    with connect() as c:
        row = record(c,lid,m)
        if not row['description'].strip(): raise HTTPException(422,'Review a description before publishing')
        snapshot = json.dumps({'facts':json.loads(row['facts']),'description':row['description']})
        r = execute(c,'UPDATE listings SET published=%s,published_revision=revision,approved_revision=revision,approved_by=%s WHERE id=%s AND business_id=%s AND revision=%s RETURNING id',(snapshot,m['subject'],lid,m['business_id'],body.expected_revision)).fetchone()
        if not r: raise HTTPException(409,'Stale approval; reload and review')
        if row['published_revision'] != body.expected_revision:
            execute(c,'INSERT INTO audit_events VALUES(%s,%s,%s,%s,%s,%s,%s)',(str(uuid.uuid4()),m['business_id'],m['subject'],lid,body.expected_revision,'publish',now()))
    return {'url':'/listing/'+lid,'revision':body.expected_revision}

@app.post('/api/listings/{lid}/unpublish')
def unpublish(lid:str,m=Depends(owner)):
    with connect() as c:
        record(c,lid,m)
        execute(c,'UPDATE listings SET published=NULL,published_revision=NULL WHERE id=%s',(lid,))
    return {'unpublished':True}

@app.get('/api/public/{lid}')
def public(lid:str):
    with connect() as c: row=record(c,lid,public=True)
    return {**json.loads(row['published']),'revision':row['published_revision']}

@app.post('/api/public/{lid}/questions')
def question(lid:str,body:Question):
    with connect() as c: row=record(c,lid,public=True)
    mode=question_mode()
    fallback={'handoff':True,'answer':'I cannot answer that from the approved facts. You can submit an inquiry to staff.','mode':mode}
    if mode == 'demo':
        fields=fields_for_question(body.question)
        if not fields: return fallback
    else:
        try:
            intent=call_ai(row['business_id'],'question',{'question':body.question})
            if set(intent) != {'intent','fields'} or intent['intent'] != 'facts' or not isinstance(intent['fields'],list) or not intent['fields'] or any(f not in ('price','mileage') for f in intent['fields']): return fallback
            fields=intent['fields']
        except Exception:
            return fallback
    # Re-read after the network call; edits and publication may occur during inference.
    current=public(lid)
    facts=current['facts']
    answers={'price':f"The price is ${facts['price']/100:,.2f} USD.",'mileage':f"The mileage is {facts['mileage']:,} miles."}
    return {'handoff':False,'answer':' '.join(answers[f] for f in dict.fromkeys(fields)),'revision':current['revision'],'mode':mode}

@app.post('/api/public/{lid}/inquiries',status_code=201)
def inquiry(lid:str,body:Inquiry):
    with connect() as c:
        row=record(c,lid,public=True)
        existing=execute(c,'SELECT * FROM inquiries WHERE business_id=%s AND request_key=%s',(row['business_id'],str(body.request_key))).fetchone()
        if existing:
            if existing['listing_id'] != lid or existing['message'] != body.message or existing['contact'] != body.contact: raise HTTPException(409,'Request key already used')
            return {'id':existing['id'],'status':existing['status']}
        iid=str(uuid.uuid4())
        execute(c,'INSERT INTO inquiries VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',(iid,row['business_id'],lid,str(body.request_key),body.contact,body.message,'open',now()))
    return {'id':iid,'status':'open'}

@app.get('/api/inquiries')
def inbox(m=Depends(identity)):
    with connect() as c: return [dict(r) for r in execute(c,'SELECT * FROM inquiries WHERE business_id=%s ORDER BY created_at DESC',(m['business_id'],)).fetchall()]

@app.patch('/api/inquiries/{iid}')
def inquiry_status(iid:str,body:Status,m=Depends(identity)):
    with connect() as c:
        r=execute(c,'UPDATE inquiries SET status=%s WHERE id=%s AND business_id=%s RETURNING id',(body.status,iid,m['business_id'])).fetchone()
        if not r: raise HTTPException(404,'Inquiry not found')
    return {'status':body.status}

@app.get('/api/diagnostics')
def diagnostics(m=Depends(owner)):
    with connect() as c:
        execute(c,'SELECT 1').fetchone()
        last=execute(c,'SELECT model,kind,status,duration_ms,result,usage,created_at FROM ai_tasks WHERE business_id=%s ORDER BY created_at DESC LIMIT 1',(m['business_id'],)).fetchone()
    return {'database':'connected','question_mode':question_mode(),'ai_enabled':ai_enabled(),'last_actual_ai_request':dict(last) if last else None}

assets=Path(__file__).resolve().parent.parent/'frontend/dist'
if (assets/'assets').exists(): app.mount('/assets',StaticFiles(directory=assets/'assets'),name='assets')
@app.get('/')
@app.get('/listing/{lid}')
def frontend(lid:str=''):
    if not (assets/'index.html').exists(): raise HTTPException(503,'Build frontend first')
    return FileResponse(assets/'index.html')
