from slack.web.client import WebClient

from modules.config import SLACK_TOKEN


client = WebClient(token=SLACK_TOKEN)


def send_message(chat: str, message: str):
    client.chat_postMessage(channel=chat, text=message)
