"""Loopback rehearsal with temporary data and simulated sign-in. No .env loading."""
import base64
import json
import logging
import os
import tempfile
from pathlib import Path

import uvicorn
from fastapi import HTTPException, Request
from fastapi.testclient import TestClient


ACCOUNTS = {
    'owner-motors@example.invalid': ('motors-owner', 'rehearsal-motors', 'owner'),
    'owner-salon@example.invalid': ('salon-owner', 'rehearsal-salon', 'owner'),
    'owner-studio@example.invalid': ('studio-owner', 'rehearsal-studio', 'owner'),
    'staff-salon@example.invalid': ('salon-staff', 'rehearsal-salon', 'staff'),
}


def main():
    os.chdir(Path(__file__).resolve().parent.parent)
    # This process always replaces supplied credentials and creates a fresh local database.
    with tempfile.TemporaryDirectory(prefix='frontdesk-rehearsal-') as temporary:
        port = 8002
        os.environ.update({
            'TESTING': '1', 'FRONTDESK_REHEARSAL': '1',
            'DATABASE_URL': 'sqlite:///' + temporary + '/rehearsal.sqlite',
            'QUESTION_MODE': 'demo', 'DRAFT_AI_ENABLED': '0',
            'XAI_API_KEY': '', 'XAI_MODEL': '',
            'SUPABASE_URL': f'http://127.0.0.1:{port}/rehearsal-auth',
            'SUPABASE_PUBLISHABLE_KEY': 'sb_publishable_rehearsal',
        })
        from backend.main import app, identity
        from backend.db import connect, execute

        with connect() as connection:
            connection.executescript(Path('migrations/001_demo.sql').read_text().split('-- Application data')[0] + 'COMMIT;')
            for migration in [p.name for p in sorted(Path('migrations').glob('*.sql')) if p.name != '001_demo.sql']:
                connection.executescript(Path('migrations', migration).read_text().split('REVOKE')[0] + 'COMMIT;')
            for business_id, name in [('rehearsal-motors', 'Demo Motors'), ('rehearsal-salon', 'Demo Salon'), ('rehearsal-studio', 'Demo Studio')]:
                execute(connection, 'INSERT INTO businesses VALUES(%s,%s)', (business_id, name))

        def rehearsal_identity(request: Request):
            header = request.headers.get('Authorization', '')
            subject = header.removeprefix('Bearer ')
            for account in ACCOUNTS.values():
                expected = make_token(account[0])
                if header.startswith('Bearer ') and subject == expected:
                    return {'subject': account[0], 'business_id': account[1], 'role': account[2]}
            raise HTTPException(401, 'Use a listed rehearsal account.')

        app.dependency_overrides[identity] = rehearsal_identity

        @app.post('/rehearsal-auth/auth/v1/token')
        async def rehearsal_login(request: Request):
            body = await request.json()
            account = ACCOUNTS.get(body.get('email'))
            if account is None or body.get('password') != 'rehearsal':
                raise HTTPException(400, 'Use a listed rehearsal account and the rehearsal password.')
            return {'access_token': make_token(account[0]), 'token_type': 'bearer', 'expires_in': 86400,
                    'refresh_token': 'rehearsal-only', 'user': {'id': account[0], 'aud': 'authenticated', 'email': body['email']}}

        client = TestClient(app)
        for email, domain in [('owner-motors@example.invalid', 'dealership'), ('owner-salon@example.invalid', 'salon'), ('owner-studio@example.invalid', 'photography_studio')]:
            account = ACCOUNTS[email]
            headers = {'Authorization': 'Bearer ' + make_token(account[0])}
            settings = sample_profile(domain)
            assert client.put('/api/business/profile', headers=headers, json={'expected_revision': 0, 'profile': settings}).status_code == 200
            assert client.post('/api/business/profile/publish', headers=headers, json={'expected_revision': 1, 'confirm_approval': True}).status_code == 200
            if domain == 'dealership':
                facts = {'make': 'Toyota', 'model': 'Camry', 'year': 2022, 'price': 2350000, 'mileage': 42000, 'availability': 'available'}
                result = client.post('/api/listings', headers=headers, json={'facts': facts, 'description': '2022 Toyota Camry with 42,000 miles. Available for $23,500 USD.'})
                assert result.status_code == 201
                assert client.post('/api/listings/' + result.json()['id'] + '/publish', headers=headers, json={'expected_revision': 1, 'confirm_approval': True}).status_code == 200

        from scripts.sample_inventory import example_vehicles
        for facts in example_vehicles():
            headers={'Authorization':'Bearer '+make_token('motors-owner')}
            result=client.post('/api/listings',headers=headers,json={'facts':facts,'description':'Fictional showcase vehicle, not a real sale offer.'})
            assert result.status_code==201
            assert client.post('/api/listings/'+result.json()['id']+'/publish',headers=headers,json={'expected_revision':1,'confirm_approval':True}).status_code==200

        logging.getLogger('frontdesk').setLevel(logging.ERROR)
        print('\nREHEARSAL ONLY — synthetic local data and simulated sign-in', flush=True)
        print(f'Open http://127.0.0.1:{port}/', flush=True)
        print('Accounts: ' + ', '.join(ACCOUNTS), flush=True)
        print('Password for all rehearsal accounts: rehearsal', flush=True)
        print('Temporary data resets when this process stops. No paid AI calls are enabled.\n', flush=True)
        uvicorn.run(app, host='127.0.0.1', port=port, access_log=False)
        app.dependency_overrides.clear()


def make_token(subject):
    payload = base64.urlsafe_b64encode(json.dumps({'sub': subject, 'exp': 4102444800}).encode()).decode().rstrip('=')
    return 'rehearsal.' + payload + '.simulated'


def sample_profile(domain):
    salon = domain == 'salon'
    studio = domain == 'photography_studio'
    return {
        'name': 'Demo Studio' if studio else 'Demo Salon' if salon else 'Demo Motors', 'domain': domain,
        'about': 'Synthetic rehearsal business. Inquiries go to this business’s staff inbox.',
        'contact': 'studio@example.invalid' if studio else 'salon@example.invalid' if salon else 'motors@example.invalid',
        'time_zone': 'America/New_York',
        'hours': [{'day': day, 'opens': '10:00' if salon else '09:00', 'closes': '18:00' if salon else '17:00'} for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']],
        'services': [{
            'id': 'portrait-session' if studio else 'haircut' if salon else 'vehicle-service', 'name': 'Portrait session' if studio else 'Haircut consultation' if salon else 'Vehicle service inquiry',
            'description': 'Staff review your request and arrange the time.', 'duration_minutes': 60 if studio else 45 if salon else 30, 'price_cents': 4500 if salon else None,
            'questions': [{'id': 'participants' if studio else 'stylist' if salon else 'vehicle', 'label': 'How many participants and which location?' if studio else 'Which stylist would you prefer?' if salon else 'What is the year, make and model of your vehicle?', 'required': True}],
        }],
        'faqs': [{'question': 'What is your cancellation policy?', 'answer': 'For this studio example, contact staff about package changes.' if studio else 'For this salon example, request changes at least 24 hours ahead.' if salon else 'For this dealership example, contact service staff to change your visit.'}],
    }


if __name__ == '__main__':
    main()
