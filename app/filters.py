from datetime import datetime, timedelta, timezone

from flask import Blueprint

bp = Blueprint('filters', __name__)


@bp.app_template_filter('join_candidates')
def join_candidates(candidates):
    return ', '.join(c.name for c in candidates)


@bp.app_template_filter('is_published')
def is_published(result):
    now = datetime.now(timezone(timedelta(hours=9)))
    now = now.replace(tzinfo=None)
    return now > result.published_at
