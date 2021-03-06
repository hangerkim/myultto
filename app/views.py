import logging
import os
import random
import time

import dateutil.parser
from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, render_template, request, url_for
from sqlalchemy import and_

from app import utils
from app.models import db, Candidate, Result

bp = Blueprint('views', __name__, url_prefix='/')


@bp.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename is not None:
            path = os.path.join(bp.root_path, endpoint, filename)
            values['ts'] = int(os.stat(path).st_mtime)
    return url_for(endpoint, **values)


def calculate_unfair_score(name, days):
    datetime_threshold = datetime.now() - timedelta(days=days)
    result_candidates = (
        db.session.query(Result, Candidate)
        .join(Candidate)
        .filter(Candidate.name == name)
        .filter(Result.created_at > datetime_threshold)
        .all()
    )

    num_tries = len(result_candidates)
    num_wins = 0

    score_sum = 0
    for result, candidate in result_candidates:
        if candidate.is_winner:
            num_winners = sum(int(c.is_winner) for c in result.candidates)
            score = len(result.candidates) / num_winners
            # Wins at 100% lottery will not be counted
            if len(result.candidates) > num_winners:
                score_sum += score
                num_wins += 1
            else:
                num_tries -= 1

    unfair_score = score_sum / max(1, num_tries)

    return num_tries, num_wins, unfair_score


@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/extract', methods=['POST'])
def extract_candidates():
    json_data = request.get_json()
    article_url = json_data['article_url']
    allow_guest = json_data['allow_guest']

    # TODO: save this info into DB
    print(article_url)

    # UTC
    time_limit = dateutil.parser.parse(json_data['time_limit'])
    # Convert to KST
    time_limit = time_limit + timedelta(hours=9)
    # Remove timezone info
    time_limit = time_limit.replace(tzinfo=None)

    candidates = utils.get_candidates_from_article(
        article_url=article_url, allow_guest=allow_guest,
        time_limit=time_limit)
    return jsonify({'candidates': candidates})


@bp.route('/draw', methods=['POST'])
def draw_lottery():
    json_data = request.get_json()
    num_winners = json_data['num_winners']
    announcement_delay = json_data['announcement_delay']
    cand_names = json_data['candidates']

    created_at = datetime.now(timezone(timedelta(hours=9)))
    created_at = created_at.replace(tzinfo=None)
    published_at = created_at + timedelta(minutes=announcement_delay)
    seed = int(created_at.timestamp() * 1000)
    result = Result(created_at=created_at, published_at=published_at,
                    seed=seed, drawer_ip=request.remote_addr)
    candidates = [Candidate(name=name, result=result) for name in cand_names]

    random.seed(seed)
    cand_indices = list(range(len(cand_names)))
    for _ in range(10):
        random.shuffle(cand_indices)
    winner_indices = random.sample(cand_indices, num_winners)
    winners = [candidates[i] for i in winner_indices]
    for winner in winners:
        winner.is_winner = True

    db.session.add(result)
    db.session.commit()

    winner_dicts = []
    for winner in winners:
        winner_dict = {}
        winner_dict['name'] = winner.name
        unfair_stats_week = calculate_unfair_score(name=winner.name, days=7)
        unfair_stats_month = calculate_unfair_score(name=winner.name, days=30)
        winner_dict['unfair'] = {
            'week': {'num_tries': unfair_stats_week[0],
                     'num_wins': unfair_stats_week[1],
                     'unfair_score': unfair_stats_week[2]},
            'month': {'num_tries': unfair_stats_month[0],
                      'num_wins': unfair_stats_month[1],
                      'unfair_score': unfair_stats_month[2]}
        }
        winner_dicts.append(winner_dict)

    result_url = url_for('views.show_result', result_id=result.id)
    return jsonify({'winners': winner_dicts,
                    'result_id': result.id,
                    'result_url': result_url})


@bp.route('/recent_results', methods=['GET'])
def recent_results():
    recent_results = Result.query.order_by(Result.id.desc()).limit(50).all()
    return render_template('recent_results.html', results=recent_results)


@bp.route('/result/<int:result_id>')
def show_result(result_id):
    result = Result.query.get(result_id)
    unfair_dict = {}
    winners = [c for c in result.candidates if c.is_winner]
    for winner in winners:
        unfair_stats_week = calculate_unfair_score(name=winner.name, days=7)
        unfair_stats_month = calculate_unfair_score(name=winner.name, days=30)
        unfair_dict[winner.name] = {
            'week': {'num_tries': unfair_stats_week[0],
                     'num_wins': unfair_stats_week[1],
                     'unfair_score': unfair_stats_week[2]},
            'month': {'num_tries': unfair_stats_month[0],
                      'num_wins': unfair_stats_month[1],
                      'unfair_score': unfair_stats_month[2]}
        }
    return render_template('show_result.html',
                           result=result,
                           unfair=unfair_dict)
