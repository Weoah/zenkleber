from datetime import datetime
from pytz import timezone

from os import environ as env

url = f"{env['ZENDESK_URL']}agent/tickets/"

assignees = {}


def mention(ticket):
    if not ticket.assignee:
        return ''
    if ticket.assignee.name in assignees.keys():
        return assignees.get(ticket.assignee.name)
    return "!here"


def br_time(iso_time):
    return datetime.fromtimestamp(
        datetime.fromisoformat(iso_time).timestamp(),
        tz=timezone('America/Sao_Paulo')).strftime("%H:%M - %d/%m")


def send_periodic(ticket, metrics):
    return [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Atualização Periódica*:\n*<{url}{ticket.id}|Ticket #{ticket.id}>*"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Expira em:*\n{metrics['periodic']}"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                    "type": "mrkdwn",
                    "text": f"*Responsável*:\n_{ticket.assignee.name}_ :pride: <{mention(ticket)}>"
            }
        },
        {
            "type": "section",
            "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Prioridade:*\n{ticket.priority.capitalize()}"
                    },
                {
                        "type": "mrkdwn",
                        "text": f"*Solicitante:*\n{ticket.requester.name}"
                },
                {
                        "type": "mrkdwn",
                        "text": f"*Criado:*\n{br_time(ticket.created_at)}"
                },
                {
                        "type": "mrkdwn",
                        "text": f"*Atualizado:*\n{br_time(ticket.updated_at)}"
                },
                {
                        "type": "mrkdwn",
                        "text": f"*Assunto:*\n{ticket.subject}"
                }
            ]
        },
    ]


def solved_periodic(ticket):
    return [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Atualizado*:\n*<{url}{ticket['ticket']}|Ticket #{ticket['ticket']}>* :white_check_mark:"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Em*:\n_{ticket['updated_at']}_"
                }
            ]
        }
    ]


def ticket_closed(ticket):
    return [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Solucionado*:\n*<{url}{ticket['ticket']}|Ticket #{ticket['ticket']}>* :white_check_mark:"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Em*:\n_{ticket['updated_at']}_"
                }
            ]
        }
    ]


def new_ticket(ticket):
    return [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Novo ticket*:\n*<{url}{ticket.id}|Ticket #{ticket.id}>*"
                }
            ]
        },
        {
            "type": "section",
            "text": {
                    "type": "mrkdwn",
                    "text": "*Responsável*:\n_Ninguém_ :pride: <@acarvalho>"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Solicitante:*\n{ticket.requester.name}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Criado:*\n{br_time(ticket.created_at)}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Atualizado:*\n{br_time(ticket.updated_at)}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Assunto:*\n{ticket.subject}"
                }
            ]
        },
    ]
