from datetime import datetime
from slack.web.client import WebClient

from modules.config import SLACK_TOKEN
from modules.dba import td


client = WebClient(token=SLACK_TOKEN)


def slack_send_message(chat: str, message: str, id: str | None = None):
    resp = client.chat_postMessage(channel=chat, text=message)
    if id is not None:
        td.add_message_data(id, resp['channel'], resp['ts'])  # type:ignore


def slack_edit_message(id: str | None, message: str) -> None:
    if id is None:
        return
    resp = td.get_message_data(id)
    if resp:
        client.chat_update(channel=resp[0][0], ts=resp[0][1], text=message)
        td.switch_edit(id, True)


def slack_edit_message_unsolved(id: str | None,
                                message: str,
                                chat: str,
                                res: bool = False) -> None:
    if id is None:
        return
    result = td.get_message_data(id)
    if result:
        check_to_send(id, chat, message, res)
        client.chat_update(channel=result[0][0], ts=result[0][1], text=message)
        return
    reopen = td.get_message_data_reopen(id)
    if reopen:
        td.switch_edit(id, False)
        slack_send_message(chat='#zenkleber', message=message, id=id)


def check_to_send(id: str, chat: str, message: str, res: bool = False) -> None:
    send = td.get_send_message(id, res)
    td.add_send_message(id)
    if send:
        if res and send[0][0] % 15 == 0:
            slack_send_message(chat=chat, message=message)
        if not res and send[0][0] % 3 == 0:
            slack_send_message(chat=chat, message=message)


def slack_send_solved_message(id: str, time: str) -> None:
    result = td.get_message_data(id)
    time_format = datetime.fromisoformat(time)
    timestamp = datetime.fromtimestamp(time_format.timestamp())
    new_time = timestamp.strftime("%H:%M - %d/%m")
    message = f'*Ticket #{id}* | _{new_time} #RESOLVIDO_ :catjam:'
    if result:
        client.chat_update(channel=result[0][0], ts=result[0][1], text=message)
