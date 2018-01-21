from flask import *
from constants import *
from models import session, Meme, User, Like
from sqlalchemy import and_, func
from config import config
from flask_httpauth import HTTPTokenAuth
import redis
from google.oauth2 import id_token
from google.auth.transport import requests


conf = config('server', default={
    "main_url": "http://127.0.0.1:8080",
    "max_count_per_query": 20,
    'redis_host': 'localhost',
    'redis_port': 6379,
    'redis_prefix': 'memes_',
    'google_client_id': 'Google client id'
})

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Token')
cache = redis.StrictRedis(host=conf['redis_host'], port=conf['redis_port'])


@app.route('/memes/')
def get_memes():
    if request.method != 'GET':
        abort(BAD_REQUEST)

    count = min(conf['max_count_per_query'], int(request.args.get('count', 10)))
    start_id = int(request.args.get('start_id', LAST_ID))

    if start_id == LAST_ID:
        resp = session.query(Meme)\
            .order_by(Meme.id.desc())\
            .limit(count)\
            .all()
    else:
        resp = session.query(Meme)\
            .order_by(Meme.id.desc())\
            .filter(and_(start_id - count + 1 <= Meme.id, Meme.id <= start_id))\
            .all()

    result = {
        'memes': []
    }

    for meme in resp:
        result['memes'].append({
            'id': meme.id,
            'img_url': '{}/img/{}.jpg'.format(conf['main_url'], meme.img)
        })

    return jsonify(result)


def get_google_id(token):
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), conf['google_client_id'])

        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        return id_info['sub']
    except ValueError:
        return -1
    except IndexError:
        return -1


@auth.verify_token
def verify_token(token):
    if not cache.exists(conf['redis_prefix'] + token):
        google_id = str(get_google_id(token))
        cache.set(conf['redis_prefix'] + token, google_id, ex=3600)

    google_id = str(cache.get(conf['redis_prefix'] + token))
    if google_id == -1:
        return False

    user = session.query(User).filter(User.google_id == google_id).first()
    if user is None:
        user = User(google_id=google_id)
        session.add(user)
        session.commit()

    g.current_user = user
    return True


@app.route('/like/<int:meme_id>', methods=['POST'])
@auth.login_required
def set_like(meme_id):
    if 'score' not in request.form:
        abort(BAD_REQUEST)

    score = int(request.form)

    if not (-1 <= score <= 1):
        abort(BAD_REQUEST)

    user = g.current_user
    meme = session.query(Meme).filter(Meme.id == meme_id).first()

    if meme is None:
        abort(BAD_REQUEST)

    like = session.query(Like).filter(and_(Like.meme_id == meme.id, Like.user_id == user.id)).first()
    old_score = 0 if like is None else like.score

    if like is None:
        like = Like(meme_id=meme.id, user_id=user.id, score=score)
        session.add(like)
    else:
        like.score = score

    meme.rating = meme.rating - old_score + score
    session.commit()
    return 'OK', CREATED


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
