import requests
from zenpy import Zenpy

from modules.config import CREDENTIALS


def start_session() -> Zenpy:
    session = Zenpy(**CREDENTIALS)  # type: ignore
    if not session:
        raise SystemError("Zenpy Session not finded")
    return session


def request_api(url: str):
    response = requests.get(url, auth=(
        CREDENTIALS['email'], CREDENTIALS['password']))
    return response.json()


session = start_session()
