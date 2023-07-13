from __future__ import annotations
from datetime import datetime
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User

from modules import request_api
from modules.slack import send_message, edit_message, edit_message_unsolved
from modules.logger import logger
from modules.dba import td


class MLDTicket:

    def __init__(self, ticket: Ticket, session: Zenpy) -> None:
        self.session = session
        self.assigned: User = ticket.assignee  # type:ignore

        # Ticket ID
        self.id_ = ticket.id

        # Ticket URL
        self.url = 'https://mundolivredigital.zendesk.com'

        # Ticket creation date
        self.created_at = datetime.fromtimestamp(
            ticket.created.timestamp())  # type:ignore

        # Ticket status
        self.status = ticket.status.capitalize()  # type:ignore

        # Ticket subject
        self.subject = ticket.subject

        # Selected tags for ticket
        self.tags = list(ticket.tags)  # type:ignore

        # Ticket priority
        self.priority = ticket.priority

        # Ticket SLA policy
        self.policy = self.__sla_policy()

        # Last ticket response
        self.updated_at: datetime
        self.last_comment = self.__get_last_comment()
        self.updated_by: str

        # Time to expire first response
        self.expires_first: datetime | None = None
        self.sla_first: str = 'Resolvido!'

        # Time to expire resolution
        self.sla_resolution: str = 'Sem SLA'
        self.requester_wait: str | datetime = 'Sem SLA'

        # Time to expire periodic update
        self.periodic_update: str | datetime = 'Sem SLA'
        self.sla_periodic: str = 'Sem SLA'

        self.__get_metrics()
        self.__sla_first_expires()
        self.__sla_resolution_expires()
        self.__sla_periodic_expires()

        # Assigned user to ticket
        self.assigned_to = 'Ninguém'
        if self.assigned:
            self.assigned_to = self.assigned.name

        # Ticket requester
        self.requester = ticket.requester.name  # type:ignore

        self._verify_ticket()
        # self.send_metrics_message()

    def __repr__(self) -> str:
        return f'MLDTicket(#{self.id_})'

    async def send_metrics_message(self, resolution=False) -> None:
        if isinstance(self.requester_wait, str) \
                and resolution:
            return
        chat = self._chat_message()
        message = self.__generate_message()
        logger.info(f'Enviando mensagem para {chat}\n{message}')
        send_message('#zenkleber', message, self.id_)
        send_message(chat, message)

    async def edit_unsolved_message(self, res: bool = False):
        chat = self._chat_message()
        message = self.__generate_message()
        edit_message_unsolved(self.id_, message, chat, res)
        logger.info(f'Enviando mensagem unsolved para {chat}\n{message}')

    async def edit_metrics_message(self):
        message = self.__update_message()
        edit_message(self.id_, message)
        logger.info(f'Editando a mensagem - {message}')

    def __generate_message(self) -> str:
        updated_at = self.updated_at.strftime("%H:%M - %d/%m")
        mention = self._chat_mention()
        message = (
            f'*Ticket ID:* _#{self.id_}_\n'
            f'*Status:* _{self.status}_\n'
            f'*Atribuído a:* _{self.assigned_to}_ :pride: <{mention}>\n\n'
            f'*Ultima Atualização:* _{updated_at}_\n'
            f'*SLA 1º Resposta Expira em:* _{self.__first_expire()}_\n'
            f'*SLA Resolução Expira em:* _{self.__resolut_expire()}_\n'
            f'*SLA Atualização Expira em:* _{self.__periodic_expire()}_\n\n'
            f'*Assunto:* _{self.subject}_\n'
            f'*Solicitante:* _{self.requester}_\n'
            f'*Ultimo comentário de:* {self.last_comment}\n\n\n'
            f'*Acesse em:* {self.url}/agent/tickets/{self.id_}\n'
            f'*-------------------------------------------------------------*')
        return message

    def __update_message(self) -> str:
        self.__get_last_comment(update=True)
        updated_at = self.updated_at.strftime("%H:%M - %d/%m")
        update = f'_{updated_at} atualizado por {self.updated_by}_'
        message = f'*Ticket #{self.id_}* | {update} :white_check_mark:'
        return message

    def _chat_mention(self) -> str:
        mention = self._chat_message()
        if self.assigned_to == 'Ninguém':
            mention = '@acarvalho'
        return mention

    def _chat_message(self) -> str:
        # return '@jcristofaro'
        match self.assigned_to:
            case 'Flávio Fraga':
                return '@ffraga'
            case 'Gabriel Lunardelli':
                return '@glunardelli'
            case 'Iuri de Oliveira':
                return '@ioliveira'
            case 'Jean Cristofaro':
                return '@jcristofaro'
            case 'João Francisco Fernandes Gazzara':
                return '@jgazzara'
            case 'Jonathan Vicentini':
                return '@jvicentini'
            case 'Marcelo Reballo':
                return '@mreballo'
            case 'Renan Medeiros':
                return '@rmedeiros'
            case 'Luis Paulo de Oliveira Ferreira':
                return self.__chat_message_comment()
            case 'Gabriel Martins':
                return self.__chat_message_comment()
            case 'Ninguém':
                return '@acarvalho'
            case _:
                return '#zenkleber'

    def __chat_message_comment(self):
        match self.updated_by:
            case 'Flávio Fraga':
                return '@ffraga'
            case 'Gabriel Lunardelli':
                return '@glunardelli'
            case 'Iuri de Oliveira':
                return '@ioliveira'
            case 'Jean Cristofaro':
                return '@jcristofaro'
            case 'João Francisco Fernandes Gazzara':
                return '@jgazzara'
            case 'Jonathan Vicentini':
                return '@jvicentini'
            case 'Marcelo Reballo':
                return '@mreballo'
            case 'Renan Medeiros':
                return '@rmedeiros'
            case _:
                return '#zenkleber'

    def _verify_ticket(self) -> None:
        verify = td.verify_ticket(self.id_)
        if not verify:
            self._store_ticket()
        else:
            self._update_ticket()

    def _store_ticket(self) -> None:
        td.store_ticket(
            id=self.id_, status=self.status, designee=self.assigned_to,
            policy=self.policy, created_at=self.created_at,
            periodic_expires=self.periodic_update,
            resolution_expires=self.requester_wait)

    def _update_ticket(self) -> None:
        td.update_ticket(
            id=self.id_, status=self.status, designee=self.assigned_to,
            policy=self.policy, created_at=self.created_at,
            periodic_expires=self.periodic_update,
            resolution_expires=self.requester_wait)

    def __first_expire(self) -> str:
        expire_msg = 'Resolvido!'
        if self.expires_first is not None:
            sla_expire = self.expires_first.strftime("%H:%M - %d/%m")
            exp_split = self.sla_first.split(':')
            expires_in = exp_split[0]
            if len(exp_split) == 3:
                expires_in = f'{exp_split[0]} Horas e {exp_split[1]} Minutos'
            expire_msg = f'{expires_in} ({sla_expire})'
        return expire_msg

    def __resolut_expire(self) -> str:
        if not isinstance(self.requester_wait, str):
            sla_expire = self.requester_wait.strftime("%H:%M - %d/%m")
            exp_split = self.sla_resolution.split(':')
            expires_in = exp_split[0]
            if len(exp_split) == 3:
                expires_in = f'{exp_split[0]} Horas e {exp_split[1]} Minutos'
            expire_msg = f'{expires_in} ({sla_expire})'
        else:
            expire_msg = self.requester_wait
        return expire_msg

    def __periodic_expire(self) -> str:
        if self.policy == 'nenhuma':
            ...
        if not isinstance(self.periodic_update, str):
            sla_expire = self.periodic_update.strftime("%H:%M - %d/%m")
            exp_split = self.sla_periodic.split(':')
            expires_in = exp_split[0]
            if len(exp_split) == 3:
                expires_in = f'{exp_split[0]} Horas e {exp_split[1]} Minutos'
            expire_msg = f'{expires_in} ({sla_expire})'
        else:
            expire_msg = self.periodic_update
        return expire_msg

    def __get_last_comment(self, update: bool = False) -> str | None:
        comments = self.session.tickets.comments(self.id_)  # type:ignore
        count = 2
        comments_len = len(comments) - 1
        comment = comments[comments_len:][0]  # type:ignore
        while not comment.public:
            comments = self.session.tickets.comments(self.id_)  # type:ignore
            comments_len = len(comments) - count
            comment = comments[comments_len:][0]  # type:ignore
            count += 1
        self.updated_at = datetime.fromtimestamp(comment.created.timestamp())
        if update:
            return None
        self.updated_by = comment.author.name
        return f'_{comment.author.name}_\n\n{comment.body[:300]}'

    def __sla_policy(self) -> str:
        policy_tags = (
            'nacsp', 'nachomeoffice', 'nacrj', 'nacregionais',
            'dasahospitais', 'oicorreios', 'preventsenior',
            'somente', 'basf', 'tarefainterna', 'nac_-_home_office')
        result = [i for i in policy_tags if i in self.tags]
        if result:
            return result[0]
        return 'nenhuma'

    def __get_metrics(self):
        url = f'{self.url}/api/v2/tickets/{self.id_}?include=slas'
        response = request_api(url)
        for policy in response['ticket']['slas']['policy_metrics']:
            if hasattr(self, f"_{policy['metric']}"):
                run = getattr(self, f"_{policy['metric']}")
                run(policy['stage'], policy['breach_at'])

    def _periodic_update_time(self, status, time):
        if status != 'paused' \
                and isinstance(time, str):
            time_format = datetime.fromisoformat(time)
            self.periodic_update = datetime.fromtimestamp(
                time_format.timestamp())

    def _requester_wait_time(self, status, time):
        if status == 'paused':
            self.requester_wait = 'Pausado!'
            return
        if isinstance(time, str):
            time_format = datetime.fromisoformat(time)
            neg = time_format.timestamp() - datetime.now().timestamp()
            if neg <= 0:
                self.sla_resolution = 'SLA Violado!'
            else:
                self.requester_wait = datetime.fromtimestamp(
                    time_format.timestamp())

    def __sla_first_expires(self) -> None:
        if self.created_at is not None \
                and self.expires_first is not None:
            time_now = abs(self.expires_first - datetime.now())
            self.sla_first = str(time_now).split('.')[0]

    def __sla_resolution_expires(self) -> None:
        if not isinstance(self.requester_wait, str):
            time_now = abs(self.requester_wait - datetime.now())
            self.sla_resolution = str(time_now).split('.')[0]

    def __sla_periodic_expires(self) -> None:
        if not isinstance(self.periodic_update, str):
            time_now = abs(self.periodic_update - datetime.now())
            neg = self.periodic_update.timestamp() - datetime.now().timestamp()
            self.sla_periodic = str(time_now).split('.')[0]
            if neg <= 0:
                self.sla_periodic = 'SLA Violado!'
