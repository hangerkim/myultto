import random
import time

import dateutil.parser
from datetime import timedelta
from flask import jsonify, render_template, request, url_for

from app import app, get_db, utils


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/extract', methods=['POST'])
def extract_candidates():
    json_data = request.get_json()
    article_url = json_data['article_url']
    allow_guest = json_data['allow_guest']

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


@app.route('/draw', methods=['POST'])
def draw_lottery():
    json_data = request.get_json()
    num_winners = json_data['num_winners']
    candidates = json_data['candidates']
    seed = int(time.time() * 1000)

    shuffled_candidates = candidates.copy()
    random.seed(seed)
    random.shuffle(shuffled_candidates)
    winners = shuffled_candidates[:num_winners]

    db = get_db()
    result_id = utils.write_result_to_db(
        db=db, candidates=candidates, winners=winners, seed=seed)
    result_url = url_for('show_result', result_id=result_id)

    return jsonify({'winners': winners, 'result_id': result_id,
                    'result_url': result_url})


@app.route('/recent_results', methods=['GET'])
def recent_results():
    db = get_db()
    recent_results = utils.fetch_recent_results(db)
    return render_template('recent_results.html', results=recent_results)


@app.route('/result/<int:result_id>')
def show_result(result_id):
    db = get_db()
    result = utils.fetch_result(db, result_id=result_id)
    return render_template('show_result.html', result=result)
