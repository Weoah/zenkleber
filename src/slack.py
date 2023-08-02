from datetime import datetime as dt
from slack.web.client import WebClient
from slack.errors import SlackApiError

from src import log
from src.config import SLACK_TOKEN, SLACK_OPEN_CHANNEL
from src.db import db


class SlackClient:

    def __init__(self):
        self.client = WebClient(token=SLACK_TOKEN)

    def brt_time(self, time_f):
        time = dt.fromtimestamp(dt.fromisoformat(time_f).timestamp())
        return time.strftime("%H:%M - %d/%m")

    def intervals(self, id, chat, message, res):
        send = db.get_message_sended(id)[0][0]
        db.add_sended(id)
        if res and send % 15 == 0:
            self.send_message(chat, message)
        elif not res and send % 3 == 0:
            self.send_message(chat, message)

    def send_message(self, chat, message, id=None) -> None:
        try:
            data = self.client.chat_postMessage(channel=chat, text=message)
            if id is not None:
                db.add_message(id, data['channel'], data['ts'])
        except SlackApiError as error:
            log.info(f'Erro no client do Slack: {error}')

    def update_message(self, id, chat, message, res=False) -> None:
        data = db.get_message(id)
        if data:
            channel, ts = data[0]
            self.intervals(id, chat, message, res)
            try:
                self.client.chat_update(channel=channel, ts=ts, text=message)
            except SlackApiError as error:
                log.info(f'Erro no client do Slack: {error}')
        self.reopen_message(id, message)

    def edit_message(self, id, message) -> None:
        if id is None:
            return
        data = db.get_message(id)
        if data:
            chat, ts = data[0]
            try:
                self.client.chat_update(channel=chat, ts=ts, text=message)
                db.edit_message(id)
            except SlackApiError as error:
                log.info(f'Erro no client do Slack: {error}')

    def reopen_message(self, id, message):
        data = db.get_message_reopen(id)
        if data:
            db.unedit_message(id)
            self.send_message(SLACK_OPEN_CHANNEL, message, id)

    def send_end(self, id, updated, status) -> None:
        data = db.get_message(id)
        if not data:
            return
        chat, timestamp = data[0]
        time = self.brt_time(updated)
        message = f'*Ticket #{id}* | _{time} #{status}_ :catjam:'
        try:
            self.client.chat_update(channel=chat, ts=timestamp, text=message)
        except SlackApiError as error:
            log.info(f'Erro no client do Slack: {error}')


slack = SlackClient()
