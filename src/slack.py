from slack_bolt import App
from slack_sdk.errors import SlackApiError
from os import environ as env

from src import template, db


TOKEN = env['SLACK_TOKEN']
SECRET = env['SLACK_SECRET']
CHANNEL = env['SLACK_CHANNEL']

client = App(token=TOKEN, signing_secret=SECRET).client


def control_message(ticket, metrics):
    send_private(ticket, metrics)
    if not db.get_ticket(ticket.id):
        send_message(ticket, metrics)
    else:
        update_message(ticket, metrics)


def send_message(ticket, metrics):
    try:
        message = client.chat_postMessage(
            channel=CHANNEL,
            text='Atualização periódica:',
            blocks=template.send_periodic(ticket, metrics)
        )
        db.add_message(ticket, message)
    except SlackApiError as error:
        print(f'Error on sending update message: {error}')


def send_private(ticket, metrics):
    try:
        client.chat_postMessage(
            channel=template.mention(ticket),
            text='Atualização periódica:',
            blocks=template.send_periodic(ticket, metrics)
        )
    except SlackApiError as error:
        print(f'Error on sending update message: {error}')


def update_message(ticket, metrics):
    try:
        message = db.get_ticket(ticket.id)[0]
        client.chat_update(
            channel=message['chat'],
            ts=message['ts'],
            text='Atualização periódica:',
            blocks=template.send_periodic(ticket, metrics)
        )
    except SlackApiError as error:
        print(f'Error on sending update message: {error}')


def solve_message(ticket):
    try:
        client.chat_update(
            channel=ticket['chat'],
            ts=ticket['ts'],
            text='Ticket atualizado:',
            blocks=template.solved_periodic(ticket)
        )
        db.solved_ticket(ticket['ticket'])
    except SlackApiError as error:
        print(f'Error on sending update message: {error}')


def close_message(ticket):
    try:
        client.chat_update(
            channel=ticket['chat'],
            ts=ticket['ts'],
            text='Ticket solucionado:',
            blocks=template.ticket_closed(ticket)
        )
        db.delete_ticket(ticket['ticket'])
    except SlackApiError as error:
        print(f'Error on sending update message: {error}')


def new_message(ticket):
    if db.get_ticket(ticket.id):
        return
    try:
        message = client.chat_postMessage(
            channel=CHANNEL,
            text='Novo ticket:',
            blocks=template.new_ticket(ticket)
        )
        db.add_message(ticket, message)
    except SlackApiError as error:
        print(f'Error on sending update message: {error}')
