from slack.web.client import WebClient

from modules.config import SLACK_TOKEN
from modules.dba import td


client = WebClient(token=SLACK_TOKEN)


def send_message(chat: str, message: str, id: str | None = None):
    result = client.chat_postMessage(channel=chat, text=message)
    if id is not None \
            and result is not None:
        td.add_chat(id, result['channel'], result['ts'])  # type: ignore


def edit_message(id: str | None, message: str):
    if id is None:
        return
    result = td.last_message(id)
    if result:
        client.chat_update(channel=result[0][0], ts=result[0][1], text=message)
        td.edit_message(id)
    return
