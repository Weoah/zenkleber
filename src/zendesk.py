from zenpy import Zenpy  # type: ignore
from datetime import datetime, timedelta
from pytz import timezone

from os import environ as env
from src import slack, db


class ZendeskI:
    def __init__(self) -> None:
        creds = {
            'email': env['ZENDESK_EMAIL'],
            'password': env['ZENDESK_PASSWORD'],
            'subdomain': env['ZENDESK_DOMAIN']
        }

        self.client = Zenpy(**creds)
        self.client.disable_caching()

    def br_time(self, iso_time):
        return datetime.fromtimestamp(
            datetime.fromisoformat(iso_time).timestamp(),
            tz=timezone('America/Sao_Paulo'))

    def ticket_slas(self, ticket_id):
        ticket = self.client.tickets(id=ticket_id, include=['slas'])
        if ticket.slas['policy_metrics']:
            db.add_updated(ticket.id, self.br_time(
                ticket.updated_at).strftime("%H:%M - %d/%m"))
            return ticket.slas['policy_metrics']


class ZendeskSearch(ZendeskI):
    search_ticket = {
        "type": 'ticket',
        "status": ["new", "open", "pending", "hold"]
    }

    def lasts_40_minutes(self, time):
        now = datetime.now(tz=timezone('America/Sao_Paulo'))
        difference = time - now
        return difference < timedelta(minutes=40)

    def search_tickets(self):
        return [ticket for ticket in self.client.search(**self.search_ticket)]

    def breaching_sla(self, metrics):
        for metric in metrics:
            if metric['metric'] == ['first_reply_time']:
                continue
            if metric['stage'] == 'active':
                breach_at = self.br_time(metric['breach_at'])
                return self.lasts_40_minutes(breach_at)

    def metrics_values(self, policies):
        response = {'periodic': 'Sem SLA', 'wait': 'Sem SLA'}
        for metric in policies:
            if 'periodic_update_time' in metric.values() \
                    and 'minutes' in metric:
                response['periodic'] = f"{metric['minutes']} Minutos"
            if 'requester_wait_time' in metric.values() \
                    and 'minutes' in metric:
                response['wait'] = f"{metric['minutes']} Minutos"
        return response

    def main(self):
        for ticket in self.search_tickets():
            metrics = self.ticket_slas(ticket.id)
            if not metrics:
                continue
            if self.breaching_sla(metrics):
                slack.control_message(ticket, self.metrics_values(metrics))


search = ZendeskSearch()


class ZendeskUpdate(ZendeskI):
    def lasts_more_than_40_minutes(self, time):
        now = datetime.now(tz=timezone('America/Sao_Paulo'))
        difference = time - now
        return difference > timedelta(minutes=40)

    def breaching_sla(self, metrics):
        for metric in metrics:
            if metric['metric'] == ['first_reply_time']:
                continue
            if metric['stage'] == 'active':
                breach_at = self.br_time(metric['breach_at'])
                return self.lasts_more_than_40_minutes(breach_at)

    def main(self):
        for ticket in db.get_message():
            metrics = self.ticket_slas(ticket['ticket'])
            if not metrics:
                continue
            if self.breaching_sla(metrics):
                slack.solve_message(ticket)


update = ZendeskUpdate()


class ZendeskClose(ZendeskI):
    def check_status(self, ticket_id):
        return self.client.tickets(id=ticket_id).status

    def main(self):
        for ticket in db.get_message():
            status = self.check_status(ticket['ticket'])
            if status == 'solved' or status == 'closed':
                slack.close_message(ticket)


close = ZendeskClose()


class ZendeskNew(ZendeskI):
    search_ticket = {
        "type": 'ticket',
        "status": ["new"]
    }

    def main(self):
        tickets = self.client.search(**self.search_ticket)
        for ticket in tickets:
            slack.new_message(ticket)


new = ZendeskNew()
