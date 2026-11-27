"""Render source values and recover safely from unverified numeric wording.

There is exactly one provider request. Model preferences, source membership and
recommendations must pass the existing checks. A numeric prose failure discards
ALL model prose; it never grants permission to display the rejected claim.
"""
import re

from .ai_rejection import Rejection
from .shopping import Preferences, claim_text, eligible, validate_answer


def compact_sources(sources):
    aliases = {s['id']: f'S{i + 1}' for i, s in enumerate(sources)}
    return [{**{key: s[key] for key in ('label', 'text', 'listing_id', 'value_text')}, 'id': aliases[s['id']],
             **({'inputs': [aliases[i] for i in s['inputs']]} if s.get('inputs') else {})}
            for s in sources]


def render_source_values(result, sources):
    if not isinstance(result, dict) or set(result) != {'preferences', 'answer', 'follow_up', 'recommended_ids', 'source_ids'}:
        raise Rejection('shape', 'shape')
    aliases = {f'S{i + 1}': s for i, s in enumerate(sources)}
    allowed = {s['id']: s for s in sources}
    refs = result['source_ids']
    if not isinstance(refs, list) or len(refs) > 30 or any(not isinstance(r, str) for r in refs):
        raise Rejection('sources', 'sources', 'source_ids')
    refs = [aliases[r]['id'] if r in aliases else r for r in refs]
    # Duplicate declarations are malformed, rather than quietly repaired.
    if len(refs) != len(set(refs)) or any(r not in allowed for r in refs):
        raise Rejection('sources', 'unapproved_source', 'source_ids')
    rendered = {**result}
    for field in ('answer', 'follow_up'):
        if not isinstance(result[field], str):
            raise Rejection('shape', 'answer', field)
        def insert(match):
            source = aliases.get(match.group(1)) or allowed.get(match.group(1))
            if not source or not source.get('value_text'):
                raise Rejection('sources', 'unapproved_source', field)
            if source['id'] not in refs:
                refs.append(source['id'])
            return source['value_text']
        text = re.sub(r'\[\[([^\]\n]{1,240})\]\]', insert, result[field])
        # Citation footnotes are references, not quantities or insertions.
        def footnote(match):
            source = aliases.get(match.group(1))
            if not source or source['id'] not in refs:
                raise Rejection('sources', 'unapproved_source', field)
            return '[' + source['id'] + ']'
        rendered[field] = re.sub(r'\[(S[0-9]+)\]', footnote, text)
    return {**rendered, 'source_ids': refs}


def confirmed_summary(result, data, body, sources):
    """A separately labeled server summary, never an edited model answer."""
    prefs = Preferences.model_validate(result['preferences'])
    allowed = {s['id']: s for s in sources}
    inventory = {l['id']: l for l in data['listings']}
    ids = body.selected_ids or result['recommended_ids'] or [l['id'] for l in data['listings'] if eligible(l, prefs)][:3]
    refs, lines = [], []
    for identity in ids:
        car = inventory[identity]
        facts = car['facts']
        values = []
        for field in ('price', 'mileage', 'seats', 'mpg_combined', 'cargo_cubic_feet'):
            source_id = f"listing:{identity}:r{car['revision']}:{field}"
            source = allowed.get(source_id)
            if source and source.get('value_text'):
                values.append(source['value_text'])
                refs.append(source_id)
        title = f"{facts['year']} {facts['make']} {facts['model']}"
        fit = 'Meets your recorded hard requirements.' if eligible(car, prefs) else 'Some requirements are unmet or unconfirmed.'
        lines.append(f"{title}: {'; '.join(values)}. {fit}")
    answer = '\n\n'.join(lines) if lines else 'No published vehicle can be confirmed to meet all your recorded requirements. Staff can help clarify missing information.'
    answer += '\n\nTaxes, fees, condition, reliability and market fairness are not established by these specifications.'
    follow_up = ('Does your budget cover the vehicle price or the total including taxes and fees?'
                 if prefs.budget_kind == 'unknown' else
                 'Are there additional features you require?' if not prefs.required_features else
                 'Would you like staff to confirm the missing details and total costs?')
    # Re-run the full validator. Invalid preferences, foreign sources, wrong
    # recommendations, or an oversized summary still cannot pass this path.
    return validate_answer({**result, 'answer': answer, 'follow_up': follow_up, 'source_ids': refs}, data, body, sources)


def validate_delivery(result, data, body, sources):
    rendered = render_source_values(result, sources)
    try:
        return {**validate_answer(rendered, data, body, sources), 'answer_mode': 'ai_explanation'}
    except Rejection as exc:
        if (exc.stage, exc.reason) != ('claims', 'unsupported_number'):
            raise
        # Unknown inline references must not be hidden by a preceding numeric
        # failure. Every declared source and structured requirement was already
        # checked before the claim stage.
        allowed = {s['id']: s for s in sources}
        for field in ('answer', 'follow_up'):
            claim_text(rendered[field], rendered['source_ids'], allowed, field)
        summary = confirmed_summary(rendered, data, body, sources)
        return {**summary, 'answer_mode': 'grounded_summary',
                'validation_rejection': exc.diagnostic(sources)}
