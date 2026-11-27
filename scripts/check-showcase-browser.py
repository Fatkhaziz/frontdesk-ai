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
    first_reply=threading.Event()
    def provider(instruction,payload):
        if 'questions' in instruction[:180]:
            return fixture.envelope({'questions':[{'question':'What warranty applies?','reason':'Warranty terms are not in the inventory.','topic':'Warranty'}, {'question':'Is accident history available?','reason':'A history report is not supplied.','topic':'Condition'}]})
        prefs=Preferences.model_validate(payload['preferences'])
        if '25,000' in payload['message']:
            prefs.budget_cents=2500000;prefs.budget_kind='vehicle';prefs.min_seats=5
            assert first_reply.wait(10), 'The browser did not show the pending message'
        if '30,000' in payload['message']:
            prefs.budget_cents=3000000
        # Mock boundary consumes the same explicitly labeled dollar payload as
        # xAI; convert back only for the backend's integer-cent helper here.
        inventory=[{**l,'facts':{**l['facts'],'price':round(float(l['facts']['price_usd'])*100)}} for l in payload['inventory']]
        matches=[l for l in inventory if eligible(l,prefs)]
        lid=matches[0]['id'] if matches else payload['inventory'][0]['id']
        source=next(s for s in payload['sources'] if s['listing_id']==lid and s['label'].endswith(' · price'))
        policy=next((s for s in payload['sources'] if not s.get('value_text')),None)
        policy_citation=f" [[{policy['id']}]]" if policy else ''
        cited=[s['id'] for s in payload['sources'] if s['label'].endswith(' · price') and any(l['id']==s['listing_id'] for l in matches[:2])]
        answer=[{'text': f"The lower-priced option leaves more of your vehicle budget available. Its listed price is [[{source['id']}]]. Total costs still need staff confirmation.",
                 'source_ids': cited}]
        if policy:
            answer.append({'text': 'Ask staff for the written warranty terms.'+policy_citation, 'source_ids': [policy['id']]})
        if 'citation recovery' in payload['message']:
            answer.append({'text':'UNVERIFIED-PROSE: This warranty is established [[S9999]].', 'source_ids':[]})
        return fixture.envelope({'preferences':prefs.model_dump(),'answer':answer,
            'follow_up':'Would you prioritize a lower purchase price or additional passenger space?',
            'recommended_ids':[l['id'] for l in matches[:2]],'source_ids':[]})
    try:
        with patch('backend.showcase_ai.provider_call',side_effect=provider) as grok, sync_playwright() as p:
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
            calls=grok.call_count
            expect(page.get_by_role('navigation',name='Dashboard sections')).not_to_contain_text('Request log')
            expect(page.get_by_role('navigation',name='Dashboard sections')).not_to_contain_text('Showcase')
            with context.expect_page() as faq_tab:
                page.get_by_role('link',name='See published answers',exact=True).click()
            faq=faq_tab.value
            expect(faq.get_by_role('heading',name='Common questions')).to_be_visible()
            faq.get_by_text('What warranty applies?',exact=True).click()
            expect(faq.get_by_text('Ask staff for the written warranty terms before purchase.',exact=True)).to_be_visible()
            faq.get_by_text('Is accident history available?',exact=True).click()
            expect(faq.get_by_text('Staff can confirm this.',exact=False)).to_be_visible()
            faq.close()
            with context.expect_page() as customer_tab:
                page.get_by_role('link',name='Open customer site',exact=True).click()
            shop=customer_tab.value
            shop.on('pageerror',lambda e:errors.append(str(e)))
            comparison_requests=[]
            shop.on('request', lambda request: comparison_requests.append(request) if request.url.endswith('/compare') else None)
            expect(shop.get_by_role('heading',name='Published inventory',exact=True)).to_be_visible()
            shop.screenshot(path='/tmp/frontdesk-shopping-inventory.png',full_page=True)
            shop.get_by_label('Compare this vehicle').first.check();shop.get_by_label('Compare this vehicle').nth(1).check()
            shop.get_by_role('button',name='Compare selected (2)',exact=True).click()
            expect(shop.get_by_text('Listed price difference: $3,000.00.',exact=False)).to_be_visible()
            expect(shop.get_by_role('table')).to_contain_text('Not provided')
            shop.get_by_role('button',name='AI chat',exact=True).click()
            assert grok.call_count==calls, 'Opening the customer features unexpectedly requested inference'
            shop.get_by_label('Your message').fill('My vehicle budget is $25,000 and I need 5 seats for commuting.')
            shop.get_by_role('button',name='Send to AI',exact=True).click()
            expect(shop.get_by_role('log')).to_contain_text('My vehicle budget is $25,000')
            expect(shop.get_by_role('status')).to_contain_text('Thinking')
            first_reply.set()
            expect(shop.get_by_role('log')).to_contain_text('lower-priced option')
            expect(shop.get_by_label('Maximum budget (USD)')).to_have_value('25000')
            expect(shop.get_by_label('Minimum seats')).to_have_value('5')
            shop.get_by_label('Your message').fill('I can raise my vehicle budget to $30,000.')
            shop.get_by_role('button',name='Send to AI',exact=True).click()
            expect(shop.get_by_label('Maximum budget (USD)')).to_have_value('30000')
            shop.screenshot(path='/tmp/frontdesk-shopping-fit.png',full_page=True)
            shop.get_by_role('button',name='Compare',exact=False).filter(has=shop.locator('.count')).click()
            shop.get_by_role('button',name='Refresh comparison',exact=True).click()
            expect(shop.get_by_text('Listed price difference: $3,000.00.',exact=False)).to_be_visible()
            shop.evaluate('window.scrollTo(0,0)')
            shop.screenshot(path='/tmp/frontdesk-shopping-comparison.png',full_page=True)
            compare_count=len(comparison_requests)
            shop.get_by_role('button',name='Explain this comparison with AI',exact=True).click()
            expect(shop.locator('.bubble.assistant > strong')).to_have_count(3)
            assert len(comparison_requests)==compare_count, 'Chat waited for an unnecessary comparison request'
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
            page.get_by_role('button',name='Request log',exact=True).click()
            expect(page.get_by_role('heading',name='Recent Grok requests')).to_be_visible()
            expect(page.get_by_text('mock-completion-123',exact=True).first).to_be_visible()
            shop.get_by_label('Your message').fill('Check citation recovery for these selected vehicles.')
            shop.get_by_role('button',name='Send to AI',exact=True).click()
            expect(shop.get_by_role('log')).to_contain_text('Some details could not be verified')
            expect(shop.get_by_role('log')).not_to_contain_text('UNVERIFIED-PROSE')
            expect(shop.get_by_role('log')).not_to_contain_text('$99,999')
            page.get_by_role('button',name='Refresh requests',exact=True).click()
            expect(page.get_by_text('accepted_with_limits',exact=True).first).to_be_visible()
            expect(page.get_by_text('AI wording omitted at sources: unapproved_source · field answer',exact=True)).to_be_visible()
            page.screenshot(path='/tmp/frontdesk-showcase-evidence.png',full_page=True)
            shop.set_viewport_size({'width':390,'height':844});shop.screenshot(path='/tmp/frontdesk-shopping-mobile.png',full_page=True)
            assert shop.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile page overflow'
            shop.get_by_role('button',name='Inventory',exact=True).click()
            assert shop.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile inventory overflow'
            assert not errors,errors
            print('PASS: rendered owner suggestions/publication, FAQs, inventory/comparison, pending and delivered chat turns, continued preferences, retained valid prose, staff inquiry, request log and mobile layout. Auth and provider completions were simulated.')
            browser.close()
    finally:
        first_reply.set()
        server.should_exit=True;thread.join(timeout=5);fixture.tearDown()


if __name__=='__main__':main()
