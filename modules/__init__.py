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


def show_message(func):
    def decorator(*args, **kwargs):
        print('\nExecutando:', func.__name__)
        try:
            print('\n', *args, **kwargs)
        except TypeError:
            ...
        result = func(*args, **kwargs)
        print('\nConcluída:', func.__name__)
        return result
    return decorator


session = start_session()
