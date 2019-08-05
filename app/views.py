import dateutil.parser
from datetime import datetime, timedelta

import random
from flask import jsonify, render_template, request

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

    candidates = utils.get_candidates_from_article(
        article_url=article_url, allow_guest=allow_guest,
        time_limit=time_limit)
    return jsonify({'candidates': candidates})


@app.route('/draw', methods=['POST'])
def draw_lottery():
    json_data = request.get_json()
    num_winners = json_data['num_winners']
    candidates = json_data['candidates']

    shuffled_candidates = candidates.copy()
    random.shuffle(shuffled_candidates)
    winners = shuffled_candidates[:num_winners]

    db = get_db()
    utils.write_result_to_db(db=db, candidates=candidates, winners=winners)

    return jsonify({'winners': winners})
