"""Read live setup and GET routes only; no migration, AI request or data write.

Called by run-real-setup.sh after the real server starts. The private report
contains IDs and setup metadata only: no emails, contacts, tokens or profiles.
"""
import argparse
import json
import logging
import os
import tempfile
import time
from collections import Counter
from pathlib import Path

import httpx
from backend.db import connect, execute

BASE = 'http://127.0.0.1:8000'
DOMAINS = ('dealership', 'salon', 'photography_studio')


def inspect():
    if os.getenv('TESTING') or os.getenv('FRONTDESK_REHEARSAL') or os.getenv('DATABASE_URL', '').startswith('sqlite:'):
        raise RuntimeError('Real PostgreSQL configuration is required')
    if os.getenv('XAI_API_KEY') or os.getenv('DRAFT_AI_ENABLED') != '0' or int(os.getenv('AI_CALL_LIMIT', '10')) != 10:
        raise RuntimeError('Paid AI must be paused and the cap must remain 10')
    with connect() as c:
        execute(c, 'SET TRANSACTION READ ONLY')
        calls = execute(c, 'SELECT calls FROM public.ai_budget WHERE id=1').fetchone()['calls']
        if calls != 9:
            raise RuntimeError('Budget differs from the confirmed 9 of 10; review privately')
        businesses = execute(c, 'SELECT id FROM public.businesses ORDER BY id').fetchall()
        profiles = execute(c, 'SELECT business_id,revision,profile,published_revision,published FROM public.business_profiles ORDER BY business_id').fetchall()
        memberships = [dict(r) for r in execute(c, 'SELECT business_id,role,active FROM public.memberships').fetchall()]
        # No password, hash, email, access token or refresh token is selected.
        execute(c, 'SAVEPOINT auth_metadata')
        confirmed = None
        try:
            confirmed = [dict(r) for r in execute(c, 'SELECT m.business_id,m.role,m.active,(u.id IS NOT NULL) AS auth_user_exists,(u.email_confirmed_at IS NOT NULL) AS email_confirmed FROM public.memberships m LEFT JOIN auth.users u ON u.id::text=m.subject').fetchall()]
        except Exception:
            execute(c, 'ROLLBACK TO SAVEPOINT auth_metadata')
        execute(c, 'RELEASE SAVEPOINT auth_metadata')
        listings = execute(c, 'SELECT id,published,published_revision FROM public.listings WHERE published IS NOT NULL ORDER BY id').fetchall()
    report = {'source':'real PostgreSQL and actual HTTP routes; no mocked identity', 'ai_calls_used':calls,'ai_call_limit':10,'businesses':[], 'membership_auth_metadata_readable':confirmed is not None}
    profile_map = {r['business_id']: r for r in profiles}
    public_checks = []
    for business in businesses:
        bid = business['id']; row = profile_map.get(bid)
        item = {'business_id':bid,'profile_exists':row is not None,
                'active_owners':sum(m['business_id']==bid and m['active'] and m['role']=='owner' for m in memberships),
                'active_staff':sum(m['business_id']==bid and m['active'] and m['role']=='staff' for m in memberships)}
        if confirmed is not None:
            item['confirmed_active_owners'] = sum(m['business_id']==bid and m['active'] and m['role']=='owner' and m['auth_user_exists'] and m['email_confirmed'] for m in confirmed)
        if row:
            profile = json.loads(row['profile'])
            item.update(domain=profile.get('domain'),private_revision=row['revision'],published_revision=row['published_revision'],needs_private_review=row['revision']!=row['published_revision'])
            if row['published']:
                public = json.loads(row['published'])
                item['published_domain'] = public.get('domain')
                public_checks.append(('/api/public/businesses/'+bid,{**public,'revision':row['published_revision']}))
        report['businesses'].append(item)
    for row in listings:
        public_checks.append(('/api/public/'+row['id'],{**json.loads(row['published']),'revision':row['published_revision']}))
    with httpx.Client(timeout=15) as client:
        response = client.get(BASE+'/health'); response.raise_for_status()
        response = client.get(BASE+'/'); response.raise_for_status()
        config = client.get(BASE+'/api/config'); config.raise_for_status(); config = config.json()
        if config.get('rehearsal') or config.get('aiEnabled'):
            raise RuntimeError('Unexpected rehearsal or paid drafting configuration')
        report['question_mode'] = config.get('questionMode')
        for route, expected in public_checks:
            response = client.get(BASE+route); response.raise_for_status()
            if response.json() != expected:
                raise RuntimeError('Published snapshot changed during route inspection; reload and review')
        report['database_backed_public_GETs_checked'] = len(public_checks)
        for route in ['/api/workspace','/api/listings','/api/inquiries','/api/diagnostics','/api/ai/evidence']:
            response = client.get(BASE+route)
            if response.status_code != 401:
                raise RuntimeError('Anonymous private-route check failed')
        report['anonymous_private_routes_rejected'] = 5
    with connect() as c:
        execute(c, 'SET TRANSACTION READ ONLY')
        after = execute(c, 'SELECT calls FROM public.ai_budget WHERE id=1').fetchone()['calls']
    if after != calls:
        raise RuntimeError('AI budget changed concurrently; review privately')
    report['remaining_attempts'] = 10-after
    coverage = Counter(b.get('published_domain') for b in report['businesses'] if b.get('published_revision'))
    report['published_domain_coverage'] = {d:coverage[d] for d in DOMAINS}
    report['missing_published_domains'] = [d for d in DOMAINS if not coverage[d]]
    descriptor, filename = tempfile.mkstemp(prefix='frontdesk-live-setup-private-', suffix='.json')
    with os.fdopen(descriptor,'w') as output:
        json.dump(report,output,indent=2)
    print('Real setup inspection passed. Public DB-backed pages checked:',len(public_checks))
    print('Active owner memberships:',sum(b['active_owners'] for b in report['businesses']))
    print('Published business types:',', '.join(d for d in DOMAINS if coverage[d]) or 'none')
    print('Business types still needing approved publication:',', '.join(report['missing_published_domains']) or 'none')
    print('Private report (mode 0600):', filename)
    print('Existing records unchanged. Attempts remain 9/10. Real user sign-in and Grok NOT verified.')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-pid',type=int,required=True)
    args=parser.parse_args()
    logging.getLogger('httpx').setLevel(logging.WARNING)
    if args.server_pid <= 0:
        raise RuntimeError('Invalid server PID')
    for _ in range(60):
        try:
            os.kill(args.server_pid,0)
        except ProcessLookupError:
            raise RuntimeError('Real server exited before startup') from None
        try:
            with httpx.Client(timeout=1) as client:
                if client.get(BASE+'/health').status_code==200:
                    inspect(); return
        except (httpx.ConnectError,httpx.TimeoutException):
            pass
        time.sleep(0.5)
    raise RuntimeError('Real server was not ready; no migration or inference attempted')


if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print('Real setup stopped safely ('+type(exc).__name__+'); inspect configuration privately. No migration, AI request or application write attempted.')
        raise SystemExit(1) from None
