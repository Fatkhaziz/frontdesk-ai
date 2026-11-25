"""Add clearly labeled fictional vehicles. No updates/deletes of existing records.

Run only with --confirm-synthetic. Requires an existing active owner. This is not
an interview or approval of actual business policies; knowledge starts private.
"""
import argparse
import json
import uuid

from backend.ai import now
from backend.db import connect, execute
from backend.main import Facts
from scripts.sample_inventory import example_vehicles


def seed(business_id=None):
    with connect() as c:
        sql = "SELECT subject,business_id FROM memberships WHERE active=TRUE AND role='owner'"
        args=()
        if business_id:
            sql+=' AND business_id=%s';args=(business_id,)
        owners=execute(c,sql,args).fetchall()
        businesses={r['business_id'] for r in owners}
        if len(businesses)!=1:
            raise RuntimeError('Choose one existing owner business with --business-id. No records were added.')
        business=next(iter(businesses));actor=owners[0]['subject'];added=0
        for index, facts in enumerate(example_vehicles()):
            facts=Facts.model_validate(facts).model_dump()
            lid=str(uuid.uuid5(uuid.NAMESPACE_URL,'frontdesk-showcase-v1:'+business+':'+str(index)))
            description='Fictional showcase vehicle. Specifications and price are illustrative, not a real sale offer.'
            snapshot=json.dumps({'facts':facts,'description':description})
            row=execute(c,'INSERT INTO listings(id,business_id,revision,facts,description,approved_revision,approved_by,published,published_revision) VALUES(%s,%s,1,%s,%s,1,%s,%s,1) ON CONFLICT(id) DO NOTHING RETURNING id',
                        (lid,business,json.dumps(facts),description,actor,snapshot)).fetchone()
            if row:
                added+=1
                execute(c,'INSERT INTO audit_events VALUES(%s,%s,%s,%s,%s,%s,%s)',(str(uuid.uuid4()),business,actor,lid,1,'synthetic_seed',now()))
    print(f'Added {added} explicitly fictional vehicles; existing records and AI budget unchanged.')
    print('Customer page: http://127.0.0.1:8000/shop/'+business)
    return business


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--business-id');p.add_argument('--confirm-synthetic',action='store_true',required=True)
    args=p.parse_args()
    try:seed(args.business_id)
    except Exception as e:
        print('Example setup stopped ('+type(e).__name__+'). Choose a single existing owner business and check migration state privately.')
        raise SystemExit(1) from None
