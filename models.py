from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Index
from config import config


conf = config('db', default={
    "db_schema": "Enter your db schema here."
})


engine = create_engine(conf['db_schema'])
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = session.query_property()


class Meme(Base):
    __tablename__ = 'memes'

    id = Column(Integer, primary_key=True)
    img = Column(String(32), nullable=False)
    rating = Column(Integer, default=0)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    google_id = Column(String(50), nullable=False, unique=True, index=True)


class Like(Base):
    __tablename__ = 'likes'

    id = Column(Integer, primary_key=True)
    meme_id = Column(Integer, ForeignKey('memes.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    score = Column(Integer, nullable=False)


Index('likes_meme_user_idx', Like.meme_id, Like.user_id, unique=True)
Base.metadata.create_all(engine)
