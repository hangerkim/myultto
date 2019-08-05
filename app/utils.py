from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from bs4 import BeautifulSoup


def requests_retry_session(max_retries=5):
    session = requests.Session()
    retry = Retry(total=max_retries, read=max_retries, connect=max_retries,
                  backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def get_article_meta(url):
    sess = requests_retry_session()
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/75.0.3770.142 Safari/537.36')
    }
    req = sess.get(url, headers=headers)
    sess.close()
    bs_parsed = BeautifulSoup(req.text, features='lxml')
    gallery_id = (bs_parsed.find('input', attrs={'id': 'gallery_id'})
                  .attrs['value'])
    article_no = (bs_parsed.find('input', attrs={'id': 'no'})
                  .attrs['value'])
    e_s_n_o = (bs_parsed.find('input', attrs={'id': 'e_s_n_o'})
               .attrs['value'])
    date = bs_parsed.select('.gall_writer .gall_date')[0].text
    date = datetime.strptime(date, '%Y.%m.%d %H:%M:%S')
    return gallery_id, article_no, e_s_n_o, date


def get_raw_comments(gallery_id, article_no, e_s_n_o, max_page=10):
    request_url = 'https://gall.dcinside.com/board/comment/'
    headers = {
        'Origin': 'https://gall.dcinside.com',
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/75.0.3770.142 Safari/537.36'),
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
    }
    comments = []
    for page in range(max_page):
        request_data = {
            'id': gallery_id,
            'no': article_no,
            'cmt_id': gallery_id,
            'cmt_no': article_no,
            'comment_page': page,
            'e_s_n_o': e_s_n_o
        }
        sess = requests_retry_session()
        req = sess.post(url=request_url, data=request_data, headers=headers)
        sess.close()
        page_comments = req.json()['comments']
        if not page_comments:
            break
        comments.extend(page_comments)
    return comments


def parse_comment_date(article_date, comment_date_str):
    # The date (and time) in the comment data does not contain
    # year information. In most cases, it should just be fine by setting
    # it to the same value as the article's (say 2019), however
    # there always exist special cases, so for the completion
    # it predicts the correct year in a heuristic and dirty way.
    comment_month = int(comment_date_str[:2])
    comment_day = int(comment_date_str[3:5])
    comment_hour = int(comment_date_str[6:8])
    comment_minute = int(comment_date_str[9:11])
    comment_second = int(comment_date_str[12:14])
    if comment_month >= article_date.month:
        # Both are in the same year.
        comment_year = article_date.year
    else:
        # A year has passed.
        comment_year = article_date.year + 1
    comment_date = datetime(comment_year, comment_month, comment_day,
                            comment_hour, comment_minute, comment_second)
    return comment_date


def build_candidates(raw_comments, allow_guest, time_limit, article_date):
    candidates = set()
    # Make time_limit inclusive by extending it by 1 minute.
    time_limit = datetime(time_limit.year, time_limit.month, time_limit.day,
                          time_limit.hour, time_limit.minute + 1, 0)
    for comment in raw_comments:
        if comment.get('ip'):
            if not allow_guest:
                continue
            candidate = f'{comment["name"]} ({comment["ip"]})'
        elif comment.get('user_id'):
            candidate = f'{comment["name"]} ({comment["user_id"][:4]})'
        else:
            continue
        comment_date = parse_comment_date(
            article_date=article_date, comment_date_str=comment['reg_date'])
        if time_limit < comment_date:
            continue
        # Make sure that there's no illegal character (comma for now)
        candidate = candidate.replace(',', '.')
        candidates.add(candidate)
    return list(candidates)


def get_candidates_from_article(article_url, allow_guest, time_limit):
    article_meta = get_article_meta(article_url)
    gallery_id, article_no, e_s_n_o, article_date = article_meta
    raw_comments = get_raw_comments(
        gallery_id=gallery_id, article_no=article_no, e_s_n_o=e_s_n_o)
    candidates = build_candidates(
        raw_comments=raw_comments, allow_guest=allow_guest,
        time_limit=time_limit, article_date=article_date)
    return candidates


def write_result_to_db(db, candidates, winners):
    kst_now = datetime.utcnow() + timedelta(hours=9)
    kst_now_text = kst_now.strftime('%Y-%m-%d %H:%M:%S')
    candidates_text = ','.join(candidates)
    winners_text = ','.join(winners)
    query = ('INSERT INTO results (created_at, candidates, winners) '
             'VALUES (?, ?, ?)')
    cur = db.execute(query, (kst_now_text, candidates_text, winners_text))
    result_id = cur.lastrowid
    db.commit()
    return result_id


def fetch_recent_results(db, count=50):
    query = ('SELECT id, created_at, candidates, winners '
             'FROM results '
             'ORDER BY id DESC '
             'LIMIT ?')
    cur = db.execute(query, (count,))
    rows = cur.fetchall()
    recent_results = []
    for row in rows:
        recent_results.append({
            'id': row[0],
            'created_at': row[1],
            'candidates': row[2].split(','),
            'winners': row[3].split(',')
        })
    return recent_results


def fetch_result(db, result_id):
    query = ('SELECT id, created_at, candidates, winners '
             'FROM results '
             'WHERE id = ?')
    cur = db.execute(query, (result_id,))
    row = cur.fetchone()
    return {'id': row[0],
            'created_at': row[1],
            'candidates': row[2].split(','),
            'winners': row[3].split(',')}
