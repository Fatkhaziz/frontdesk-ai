"""Read the saved synthetic shopping check for the local owner dashboard."""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from .ai_rejection import stored_rejection
from .db import connect, execute

MAX_CAPTURE_BYTES = 512 * 1024
RUN_DIRECTORY = re.compile(r"\d{8}T\d{6}Z")
QUESTIONS = (
    'My vehicle-price budget is $25,000. I need five seats for commuting and prefer fuel economy. Compare my selected vehicles, explain missing information and ask one useful follow-up.',
    'Raise my vehicle-price budget to $30,000 and retain five seats. Which selected option fits my priorities better now?',
    'Is this a fair price? Explain what you can verify and what information you would still need.',
)


def local_showcase_enabled():
    return os.getenv('FRONTDESK_LOCAL_SHOWCASE') == '1'


def captures_directory():
    return Path.home() / 'Desktop' / 'FrontDesk-AI-Live-Acceptance'


def read_capture(directory):
    path = directory / 'actual-results.json'
    if directory.is_symlink() or path.is_symlink() or not path.is_file():
        return None
    try:
        with path.open('rb') as stream:
            content = stream.read(MAX_CAPTURE_BYTES + 1)
        if len(content) <= MAX_CAPTURE_BYTES:
            return json.loads(content)
    except (OSError, ValueError):
        pass  # A check may still be writing this file. Refresh to read it again.
    return None


def saved_turn(connection, business_id, turn, question):
    request_id = turn.get('request_id')
    if not isinstance(request_id, str) or len(request_id) > 64:
        return {'question': question, 'outcome': 'capture_incomplete'}
    row = execute(connection, '''
        SELECT r.task_id, r.provider_response_id, r.provider_outcome,
               r.application_outcome, r.source_snapshot, r.source_ids,
               t.model, t.result
        FROM assistant_runs r
        JOIN ai_tasks t ON t.id = r.task_id AND t.business_id = r.business_id
        WHERE r.business_id = %s AND r.request_id = %s AND r.operation = 'shopping_assistant'
    ''', (business_id, request_id)).fetchone()
    if not row:
        return {'question': question, 'outcome': 'no_matching_request'}

    snapshot = json.loads(row['source_snapshot'])
    saved = {
        'question': question, 'request_id': request_id, 'task_id': row['task_id'],
        'provider_response_id': row['provider_response_id'], 'model': row['model'],
        'provider_outcome': row['provider_outcome'], 'outcome': row['application_outcome'],
        'rejection': stored_rejection(row['result'], snapshot),
    }
    response = turn.get('application_response')
    # Only the app's delivered answer is displayable. The provider's original
    # completion may contain unverified wording and stays in the private file.
    if (row['provider_outcome'] != 'succeeded'
            or saved['outcome'] not in ('accepted', 'accepted_with_limits')
            or turn.get('http_status') != 200 or not isinstance(response, dict)
            or response.get('mode') != 'live_ai' or response.get('task_id') != row['task_id']
            or response.get('request_id') != request_id):
        return saved

    answer = response.get('answer')
    if not isinstance(answer, str) or not answer.strip() or len(answer) > 1400:
        return saved
    follow_up = response.get('follow_up')
    preferences = response.get('preferences')
    preferences = preferences if isinstance(preferences, dict) else {}
    cited = set(json.loads(row['source_ids'] or '[]'))
    return {
        **saved, 'answer': answer,
        'follow_up': follow_up if isinstance(follow_up, str) and len(follow_up) <= 240 else '',
        'budget_cents': preferences.get('budget_cents') if type(preferences.get('budget_cents')) is int else None,
        'min_seats': preferences.get('min_seats') if type(preferences.get('min_seats')) is int else None,
        'sources': [source for source in snapshot if source['id'] in cited],
    }


def latest_capture(business_id):
    try:
        directories = sorted((folder for folder in captures_directory().iterdir()
                              if RUN_DIRECTORY.fullmatch(folder.name)), reverse=True)
    except OSError:
        return None
    for folder in directories[:20]:
        try:
            saved_at = datetime.strptime(folder.name, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
        capture = read_capture(folder)
        if not isinstance(capture, dict) or capture.get('business_id') != business_id:
            continue
        turns = capture.get('turns')
        if not isinstance(turns, list) or not 1 <= len(turns) <= len(QUESTIONS):
            continue
        if any(not isinstance(turn, dict) or turn.get('question') != question
               for turn, question in zip(turns, QUESTIONS)):
            continue
        with connect() as connection:
            return {'saved_at': saved_at, 'turns': [saved_turn(connection, business_id, turn, question)
                                                    for turn, question in zip(turns, QUESTIONS)]}
    return None
