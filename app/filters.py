from flask import Blueprint

bp = Blueprint('filters', __name__)


@bp.app_template_filter('join_candidates')
def join_candidates(candidates):
    return ', '.join(c.name for c in candidates)
