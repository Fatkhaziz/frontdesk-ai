"""Bounded rejection metadata. Never serialize exception messages or inputs."""
STAGES = {'provider', 'envelope', 'json', 'shape', 'preferences', 'sources', 'claims', 'publication', 'internal'}
REASONS = {'provider_timeout', 'provider_rate_limit', 'provider_http_error', 'provider_error',
           'invalid_envelope', 'incomplete_output', 'invalid_json', 'shape', 'answer',
           'invalid_preferences', 'sources', 'unapproved_source', 'recommendations',
           'hard_constraint', 'unselected_recommendation', 'uncited_recommendation',
           'invented_preference', 'removed_constraint', 'invented_feature_requirement',
           'removed_feature_requirement', 'unsupported_number', 'unsupported_guarantee',
           'stale_source', 'question_shape', 'question_length', 'questions', 'internal_error'}
FIELDS = {'answer', 'follow_up', 'preferences', 'source_ids', 'recommended_ids', 'questions',
          'budget_cents', 'budget_kind', 'min_seats', 'max_mileage', 'body_style', 'fuel_type',
          'drivetrain', 'priorities', 'required_features'}


class Rejection(ValueError):
    def __init__(self, stage, reason, field=None, source_id=None):
        super().__init__('AI response rejected')
        self.stage = stage if stage in STAGES else 'internal'
        self.reason = reason if reason in REASONS else 'internal_error'
        self.field = field if field in FIELDS else None
        self.source_id = source_id

    def diagnostic(self, sources):
        # An arbitrary provider string is never an identifier worth logging.
        approved = {s['id'] for s in sources}
        return {'stage': self.stage, 'reason': self.reason, 'field': self.field,
                'source_id': self.source_id if isinstance(self.source_id, str) and len(self.source_id) <= 240 and self.source_id in approved else None}


def stored_rejection(value, sources):
    import json
    try:
        data = json.loads(value) if value else None
        rejection = data.get('rejection') if isinstance(data, dict) else None
        if not isinstance(rejection, dict) or rejection.get('stage') not in STAGES or rejection.get('reason') not in REASONS:
            return None
        return Rejection(rejection['stage'], rejection['reason'], rejection.get('field'), rejection.get('source_id')).diagnostic(sources)
    except (ValueError, TypeError):
        return None
