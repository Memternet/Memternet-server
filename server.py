from flask import *
from constants import *
from models import session, Meme
from sqlalchemy import and_
from config import config


conf = config('server', default={
    "main_url": "http://127.0.0.1:8080",
    "max_count_per_query": 20
})

app = Flask(__name__)


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


@app.route('/img/<path:filename>')
def get_img(filename):
    return send_from_directory('img', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
