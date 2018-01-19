#!/usr/bin/python3

import os
from models import session, Meme

session.query(Meme).delete()
session.commit()

os.system('rm -r ./vk_loader/loaded_ids')
os.system('rm -r ./img')
