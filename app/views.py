from datetime import datetime, timedelta

import random
from flask import jsonify, render_template, request

from app import app, utils


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/extract', methods=['POST'])
def extract_candidates():
    json_data = request.get_json()
    article_url = json_data['article_url']
    allow_guest = json_data['allow_guest']

    # UTC
    time_limit = datetime.strptime(
        json_data['time_limit'], '%Y-%m-%dT%H:%M:%S.%f%z')
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
    random.shuffle(candidates)
    winners = candidates[:num_winners]
    return jsonify({'winners': winners})
