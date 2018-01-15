import requests
from config import config


def api(method, params):
    url = 'https://api.vk.com/method/{}'.format(method)
    params['access_token'] = config('loader')['access_token']
    params['v'] = '5.69'
    try:
        data = requests.get(url, params=params).json()
        return data['response']
    except ValueError:
        return {}
    except IndexError:
        return {}


def get_posts(source_id, offset=0, count=100):
    data = api('wall.get', {
        'owner_id': source_id,
        'offset': offset,
        'count': count
    })

    if 'items' not in data:
        return []

    return data
