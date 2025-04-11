from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from lib.streamlit_common import *

common_page_initialization("app.py")
