"""Rendered release acceptance with injected Auth/Grok and isolated SQLite.

No .env loading, real sign-in or paid API calls. Screenshots go to /tmp.
"""
import base64
import json
import logging
import os
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
os.chdir(Path(__file__).resolve().parent.parent)
os.environ.update(SUPABASE_URL='https://showcase.invalid',SUPABASE_PUBLISHABLE_KEY='sb_publishable_mock')
from tests.test_shopping import Shopping
from backend.main import app
from backend.shopping import Preferences, eligible
from playwright.sync_api import sync_playwright, expect
import uvicorn


def main():
    logging.disable(logging.CRITICAL)
    fixture=Shopping();fixture.setUp()
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8003,log_level='critical',access_log=False))
    thread=threading.Thread(target=server.run,daemon=True);thread.start()
    for _ in range(100):
        if server.started:break
        time.sleep(.05)
    assert server.started
    def provider(instruction,payload):
        if 'questions' in instruction[:180]:
            return fixture.envelope({'questions':[{'question':'What warranty applies?','reason':'Warranty terms are not in the inventory.','topic':'Warranty'}, {'question':'Is accident history available?','reason':'A history report is not supplied.','topic':'Condition'}]})
        prefs=Preferences.model_validate(payload['preferences'])
        if '25,000' in payload['message']:
            prefs.budget_cents=2500000;prefs.budget_kind='vehicle';prefs.min_seats=5
        if '30,000' in payload['message']:
            prefs.budget_cents=3000000
        # Mock boundary consumes the same explicitly labeled dollar payload as
        # xAI; convert back only for the backend's integer-cent helper here.
        inventory=[{**l,'facts':{**l['facts'],'price':round(float(l['facts']['price_usd'])*100)}} for l in payload['inventory']]
        matches=[l for l in inventory if eligible(l,prefs)]
        lid=matches[0]['id'] if matches else payload['inventory'][0]['id']
        source=next(s for s in payload['sources'] if s['listing_id']==lid and s['id'].endswith(':price'))
        return fixture.envelope({'preferences':prefs.model_dump(),'answer':'The lower-priced option leaves more of your vehicle budget available. Compare seating and mileage before deciding; total costs still need staff confirmation.',
            'follow_up':'Would you prioritize a lower purchase price or additional passenger space?',
            'recommended_ids':[l['id'] for l in matches[:2]],'source_ids':[s['id'] for s in payload['sources'] if any(l['id']==s['listing_id'] for l in matches[:2])][:25]})
    try:
        with patch('backend.showcase_ai.provider_call',side_effect=provider),sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=os.getenv('FRONTDESK_BROWSER_EXECUTABLE') or None)
            context=browser.new_context(viewport={'width':1440,'height':1000});errors=[]
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            def auth(route):
                token=base64.urlsafe_b64encode(json.dumps({'sub':'owner-a','exp':int(time.time())+3600}).encode()).decode().rstrip('=')
                route.fulfill(status=200,content_type='application/json',body=json.dumps({'access_token':'test.'+token+'.test','token_type':'bearer','expires_in':3600,'refresh_token':'mock','user':{'id':'owner-a','aud':'authenticated','email':'owner@example.invalid'}}))
            context.route('https://showcase.invalid/auth/v1/token**',auth)
            page.goto('http://127.0.0.1:8003/')
            page.get_by_label('Email',exact=True).fill('owner@example.invalid');page.get_by_label('Password',exact=True).fill('mock')
            page.get_by_role('button',name='Sign in',exact=True).click()
            expect(page.get_by_role('heading',name='Your front desk')).to_be_visible()
            page.get_by_role('button',name='Owner knowledge',exact=True).click()
            page.get_by_role('button',name='Suggest customer questions with AI').click()
            expect(page.get_by_label('Customer question').first).to_have_value('What warranty applies?')
            page.get_by_label('Owner-provided answer').first.fill('Ask staff for the written warranty terms before purchase.')
            page.get_by_label('How should the receptionist handle it?').first.select_option('approved')
            page.get_by_label('How should the receptionist handle it?').nth(1).select_option('staff')
            page.get_by_role('button',name='Save private knowledge',exact=True).click()
            expect(page.get_by_role('status')).to_contain_text('Private knowledge saved')
            page.get_by_role('checkbox').check();page.get_by_role('button',name='Publish reviewed knowledge',exact=True).click()
            expect(page.get_by_role('status')).to_contain_text('Reviewed knowledge published')
            page.screenshot(path='/tmp/frontdesk-owner-knowledge.png',full_page=True)
            shop=context.new_page();shop.on('pageerror',lambda e:errors.append(str(e)));shop.goto('http://127.0.0.1:8003/shop/a')
            expect(shop.get_by_role('heading',name='Published inventory',exact=True)).to_be_visible()
            shop.screenshot(path='/tmp/frontdesk-shopping-inventory.png',full_page=True)
            shop.get_by_label('Compare this vehicle').first.check();shop.get_by_label('Compare this vehicle').nth(1).check()
            shop.get_by_role('button',name='Compare selected (2)',exact=True).click()
            expect(shop.get_by_text('Listed price difference: $3,000.00.',exact=False)).to_be_visible()
            expect(shop.get_by_role('table')).to_contain_text('Not provided')
            shop.get_by_role('button',name='Find my fit',exact=True).click()
            shop.get_by_label('Your message').fill('My vehicle budget is $25,000 and I need 5 seats for commuting.')
            shop.get_by_role('button',name='Send to AI',exact=True).click()
            expect(shop.get_by_role('log')).to_contain_text('lower-priced option')
            expect(shop.get_by_label('Maximum budget (USD)')).to_have_value('25000')
            expect(shop.get_by_label('Minimum seats')).to_have_value('5')
            shop.get_by_label('Your message').fill('I can raise my vehicle budget to $30,000.')
            shop.get_by_role('button',name='Send to AI',exact=True).click()
            expect(shop.get_by_label('Maximum budget (USD)')).to_have_value('30000')
            shop.screenshot(path='/tmp/frontdesk-shopping-fit.png',full_page=True)
            shop.get_by_role('button',name='Compare',exact=False).filter(has=shop.locator('.count')).click()
            shop.get_by_role('button',name='Refresh comparison',exact=True).click()
            shop.get_by_role('button',name='Explain this comparison with AI',exact=True).click()
            expect(shop.locator('.bubble.assistant')).to_have_count(3)
            expect(shop.get_by_role('status')).to_contain_text('Answer received from live AI')
            expect(shop.get_by_text('Listed price difference: $3,000.00.',exact=False)).to_be_visible()
            shop.evaluate('window.scrollTo(0,0)')
            shop.screenshot(path='/tmp/frontdesk-shopping-comparison.png',full_page=True)
            shop.get_by_role('button',name='Ask staff to follow up',exact=True).click()
            shop.get_by_label('Your question or summary').fill('Please confirm warranty and accident history for these vehicles.')
            shop.get_by_label('Email or phone for follow-up').fill('class-test@example.invalid')
            shop.get_by_role('checkbox',name='I agree to send these details to staff for follow-up.').check()
            shop.get_by_role('button',name='Send inquiry to staff',exact=True).click()
            expect(shop.get_by_role('status')).to_contain_text('Inquiry saved in the staff inbox')
            page.get_by_role('button',name='Inquiries',exact=False).click();page.get_by_role('button',name='Refresh inquiries',exact=True).click()
            expect(page.get_by_text('class-test@example.invalid',exact=False)).to_be_visible()
            page.get_by_label('Status for Vehicle shopping consultation inquiry').select_option('pending')
            expect(page.get_by_role('status')).to_contain_text('Inquiry status saved')
            page.get_by_text('Customer requirements and selected vehicles',exact=True).click()
            expect(page.get_by_text('$30,000.00',exact=True)).to_be_visible()
            page.get_by_role('button',name='System status',exact=True).click()
            expect(page.get_by_role('heading',name='Latest showcase AI requests')).to_be_visible()
            expect(page.get_by_text('mock-completion-123',exact=True).first).to_be_visible()
            page.screenshot(path='/tmp/frontdesk-showcase-evidence.png',full_page=True)
            shop.set_viewport_size({'width':390,'height':844});shop.screenshot(path='/tmp/frontdesk-shopping-mobile.png',full_page=True)
            assert shop.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile page overflow'
            shop.get_by_role('button',name='Inventory',exact=True).click()
            assert shop.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile inventory overflow'
            assert not errors,errors
            print('PASS: rendered owner AI questions/review/publication, public inventory, exact comparison, multi-turn preferences, AI explanation/sources, consented inquiry/context/status, correlated evidence and mobile layout. Auth and provider completions were mocked; no paid calls.')
            browser.close()
    finally:
        server.should_exit=True;thread.join(timeout=5);fixture.tearDown()


if __name__=='__main__':main()
