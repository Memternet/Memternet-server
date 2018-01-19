from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, Column, Integer, String
from config import config


conf = config('db', default={
    "db_schema": "postgresql://memes_user:kvdiempzfhnq@localhost/memes"
})


engine = create_engine(conf['db_schema'])
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = session.query_property()


class Meme(Base):
    __tablename__ = 'memes'

    id = Column(Integer, primary_key=True)
    img = Column(String(32), nullable=False)


Base.metadata.create_all(engine)

