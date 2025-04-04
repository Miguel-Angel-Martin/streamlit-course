import os
from contextlib import contextmanager
import functools
import streamlit as st

from lib.logging import logger

@functools.cache
def connection():
    return st.connection("sqlite", type="sql", url=os.getenv("DATABASE_URL"))

@contextmanager
def transaction():
    session = connection().session
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error in transaction: {e}")
    finally:
        session.close()

@contextmanager
def session():
    session = connection().session
    try:
        yield session
    finally:
        session.close()
