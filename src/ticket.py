from __future__ import annotations
from datetime import datetime
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket

from src import request_zendesk, log
from src.config import COLLABORATORS, ZENDESK_DOMAIN, SLACK_OPEN_CHANNEL
from src.db import db
from src.slack import slack


class IMLDTicket:

    def __init__(self, ticket: Ticket, zendesk_session: Zenpy) -> None:
        self.zendesk_session = zendesk_session
        self.ticket = ticket

    @property
    def id(self):
        if self.ticket.id:
            return self.ticket.id

    @property
    def status(self):
        if self.ticket.status:
            return self.ticket.status.capitalize()

    @property
    def assignee(self):
        if self.ticket.assignee:
            return self.ticket.assignee.name
        return 'Ninguém'

    @property
    def requester(self):
        if self.ticket.requester:
            return self.ticket.requester.name

    @property
    def created_at(self):
        if self.ticket.created:
            return datetime.fromtimestamp(self.ticket.created.timestamp())

    @property
    def subject(self):
        if self.ticket.subject:
            return self.ticket.subject

    @property
    def tags(self):
        if self.ticket.tags:
            return list(self.ticket.tags)

    @property
    def priority(self):
        if self.ticket.priority:
            return self.ticket.priority

    @property
    def comments(self):
        if self.zendesk_session:
            return list(self.zendesk_session.tickets.comments(self.id))

    def _public_comment(self):
        if self.comments:
            count = 1
            comment = self.comments[-1]
            while not comment.public:
                count += 1
                comment = self.comments[-count]
            return comment

    @property
    def updated_at(self):
        comm = self._public_comment()
        return datetime.fromtimestamp(comm.created.timestamp())

    @property
    def updated_by(self):
        comm = self._public_comment()
        return comm.author.name

    @property
    def last_comment(self):
        comm = self._public_comment()
        return comm.body[:300]

    def __repr__(self) -> str:
        return f'MLDTicket(#{self.id})'


class TicketSLA(IMLDTicket):

    def __init__(self, ticket: Ticket, zendesk_session: Zenpy) -> None:
        super().__init__(ticket, zendesk_session)

        self.requester_wait_time: datetime | str = 'Sem SLA!'
        self.periodic_update_time: datetime | str = 'Sem SLA!'
        self.add_metrics()

        self.requester_wait_time_metric = self._requester_wait_time_metric()
        self.periodic_update_time_metric = self._periodic_update_time_metric()

        self._manage_ticket()

    def metrics(self):
        url = f'api/v2/tickets/{self.id}?include=slas'
        response = request_zendesk(url)
        if response:
            return response['slas']['policy_metrics']
        raise ValueError('Not possible to access Zendesk API')

    def add_metrics(self):
        for metric in self.metrics():
            status = metric['stage']
            time_f = metric['breach_at']
            if metric['metric'] == 'requester_wait_time':
                self.requester_wait_time = self._requester_wait_time(
                    status, time_f)
            if metric['metric'] == 'periodic_update_time':
                self.periodic_update_time = self._periodic_update_time(time_f)

    def _requester_wait_time(self, status: str, time_f: str):
        if status == 'paused':
            return 'Pausado!'
        if isinstance(time_f, str):
            time = datetime.fromisoformat(time_f)
            violated = time.timestamp() - datetime.now().timestamp()
            if violated:
                return 'SLA Violado!'
            return datetime.fromtimestamp(time.timestamp())

    def _periodic_update_time(self, time_f: str):
        if isinstance(time_f, str):
            time = datetime.fromisoformat(time_f)
            return datetime.fromtimestamp(time.timestamp())

    def _requester_wait_time_metric(self) -> str:
        if isinstance(self.requester_wait_time, datetime):
            time_left = abs(self.requester_wait_time - datetime.now())
            return str(time_left).split('.')[0]
        return 'Sem SLA!'

    def _periodic_update_time_metric(self) -> str:
        if isinstance(self.periodic_update_time, datetime):
            time_left = abs(self.periodic_update_time - datetime.now())
            violated = (self.periodic_update_time.timestamp() -
                        datetime.now().timestamp())
            if violated <= 0:
                return 'SLA Violado!'
            return str(time_left).split('.')[0]
        return 'Sem SLA!'

    def _manage_ticket(self):
        check = db.check_ticket(self.id)
        self._store() if not check else self._update()

    def _store(self):
        db.store_ticket(self.id, self.status, self.created_at,
                        self.periodic_update_time, self.requester_wait_time)

    def _update(self):
        db.update_ticket(self.id, self.status, self.created_at,
                         self.periodic_update_time, self.requester_wait_time)


class MLDTicket(TicketSLA):

    def __init__(self, ticket: Ticket, zendesk_session: Zenpy) -> None:
        super().__init__(ticket, zendesk_session)

        self.updated = self.updated_at.strftime("%H:%M - %d/%m")

    def mention(self):
        if self.assignee in COLLABORATORS.keys():
            return COLLABORATORS.get(self.assignee)

    def remention(self):
        if self.updated_by in COLLABORATORS.keys():
            return COLLABORATORS.get(self.updated_by)

    def chat(self):
        if self.mention() is None:
            return self.remention()
        return self.mention()

    def wait_expire(self):
        message = self.requester_wait_time_metric
        if not isinstance(self.requester_wait_time, str):
            expire = self.requester_wait_time.strftime("%H:%M - %d/%m")
            expire_sep = self.requester_wait_time_metric.split(':')
            expires = expire_sep[0]
            if len(expire_sep) == 3:
                expires = f'{expire_sep[0]} Horas e {expire_sep[1]} Minutos'
            message = f'{expires} ({expire})'
        return message

    def periodic_expire(self):
        message = self.periodic_update_time_metric
        if not isinstance(self.periodic_update_time, str):
            expire = self.periodic_update_time.strftime("%H:%M - %d/%m")
            expire_sep = self.periodic_update_time_metric.split(':')
            expires = expire_sep[0]
            if len(expire_sep) == 3:
                expires = f'{expire_sep[0]} Horas e {expire_sep[1]} Minutos'
            message = f'{expires} ({expire})'
        return message

    def ticket_message(self):
        last_comment = f'_{self.updated_by}_\n\n{self.last_comment}'
        message = (
            f'*Ticket ID:* _#{self.id}_\n'
            f'*Status:* _{self.status}_\n'
            f'*Atribuído a:* _{self.assignee}_ :pride: <{self.chat()}>\n\n'
            f'*Ultima Atualização:* _{self.updated}_\n'
            f'*SLA Resolução Expira em:* _{self.wait_expire()}_\n'
            f'*SLA Atualização Expira em:* _{self.periodic_expire()}_\n\n'
            f'*Assunto:* _{self.subject}_\n'
            f'*Solicitante:* _{self.requester}_\n'
            f'*Ultimo comentário de:* {last_comment}\n\n\n'
            f'*Acesse em:* {ZENDESK_DOMAIN}/agent/tickets/{self.id}\n'
            f'*-------------------------------------------------------------*')
        log.info(f'sending message to {self.chat()}\n{message[:400]}\n')
        return message

    def update_message(self):
        update = f'_{self.updated} atualizado por {self.updated_by}_'
        message = f'*Ticket #{self.id}* | {update} :white_check_mark:'
        log.info(f'editing message {message}\n')
        return message

    def ticket_send_message(self, wait: bool):
        if isinstance(self.requester_wait_time, str) and wait:
            return
        chat = self.chat()
        message = self.ticket_message()
        slack.send_message(SLACK_OPEN_CHANNEL, message, self.id)
        if chat is not None:
            slack.send_message(chat, message, None)

    def ticket_update_message(self, wait: bool) -> None:
        chat = self.chat()
        if chat is None:
            return
        message = self.ticket_message()
        slack.update_message(self.id, chat, message, wait)

    def ticket_edit_message(self):
        if self.updated_by not in COLLABORATORS.keys():
            return
        slack.edit_message(self.id, self.update_message())
