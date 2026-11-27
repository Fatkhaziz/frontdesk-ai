"""Render source values and recover safely from unverified numeric wording.

There is exactly one provider request. Model preferences, source membership and
recommendations must pass the existing checks. Unusable numeric or citation
wording discards ALL model prose; rejected claims never become evidence.
"""
import re

from .ai_rejection import Rejection
from .shopping import Preferences, eligible, validate_answer


def compact_sources(sources):
    aliases = {s['id']: f'S{i + 1}' for i, s in enumerate(sources)}
    return [{**{key: s[key] for key in ('label', 'text', 'listing_id', 'value_text')}, 'id': aliases[s['id']],
             **({'inputs': [aliases[i] for i in s['inputs']]} if s.get('inputs') else {})}
            for s in sources]


def normalize_sources(result, sources):
    if not isinstance(result, dict) or set(result) != {'preferences', 'answer', 'follow_up', 'recommended_ids', 'source_ids'}:
        raise Rejection('shape', 'shape')
    aliases = {f'S{i + 1}': s for i, s in enumerate(sources)}
    allowed = {s['id']: s for s in sources}
    refs = result['source_ids']
    if not isinstance(refs, list) or len(refs) > 30 or any(not isinstance(r, str) for r in refs):
        raise Rejection('sources', 'sources', 'source_ids')
    refs = [aliases[r]['id'] if r in aliases else r for r in refs]
    if any(r not in allowed for r in refs):
        raise Rejection('sources', 'unapproved_source', 'source_ids')
    return {**result, 'source_ids': list(dict.fromkeys(refs))}


def render_source_values(result, sources):
    result = normalize_sources(result, sources)
    aliases = {f'S{i + 1}': s for i, s in enumerate(sources)}
    allowed = {s['id']: s for s in sources}
    refs = list(result['source_ids'])
    rendered = {**result}
    for field in ('answer', 'follow_up'):
        if not isinstance(result[field], str):
            raise Rejection('shape', 'answer', field)
        def citation(match):
            inner = re.sub(r'^(?:sources?|refs?|citations?)\s*:\s*', '', match.group(1).strip(), flags=re.I)
            double = match.group(0).startswith('[[')
            if not double and not re.match(r'(?:S[0-9]|listing:|comparison:|knowledge:|profile:)', inner, re.I):
                return match.group(0)
            resolved = []
            for reference in re.split(r'\s*[,;]\s*|\s+', inner):
                if re.fullmatch(r'[sS][0-9]{1,4}', reference):
                    reference = 'S' + str(int(reference[1:]))
                source = aliases.get(reference) or allowed.get(reference)
                if not source:
                    raise Rejection('sources', 'unapproved_source', field)
                resolved.append(source)
                if source['id'] not in refs:
                    refs.append(source['id'])
            # Single brackets and groups are citations. A single double-
            # bracket field reference is an approved value insertion. Knowledge
            # and policy sources have no scalar value and remain citations.
            if double and len(resolved) == 1 and resolved[0].get('value_text'):
                return resolved[0]['value_text']
            return ''
        rendered[field] = re.sub(r'\[\[?([^\[\]\n]{1,800})\]\]?', citation, result[field])
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
    rendered = None
    try:
        rendered = render_source_values(result, sources)
        return {**validate_answer(rendered, data, body, sources), 'answer_mode': 'ai_explanation'}
    except Rejection as exc:
        numeric = (exc.stage, exc.reason) == ('claims', 'unsupported_number')
        inline_source = (exc.stage, exc.reason) == ('sources', 'unapproved_source') and exc.field in ('answer', 'follow_up')
        if not (numeric or inline_source):
            raise
        # Discard ALL model prose, including unusable inline references. Validate
        # the structured result independently before building anything useful:
        # foreign declared sources, bad needs and invalid recommendations still
        # fail. This never turns an unknown citation into approved evidence.
        structured = normalize_sources(rendered if rendered is not None else result, sources)
        structured = validate_answer({**structured, 'answer': 'Checking published options.', 'follow_up': ''}, data, body, sources)
        summary = confirmed_summary(structured, data, body, sources)
        return {**summary, 'answer_mode': 'grounded_summary',
                'validation_rejection': exc.diagnostic(sources)}
