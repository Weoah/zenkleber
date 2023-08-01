import sys
import logging
import requests
from zenpy import Zenpy

from src.config import ZENDESK_DOMAIN, ZENDESK_CREDENTIALS


def start_zendesk_session() -> Zenpy:
    zendesk_session = Zenpy(**ZENDESK_CREDENTIALS)
    if not zendesk_session:
        raise SystemError("Zenpy Session not finded")
    return zendesk_session


zendesk_session = start_zendesk_session()


def request_zendesk(url: str):
    response = requests.get(f'{ZENDESK_DOMAIN}/{url}', auth=(
        ZENDESK_CREDENTIALS['email'], ZENDESK_CREDENTIALS['password']))
    return response.json()['ticket']


def logger(name="log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    system_handler = logging.StreamHandler(sys.stdout)
    system_handler.setLevel(logging.DEBUG)
    system_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(f"{name}.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(system_handler)
    logger.addHandler(file_handler)

    return logger


log = logger()
