# -- coding: utf-8 --
# @Time : 2024/5/27 11:22
# @Author : PinBar
# @File : mysql.py
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, scoped_session
from config.settings import DB_URL, ASYNC_DB_URL

engine = create_engine(
    url=DB_URL,
    pool_recycle=300,
    pool_size=30,
    max_overflow=10,
    pool_timeout=30,
    echo=False,
)
async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
)
Session = sessionmaker(bind=engine)
session = scoped_session(Session)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)
