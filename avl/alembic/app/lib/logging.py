import sys
import logging
from datetime import datetime
import streamlit as st

__all__ = ['logger']

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

class StreamlitHandler(logging.Handler):

    def emit(self, record):
        match record.levelname:
            case 'INFO':
                icon = ':material/info:'
            case 'WARNING':
                icon = ':material/warning:'
            case 'ERROR':
                icon = ':material/error:'
            case 'CRITICAL':
                icon = ':material/error:'
            case _:
                icon = None
        if record.levelno > logging.DEBUG and record.levelno <= logging.WARNING:
            st.toast(record.getMessage(), icon=icon)
        elif record.levelno > logging.WARNING:
            st.error(record.getMessage(), icon=icon)
    

def _init(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt=DATE_FORMAT))
    logger.addHandler(stdout)
    logger.addHandler(StreamlitHandler())
    return logger


logger = _init('ibe.material-tracker')