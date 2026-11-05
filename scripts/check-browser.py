"""Browser rehearsal against isolated SQLite, mocked Supabase Auth and mocked Grok.
Run after building with Playwright available; never loads .env or touches demo data.
"""
import base64
import json
import logging
import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch

os.environ.update(TESTING='1', QUESTION_MODE='ai', DRAFT_AI_ENABLED='1', XAI_API_KEY='mock-only', XAI_MODEL='mock-only', SUPABASE_URL='https://demo.invalid', SUPABASE_PUBLISHABLE_KEY='sb_publishable_mock')
from fastapi import Request, HTTPException
from backend.main import app, identity
from backend.db import connect, execute
from fastapi.testclient import TestClient
from playwright.sync_api import sync_playwright, expect
import uvicorn

logging.disable(logging.CRITICAL)
with tempfile.TemporaryDirectory() as tmp:
    os.environ['DATABASE_URL']='sqlite:///'+tmp+'/browser.sqlite'
    with connect() as c:
        c.executescript(Path('migrations/001_demo.sql').read_text().split('-- Application data')[0]+'COMMIT;')
        c.executescript(Path('migrations/002_listing_ai_tasks.sql').read_text().split('REVOKE')[0]+'COMMIT;')
        execute(c,'INSERT INTO businesses VALUES(%s,%s)',('browser','Demo Motors'))
    def test_identity(request: Request):
        if not request.headers.get('authorization','').startswith('Bearer '):
            raise HTTPException(401,'Sign in required')
        return {'business_id':'browser','role':'owner','subject':'browser-owner'}
    app.dependency_overrides[identity]=test_identity
    api=TestClient(app)
    headers={'Authorization':'Bearer browser-test'}
    facts={'make':'Toyota','model':'Camry','year':2022,'price':2350000,'mileage':42000,'availability':'available'}
    ids=[]
    for _ in range(2):
        r=api.post('/api/listings',headers=headers,json={'facts':facts,'description':'Approved demonstration Camry.'});ids.append(r.json()['id'])
        api.post('/api/listings/'+ids[-1]+'/publish',headers=headers,json={'expected_revision':1,'confirm_approval':True})
    def mock_ai(business,kind,payload,*args):
        return {'description':'2022 Toyota Camry. $23,500 USD. 42,000 miles. Available.'} if kind=='draft' else {'intent':'facts','fields':['price','mileage'] if 'mileage' in payload['question'].lower() else ['price']}
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8001,log_level='critical',access_log=False))
    thread=threading.Thread(target=server.run,daemon=True);thread.start()
    for _ in range(100):
        if server.started:break
        time.sleep(.05)
    assert server.started
    try:
        with patch('backend.main.call_ai',side_effect=mock_ai),sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            context=browser.new_context()
            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(type(e).__name__))
            def login_route(route):
                payload=base64.urlsafe_b64encode(json.dumps({'sub':'browser-owner','exp':int(time.time())+3600}).encode()).decode().rstrip('=')
                route.fulfill(status=200,content_type='application/json',body=json.dumps({'access_token':'test.'+payload+'.test','token_type':'bearer','expires_in':3600,'refresh_token':'mock-only','user':{'id':'browser-owner','aud':'authenticated','email':'owner@example.invalid'}}))
            context.route('https://demo.invalid/auth/v1/token**',login_route)
            def login():
                page.get_by_label('Email',exact=True).fill('owner@example.invalid');page.get_by_label('Password',exact=True).fill('mock-only');page.get_by_role('button',name='Sign in',exact=True).click()
                expect(page.get_by_role('heading',name='Your front desk')).to_be_visible()
            page.goto('http://127.0.0.1:8001/');login()
            expect(page.get_by_role('button',name='Listings',exact=True)).to_have_attribute('aria-current','page')
            expect(page.get_by_label('Price (USD)',exact=True)).to_have_value('23500')
            selected=context.request.get('http://127.0.0.1:8001/api/listings',headers=headers).json()
            latest=max(selected,key=lambda c:c['published_at']);lid=latest['id']
            page.get_by_label('Make',exact=True).fill(' ');page.get_by_role('button',name='Save vehicle details').click()
            expect(page.get_by_role('status')).to_have_text('Enter the vehicle make.')
            assert 'Pydantic' not in page.locator('body').inner_text()
            page.get_by_label('Make',exact=True).fill('Toyota')
            page.get_by_label('Price (USD)',exact=True).fill('24500');page.get_by_role('button',name='Save vehicle details').click()
            expect(page.get_by_role('status')).to_contain_text('Private draft saved')
            assert context.request.get('http://127.0.0.1:8001/api/public/'+lid).json()['facts']['price']==2350000
            assert context.request.get('http://127.0.0.1:8001/api/listings/'+lid,headers=headers).json()['facts']['price']==2450000
            page.reload();login();expect(page.get_by_label('Price (USD)',exact=True)).to_have_value('24500')
            page.get_by_label('Price (USD)',exact=True).fill('23500');page.get_by_role('button',name='2 AI description',exact=True).click();page.get_by_role('button',name='Generate with Grok').click()
            expect(page.get_by_role('status')).to_contain_text('Grok description saved')
            page.get_by_label('Listing description').fill('Owner-reviewed Camry. $23,500 USD and 42,000 miles.')
            page.get_by_role('button',name='Save description').click();expect(page.get_by_role('status')).to_contain_text('Description saved')
            page.get_by_role('checkbox').check();page.get_by_role('button',name='Publish approved revision').click();expect(page.get_by_role('status')).to_contain_text('Approved revision published')
            expect(page.get_by_role('link',name='View public page')).to_be_visible()
            page.screenshot(path='/private/tmp/frontdesk-dashboard.png',full_page=True)
            public=context.new_page();public.goto('http://127.0.0.1:8001/listing/'+lid)
            expect(public.get_by_role('heading',name='2022 Toyota Camry',exact=True)).to_be_visible()
            public.get_by_label('Your question',exact=True).fill('Price and mileage?');public.get_by_role('button',name='Ask question').click()
            expect(public.get_by_role('log')).to_contain_text('The price is $23,500.00 USD. The mileage is 42,000 miles.')
            public.get_by_label('Your question',exact=True).fill('Accident history?');public.get_by_role('button',name='Ask question').click()
            expect(public.get_by_role('heading',name='Let our staff help')).to_be_visible()
            public.get_by_label('Your email or phone').fill('browser@example.invalid');public.get_by_role('button',name='Send inquiry to staff').click()
            expect(public.get_by_role('status')).to_contain_text('staff inbox')
            page.get_by_role('button',name='Inquiries',exact=False).click();page.get_by_role('button',name='Refresh inquiries').click()
            expect(page.get_by_text('browser@example.invalid',exact=False)).to_be_visible()
            page.get_by_label('Status for 2022 Toyota Camry inquiry').select_option('pending');expect(page.get_by_role('status')).to_contain_text('Inquiry status saved')
            page.get_by_role('button',name='System status',exact=True).click();expect(page.get_by_role('heading',name='System status')).to_be_visible();expect(page.get_by_text('Supabase Auth',exact=True)).to_be_visible()
            page.get_by_role('button',name='Listings',exact=True).click()
            page.get_by_text('Listing management',exact=True).click()
            page.once('dialog',lambda dialog:dialog.dismiss());page.get_by_role('button',name='Delete listing',exact=True).click()
            assert context.request.get('http://127.0.0.1:8001/api/public/'+lid).status==200
            page.once('dialog',lambda dialog:dialog.accept());page.get_by_role('button',name='Delete listing',exact=True).click();expect(page.get_by_role('status')).to_have_text('Listing deleted.')
            assert context.request.get('http://127.0.0.1:8001/api/public/'+lid).status==404
            assert context.request.get('http://127.0.0.1:8001/api/inquiries',headers=headers).json()==[]
            public.goto('http://127.0.0.1:8001/listing/'+ids[0]);public.set_viewport_size({'width':390,'height':844})
            expect(public.get_by_role('heading',name='Ask about this vehicle')).to_be_visible()
            assert public.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            page.set_viewport_size({'width':390,'height':844});expect(page.get_by_role('button',name='+ New listing')).to_be_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            assert not errors,errors
            print('Browser PASS: mocked sign-in, default selection, dollar entry, friendly validation, private snapshot isolation, refresh/re-login, mocked Grok/edit/save/approve/publish, public chat/handoff, inbox/status, delete cancel/confirm/cleanup, mobile widths; zero runtime errors. No real data or paid AI used.')
            browser.close()
    finally:
        server.should_exit=True;thread.join(timeout=5);app.dependency_overrides.clear()
