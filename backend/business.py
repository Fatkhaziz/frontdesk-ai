"""Shared, approved business configuration and voluntary service inquiries."""
import json
import re
import uuid
from datetime import time
from typing import Literal, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .ai import now
from .db import connect, execute


class Strict(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class OpeningHours(Strict):
    day: Literal['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    opens: Optional[str] = None
    closes: Optional[str] = None

    @model_validator(mode='after')
    def valid_interval(self):
        if self.opens is None and self.closes is None:
            return self
        if not self.opens or not self.closes:
            raise ValueError('Enter both opening and closing time, or mark the day closed.')
        if any(not re.fullmatch(r'\d{2}:\d{2}', value) for value in (self.opens, self.closes)):
            raise ValueError('Use hours and minutes.')
        if time.fromisoformat(self.opens) >= time.fromisoformat(self.closes):
            raise ValueError('Closing time must follow opening time.')
        return self


class IntakeQuestion(Strict):
    id: str = Field(pattern=r'^[a-z][a-z0-9_-]{0,39}$')
    label: str = Field(min_length=1, max_length=160)
    required: bool = True


class Service(Strict):
    id: str = Field(pattern=r'^[a-z][a-z0-9_-]{0,39}$')
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default='', max_length=700)
    duration_minutes: int = Field(ge=5, le=1440)
    price_cents: Optional[int] = Field(default=None, ge=0, le=1000000000)
    questions: list[IntakeQuestion] = Field(default_factory=list, max_length=12)

    @model_validator(mode='after')
    def unique_question_ids(self):
        if len({q.id for q in self.questions}) != len(self.questions):
            raise ValueError('Question IDs must be unique within a service.')
        return self


class FAQ(Strict):
    question: str = Field(min_length=1, max_length=200)
    answer: str = Field(min_length=1, max_length=1200)


def normalize(value):
    return ' '.join(re.findall(r'\w+', value.casefold()))


class Profile(Strict):
    name: str = Field(min_length=1, max_length=120)
    domain: Literal['dealership', 'salon', 'photography_studio']
    about: str = Field(default='', max_length=1200)
    contact: str = Field(min_length=1, max_length=300)
    time_zone: str = Field(default='America/New_York', max_length=80)
    hours: list[OpeningHours] = Field(min_length=7, max_length=7)
    services: list[Service] = Field(min_length=1, max_length=20)
    faqs: list[FAQ] = Field(default_factory=list, max_length=30)

    @field_validator('time_zone')
    @classmethod
    def valid_time_zone(cls, value):
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError('Use a recognized time zone, such as America/New_York.')
        return value

    @model_validator(mode='after')
    def unique_identifiers(self):
        if len({day.day for day in self.hours}) != 7:
            raise ValueError('Include every weekday once.')
        if len({service.id for service in self.services}) != len(self.services):
            raise ValueError('Service IDs must be unique.')
        questions = [normalize(faq.question) for faq in self.faqs]
        if any(not question for question in questions) or len(set(questions)) != len(questions):
            raise ValueError('FAQ questions must be distinct and contain words.')
        return self


class SaveProfile(Strict):
    expected_revision: int = Field(ge=0)
    profile: Profile


class PublishProfile(Strict):
    expected_revision: int = Field(gt=0)
    confirm_approval: Literal[True]


class BusinessQuestion(Strict):
    question: str = Field(min_length=1, max_length=1000)


class BusinessInquiry(Strict):
    request_key: uuid.UUID
    expected_revision: int = Field(gt=0)
    service_id: Optional[str] = None
    message: str = Field(min_length=1, max_length=1000)
    contact: str = Field(min_length=3, max_length=300)
    answers: dict[str, str] = Field(default_factory=dict, max_length=12)


class InquiryStatus(Strict):
    status: Literal['open', 'pending', 'resolved']


def public_profile(c, business_id, lock=False):
    suffix = ' FOR UPDATE' if lock and not c.__class__.__module__.startswith('sqlite3') else ''
    row = execute(c, 'SELECT * FROM business_profiles WHERE business_id=%s AND published IS NOT NULL' + suffix, (business_id,)).fetchone()
    if not row:
        raise HTTPException(404, 'This business page is unavailable.')
    return {**json.loads(row['published']), 'revision': row['published_revision']}


def format_inquiry(row):
    return {**dict(row), 'answers': json.loads(row['answers']), 'answer_labels': json.loads(row['answer_labels']), 'kind': 'business', 'vehicle_name': row['service_name']}


def create_router(identity, owner):
    router = APIRouter()

    @router.get('/api/workspace')
    def workspace(member=Depends(identity)):
        with connect() as c:
            business = execute(c, 'SELECT name FROM businesses WHERE id=%s', (member['business_id'],)).fetchone()
            row = execute(c, 'SELECT * FROM business_profiles WHERE business_id=%s', (member['business_id'],)).fetchone()
        return {
            'id': member['business_id'], 'name': business['name'], 'role': member['role'],
            'revision': row['revision'] if row else 0,
            'profile': json.loads(row['profile']) if row else None,
            'published_revision': row['published_revision'] if row else None,
            'published': json.loads(row['published']) if row and row['published'] else None,
        }

    @router.put('/api/business/profile')
    def save_profile(body: SaveProfile, member=Depends(owner)):
        profile = body.profile.model_dump_json()
        with connect() as c:
            if body.expected_revision == 0:
                row = execute(c, 'INSERT INTO business_profiles(business_id,revision,profile) VALUES(%s,1,%s) ON CONFLICT(business_id) DO NOTHING RETURNING revision', (member['business_id'], profile)).fetchone()
            else:
                row = execute(c, 'UPDATE business_profiles SET profile=%s,revision=revision+1 WHERE business_id=%s AND revision=%s RETURNING revision', (profile, member['business_id'], body.expected_revision)).fetchone()
            if not row:
                raise HTTPException(409, 'Business settings changed. Reload before saving again.')
        return {'revision': row['revision']}

    @router.post('/api/business/profile/publish')
    def publish_profile(body: PublishProfile, member=Depends(owner)):
        with connect() as c:
            row = execute(c, 'UPDATE business_profiles SET published=profile,published_revision=revision,approved_by=%s WHERE business_id=%s AND revision=%s RETURNING revision', (member['subject'], member['business_id'], body.expected_revision)).fetchone()
            if not row:
                raise HTTPException(409, 'Saved settings changed. Reload and review the current revision.')
            execute(c, 'INSERT INTO business_profile_events VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(business_id,revision,action) DO NOTHING', (str(uuid.uuid4()), member['business_id'], member['subject'], row['revision'], 'publish', now()))
        return {'revision': row['revision'], 'url': '/business/' + member['business_id']}

    @router.post('/api/business/profile/unpublish')
    def unpublish_profile(member=Depends(owner)):
        with connect() as c:
            row = execute(c, 'UPDATE business_profiles SET published=NULL,published_revision=NULL WHERE business_id=%s RETURNING revision', (member['business_id'],)).fetchone()
            if not row:
                raise HTTPException(404, 'Business settings are not configured.')
            execute(c, 'INSERT INTO business_profile_events VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(business_id,revision,action) DO NOTHING', (str(uuid.uuid4()), member['business_id'], member['subject'], row['revision'], 'unpublish', now()))
        return {'unpublished': True}

    @router.get('/api/public/businesses/{business_id}')
    def business_page(business_id: str):
        with connect() as c:
            return public_profile(c, business_id)

    @router.post('/api/public/businesses/{business_id}/questions')
    def answer(business_id: str, body: BusinessQuestion, request: Request):
        from .business_qa import answer_question
        with connect() as c:
            profile = public_profile(c, business_id)
        def current():
            with connect() as c:
                return public_profile(c, business_id)
        return answer_question(business_id, profile, body.question, request.state.request_id, current)

    @router.post('/api/public/businesses/{business_id}/inquiries', status_code=201)
    def submit_inquiry(business_id: str, body: BusinessInquiry):
        answers = json.dumps(body.answers, sort_keys=True)
        key = str(body.request_key)
        with connect() as c:
            # Serialize request retries with settings publication on this business.
            profile = public_profile(c, business_id, lock=True)
            existing = execute(c, 'SELECT * FROM business_inquiries WHERE business_id=%s AND request_key=%s', (business_id, key)).fetchone()
            if existing:
                if (existing['message'], existing['contact'], existing['answers'], existing['service_id'], existing['profile_revision']) != (body.message, body.contact, answers, body.service_id, body.expected_revision):
                    raise HTTPException(409, 'This request key was already used for different details.')
                return {'id': existing['id'], 'status': existing['status']}
            if body.expected_revision != profile['revision']:
                raise HTTPException(409, 'The business updated its request form. Reload and review it before submitting.')
            service = next((s for s in profile['services'] if s['id'] == body.service_id), None)
            if body.service_id is not None and service is None:
                raise HTTPException(422, 'Select a service offered by this business.')
            questions = service['questions'] if service else []
            allowed = {q['id'] for q in questions}
            if set(body.answers) - allowed or any(len(v) > 500 or not v.strip() for v in body.answers.values()):
                raise HTTPException(422, 'Use the questions on the current request form.')
            if any(q['required'] and not body.answers.get(q['id'], '').strip() for q in questions):
                raise HTTPException(422, 'Please answer the required service questions.')
            inquiry_id = str(uuid.uuid4())
            labels = json.dumps({q['id']: q['label'] for q in questions})
            execute(c, 'INSERT INTO business_inquiries VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (inquiry_id, business_id, key, profile['revision'], body.service_id, service['name'] if service else 'General inquiry', body.message, body.contact, answers, labels, 'open', now()))
        return {'id': inquiry_id, 'status': 'open'}

    @router.patch('/api/business/inquiries/{inquiry_id}')
    def update_inquiry(inquiry_id: str, body: InquiryStatus, member=Depends(identity)):
        with connect() as c:
            row = execute(c, 'UPDATE business_inquiries SET status=%s WHERE id=%s AND business_id=%s RETURNING id', (body.status, inquiry_id, member['business_id'])).fetchone()
            if not row:
                raise HTTPException(404, 'Inquiry not found.')
        return {'status': body.status}

    return router
