"""Atomic conservative spending reservations across every paid AI route.

USD figures are account-owner declarations, never a live xAI balance. A reserve
is not refunded on failed calls or missing usage. This intentionally overstates
estimated spending. No route purchases credits or resets historical attempts.
"""
import json
import math
import os
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from fastapi import HTTPException
from .db import execute

PRICED_MODEL = 'grok-4.20-0309-non-reasoning'
INPUT_MICRO_PER_TOKEN = Decimal('1.25')
OUTPUT_MICRO_PER_TOKEN = Decimal('2.50')


def micros(value):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0:
            raise ValueError('Invalid budget amount')
        return int(amount * 1000000)
    except (InvalidOperation, TypeError):
        raise ValueError('Invalid budget amount') from None


def initialize(c):
    if os.getenv('AI_PREPARATION_BUDGET_USD') is None:
        return
    total = micros(os.getenv('AI_AUTHORIZED_REMAINING_USD', '4.97'))
    preparation = micros(os.getenv('AI_PREPARATION_BUDGET_USD', '1.00'))
    reserve = micros(os.getenv('AI_PRESENTATION_RESERVE_USD', '3.50'))
    if total > micros('4.97') or preparation > micros('1.00') or reserve < micros('3.50') or preparation + reserve > total:
        raise ValueError('Budget must preserve the authorized presentation reserve')
    execute(c, 'INSERT INTO ai_spend_budget(id,total_micro_usd,preparation_micro_usd,presentation_reserve_micro_usd,created_at) VALUES(1,%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING',
            (total, preparation, reserve, datetime.now(timezone.utc).isoformat()))


def ceiling_micro(instruction, payload, output_tokens=1800):
    # One input token per UTF-8 byte is a conservative bound; include framing.
    size = len(json.dumps(payload).encode()) + len(instruction.encode()) + 4096
    return math.ceil(Decimal(size) * INPUT_MICRO_PER_TOKEN + Decimal(output_tokens) * OUTPUT_MICRO_PER_TOKEN)


def reserve_attempt(c, task, business, operation, instruction, payload, output_tokens=1800):
    initialize(c)
    budget = execute(c, 'SELECT * FROM ai_spend_budget WHERE id=1').fetchone()
    if budget:
        if os.getenv('XAI_MODEL') != PRICED_MODEL:
            raise HTTPException(503, 'The budget estimate is not verified for this model. No AI request was sent.')
        cost = ceiling_micro(instruction, payload, output_tokens)
        if len(json.dumps(payload).encode()) > 48000:
            raise HTTPException(422, 'Too much AI context. Shorten the message or reduce the selection.')
        row = execute(c, '''UPDATE ai_spend_budget SET reserved_micro_usd=reserved_micro_usd+%s,
            preparation_reserved_micro_usd=preparation_reserved_micro_usd+CASE WHEN mode='preparation' THEN %s ELSE 0 END
            WHERE id=1 AND reserved_micro_usd+%s<=total_micro_usd AND
            (mode='presentation' OR (preparation_reserved_micro_usd+%s<=preparation_micro_usd AND
             total_micro_usd-reserved_micro_usd-%s>=presentation_reserve_micro_usd)) RETURNING mode''',
            (cost,cost,cost,cost,cost)).fetchone()
        if not row:
            raise HTTPException(429, 'The practice budget is reserved. No AI request was sent. The owner can review the presentation allowance in System status.')
        execute(c, 'INSERT INTO ai_spend_reservations VALUES(%s,%s,%s,%s,%s,%s)',
                (task,business,operation,row['mode'],cost,datetime.now(timezone.utc).isoformat()))
    calls = execute(c, 'UPDATE ai_budget SET calls=calls+1 WHERE id=1 AND calls<%s RETURNING calls',
                    (int(os.getenv('AI_CALL_LIMIT','10')),)).fetchone()
    if not calls:
        # Caller transaction rolls back both reservations on a capped attempt.
        raise HTTPException(429, 'The configured AI attempt limit has been reached. No request was sent.')


def status(c):
    initialize(c)
    row = execute(c,'SELECT * FROM ai_spend_budget WHERE id=1').fetchone()
    if not row:
        return {'configured':False}
    b=dict(row)
    return {'configured':True,'mode':b['mode'],
            'authorized_remaining_usd':b['total_micro_usd']/1000000,
            'preparation_limit_usd':b['preparation_micro_usd']/1000000,
            'presentation_reserve_usd':b['presentation_reserve_micro_usd']/1000000,
            'conservative_reserved_usd':b['reserved_micro_usd']/1000000,
            'preparation_remaining_usd':max(0,b['preparation_micro_usd']-b['preparation_reserved_micro_usd'])/1000000,
            'conservative_remaining_usd':max(0,b['total_micro_usd']-b['reserved_micro_usd'])/1000000,
            'balance_source':'Owner-declared starting allowance; verify actual remaining credit at xAI. Reservations are conservative ceilings, not charges.'}
