from datetime import datetime
from slack.web.client import WebClient

from modules.config import SLACK_TOKEN
from modules.dba import td


client = WebClient(token=SLACK_TOKEN)


def send_message(chat: str, message: str, id: str | None = None):
    result = client.chat_postMessage(channel=chat, text=message)
    if id is not None:
        td.add_chat(id, result['channel'], result['ts'])  # type: ignore


def edit_message(id: str | None, message: str) -> None:
    if id is None:
        return
    result = td.last_message(id)
    if result:
        client.chat_update(channel=result[0][0], ts=result[0][1], text=message)
        td.switch_edit(id, True)


def edit_message_unsolved(id: str | None,
                          message: str,
                          chat: str,
                          res: bool = False) -> None:
    if id is None:
        return
    result = td.last_message(id)
    if result:
        check_to_send(id, chat, message, res)
        client.chat_update(channel=result[0][0], ts=result[0][1], text=message)
        return
    reopen = td.reopen_message(id)
    if reopen:
        td.switch_edit(id, False)
        send_message(chat='#zenkleber', message=message, id=id)


def check_to_send(id: str, chat: str, message: str, res: bool = False) -> None:
    send = td.get_send(id, res)
    td.add_send(id)
    if send:
        if res and send[0][0] % 8 == 0:
            send_message(chat=chat, message=message)
        if not res and send[0][0] % 2 == 0:
            send_message(chat=chat, message=message)


def send_solved_message(id: str, time: str) -> None:
    result = td.last_message(id)
    time_format = datetime.fromisoformat(time)
    timestamp = datetime.fromtimestamp(time_format.timestamp())
    new_time = timestamp.strftime("%H:%M - %d/%m")
    message = f'*Ticket #{id}* | _{new_time} #RESOLVIDO_ :catjam:'
    if result:
        client.chat_update(channel=result[0][0], ts=result[0][1], text=message)
