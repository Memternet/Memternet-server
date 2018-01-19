import vk_loader.vk_api as vk
from config import config
import uuid
import requests
from models import session, Meme
import os

PHOTO_URL_FIELDS = [
    "photo_75",
    "photo_130",
    "photo_604",
    "photo_807",
    "photo_1280",
    "photo_2560"
]


conf = config('loader', default={
    "access_token": "Enter VK access token here.",
    "sources": [],
    "load_limit_per_source": 20,
    "remember_loaded_ids": 50,
    "images_dir": "img/"
})


def get_random_id():
    return uuid.uuid4().hex


def is_post_meme(post):
    if 'id' not in post:
        return False

    if 'attachments' not in post:
        return False

    if 'is_pinned' in post and post['is_pinned'] == 1:
        return False

    if 'marked_as_ads' in post and post['marked_as_ads'] == 1:
        return False

    attachments = post['attachments']

    if type(attachments) != list:
        return False

    if len(attachments) != 1:
        return False

    photo = attachments[0]

    if 'type' not in photo:
        return False

    if photo['type'] != 'photo' or 'photo' not in photo:
        return False

    return True


def get_last_loaded_ids(source_id):
    try:
        with open('vk_loader/loaded_ids/' + str(source_id), 'r') as file:
            return list(map(lambda s: int(s.replace('\n', '')), file.readlines()))
    except IOError:
        return []


def save_loaded_ids(source_id, ids):
    actual = ids + get_last_loaded_ids(source_id)
    remember = conf['remember_loaded_ids']
    if len(actual) > remember:
        actual = actual[:remember]
    try:
        with open('vk_loader/loaded_ids/' + str(source_id), 'w') as file:
            file.write('\n'.join(map(str, actual)))
    except IOError:
        print('Can\'t save ids!')


def get_unique_post_id(source_id, post_id):
    return str(source_id) + '_' + str(post_id)


def get_new_posts():
    result = []

    for source_id in conf['sources']:
        loaded_ids = set(get_last_loaded_ids(source_id))
        to_save = []

        finished = False
        considered = 0

        while not finished:
            posts = vk.get_posts(source_id, offset=considered)['items']
            count = len(posts)

            if count == 0:
                finished = True
                continue

            for item in posts:
                if considered == conf['load_limit_per_source']:
                    finished = True
                    break

                considered += 1

                if 'id' not in item:
                    continue

                post_id = item['id']
                if post_id in loaded_ids:
                    finished = True
                    continue

                to_save.append(post_id)
                result.append(item)

        if len(to_save) > 0:
            save_loaded_ids(source_id, to_save)

    return result


def download(url, filename):
    with open(filename, "wb") as file:
        response = requests.get(url)
        file.write(response.content)


def __main__():
    posts = get_new_posts()
    posts = filter(is_post_meme, posts)
    os.makedirs(conf['images_dir'], exist_ok=True)
    os.makedirs('vk_loader/loaded_ids', exist_ok=True)

    for post in posts:
        photo = post['attachments'][0]['photo']
        ptr = len(PHOTO_URL_FIELDS) - 1

        while ptr >= 0 and PHOTO_URL_FIELDS[ptr] not in photo:
            ptr -= 1

        if ptr < 0:
            continue

        photo_url = photo[PHOTO_URL_FIELDS[ptr]]
        assert(photo_url.endswith('.jpg'))

        photo_id = get_random_id()

        try:
            print('loading', photo_id, photo_url)
            download(photo_url, conf['images_dir'] + photo_id + '.jpg')
        except IOError:
            print('Downloading/saving an image failed!')
            continue

        session.add(Meme(img=photo_id))

    session.commit()


__main__()
