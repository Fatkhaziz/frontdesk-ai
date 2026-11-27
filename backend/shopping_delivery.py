"""Check each live Grok paragraph against its own published sources."""
import re

from .ai_rejection import Rejection
from .shopping import validate_answer


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


def prose_rejection(exc):
    return (exc.stage == 'claims' or
            (exc.stage == 'sources' and exc.reason in ('unapproved_source', 'sources')) or
            (exc.stage == 'shape' and exc.reason == 'answer'))


def validate_delivery(result, data, body, sources):
    result = normalize_sources(result, sources)
    if isinstance(result['answer'], str):
        # Accept a checked plain-text reply if the model uses the older format.
        legacy = validate_answer(render_source_values(result, sources), data, body, sources)
        return {**legacy, 'answer_mode': 'ai_explanation'}

    paragraphs = result['answer']
    if not isinstance(paragraphs, list) or not 1 <= len(paragraphs) <= 4:
        raise Rejection('shape', 'answer', 'answer')
    if not isinstance(result['follow_up'], str):
        raise Rejection('shape', 'answer', 'follow_up')

    context = {'preferences': result['preferences'], 'answer': 'Published inventory.',
               'follow_up': '', 'recommended_ids': [], 'source_ids': []}
    # Preference errors belong to the whole response, even if some text is valid.
    checked = validate_answer(context, data, body, sources)
    paragraphs_kept, refs, rejected = [], [], None
    for paragraph in paragraphs:
        if not isinstance(paragraph, dict) or set(paragraph) != {'text', 'source_ids'}:
            raise Rejection('shape', 'answer', 'answer')
        candidate = {**checked, 'answer': paragraph['text'], 'source_ids': paragraph['source_ids']}
        try:
            rendered = render_source_values(candidate, sources)
            valid = validate_answer(rendered, data, body, sources)
        except Rejection as exc:
            if not prose_rejection(exc):
                raise
            if rejected is None:
                rejected = exc
            continue
        paragraphs_kept.append(valid['answer'].strip())
        refs.extend(valid['source_ids'])
    if not paragraphs_kept:
        raise rejected or Rejection('shape', 'answer', 'answer')

    follow_up = ''
    if result['follow_up']:
        candidate = {**checked, 'follow_up': result['follow_up'], 'source_ids': result['source_ids']}
        try:
            valid = validate_answer(render_source_values(candidate, sources), data, body, sources)
            follow_up = valid['follow_up']
            refs.extend(valid['source_ids'])
        except Rejection as exc:
            if not prose_rejection(exc):
                raise
            if rejected is None:
                rejected = exc

    by_id = {source['id']: source for source in sources}
    # A comparison citation includes exact field references for its two inputs.
    refs.extend(input_id for ref in dict.fromkeys(refs) for input_id in by_id[ref].get('inputs', []))
    final = {**checked, 'answer': '\n\n'.join(paragraphs_kept), 'follow_up': follow_up,
             'recommended_ids': result['recommended_ids'], 'source_ids': list(dict.fromkeys(refs))}
    try:
        validated = validate_answer(final, data, body, sources)
    except Rejection as exc:
        if not rejected or exc.reason != 'uncited_recommendation':
            raise
        # A dropped paragraph may have been the evidence for a suggestion.
        # Drop that suggestion too. Scope and hard requirements already passed.
        cited_cars = {by_id[ref].get('listing_id') for ref in refs}
        final['recommended_ids'] = [identity for identity in final['recommended_ids'] if identity in cited_cars]
        validated = validate_answer(final, data, body, sources)
    if rejected:
        return {**validated, 'answer_mode': 'partial_ai_explanation', 'validation_rejection': rejected.diagnostic(sources)}
    return {**validated, 'answer_mode': 'ai_explanation'}
