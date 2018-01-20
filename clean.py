#!/usr/bin/python3

import os
from models import session, Base, engine

session.commit()
session.close()
Base.metadata.drop_all(engine)

os.system('rm -r ./vk_loader/loaded_ids')
os.system('rm -r ./img')
