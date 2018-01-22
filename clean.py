#!/usr/bin/python3

import os
from models import session, Base, engine
from config import config
import redis

session.commit()
session.close()
Base.metadata.drop_all(engine)

conf = config('server', default={
    'main_url': 'http://127.0.0.1:8080',
    'max_count_per_query': 20,
    'redis_host': 'localhost',
    'redis_port': 6379,
    'redis_prefix': 'memes_',
    'google_client_id': 'Google client id'
})

cache = redis.StrictRedis(host=conf['redis_host'], port=conf['redis_port'], charset="utf-8", decode_responses=True)
cache.flushdb()

os.system('rm -r ./vk_loader/loaded_ids')
os.system('rm -r ./img')
