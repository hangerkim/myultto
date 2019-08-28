from app import app


@app.template_filter('join_candidates')
def join_candidates(candidates):
    return ', '.join(c.name for c in candidates)
