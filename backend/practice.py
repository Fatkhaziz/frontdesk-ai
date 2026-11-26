"""Local owner launch configuration. Never resets counters or buys credits."""
import argparse
import os
from .db import connect, execute
from .spending import initialize, status, PRICED_MODEL


def main():
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group()
    group.add_argument('--practice',action='store_true')
    group.add_argument('--presentation',action='store_true')
    args=p.parse_args()
    if not os.getenv('XAI_API_KEY') or os.getenv('XAI_MODEL')!=PRICED_MODEL:
        raise RuntimeError('Existing xAI key and the priced model are required; no paid request sent.')
    with connect() as c:
        initialize(c)
        execute(c,'UPDATE ai_spend_budget SET mode=%s WHERE id=1',('presentation' if args.presentation else 'preparation',))
        s=status(c)
        calls=execute(c,'SELECT calls FROM ai_budget WHERE id=1').fetchone()['calls']
    print('AI mode:',s['mode'],'| Historical attempts preserved:',calls)
    print('Preparation remaining (conservative): $'+format(s['preparation_remaining_usd'],'.2f'))
    print('Presentation reserve during preparation: $'+format(s['presentation_reserve_usd'],'.2f'))
    print('Owner-declared starting credit: $4.97. This is not a current provider balance. Verify actual credit at console.x.ai.')
    print('No inference request, purchase, credit reset or automatic retry performed.')


if __name__=='__main__':
    main()
