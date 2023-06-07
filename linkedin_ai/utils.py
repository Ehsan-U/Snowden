
""" Helper functions """

import csv
import json
import random
import time
import uuid
from copy import deepcopy
from linkedin_ai import settings
from linkedin_ai.logging_config import logger
from requests import Session
from tinydb import TinyDB, Query


def init_db():
    logger.info("Initializing database")
    return (TinyDB(".tinydb/db.json"), Query())

def create_session(cookies):
    session = Session()
    session.cookies.update(cookies)
    return session

def send_request(s, method: str = None, url: str = None, **kwargs):
    try:
        sleep_time = random.choice(settings.SLEEP_RANGE)
        logger.debug(f"Sleeping for {sleep_time}")
        time.sleep(sleep_time)
        response = s.request(
            method=method,
            url=url,
            headers=kwargs['headers'],
            data=json.dumps(kwargs['data']) if kwargs.get('data') else None,
        )
    except Exception as e:
        logger.error(e)
        response = None
    finally:
        return response

def build_headers(csrf_token, keyword=None, invite=None):
    headers = deepcopy(settings.SEARCH_HEADERS)
    if keyword:
        headers['Referer'] = f'https://www.linkedin.com/search/results/people/?keywords={keyword}&origin=GLOBAL_SEARCH_HEADER'
    headers['Csrf-Token'] = csrf_token
    if invite:
        headers.update(settings.INVITE)
    return headers

def load_urls():
    urls = []
    with open('data/urls.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            urls.append(row[0])
    return urls

def generate_token():
    return str(uuid.uuid4())

def get_csrf_token(cookies):
    return cookies.get("JSESSIONID").replace('"','')
