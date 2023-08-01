from __future__ import annotations
from typing import List

from src import zendesk_session, request_zendesk
from src.config import SEARCH_TICKET, BLOCKED_TICKETS, PERIODS
from src.db import db
from src.slack import slack
from src.ticket import MLDTicket


class MLDTicketQueue:

    def __init__(self) -> None:
        self.tickets: List[MLDTicket] = []

    def __repr__(self) -> str:
        return f'TicketQueue ({self.tickets})'

    def add_ticket(self, ticket: MLDTicket) -> None:
        if ticket not in self.tickets:
            self.tickets.append(ticket)

    def get_tickets(self):
        self.tickets.clear()
        for ticket in zendesk_session.search(**SEARCH_TICKET):
            if ticket.id in BLOCKED_TICKETS:
                continue
            self.add_ticket(MLDTicket(ticket, zendesk_session))

    def queue_first_message(self, id, wait=False) -> None:
        ticket = next(
            (ticket for ticket in self.tickets if ticket.id == int(id)), None)
        if ticket is not None:
            db.add_sended(id)
            ticket.ticket_send_message(wait)

    def queue_update_message(self, id, wait=False) -> None:
        ticket = next(
            (ticket for ticket in self.tickets if ticket.id == int(id)), None)
        if ticket is None:
            self.end_message(id)
        else:
            ticket.ticket_update_message(wait)

    def queue_edit_message(self, id) -> None:
        ticket = next(
            (ticket for ticket in self.tickets if ticket.id == int(id)), None)
        if ticket is None:
            self.end_message(id)
        else:
            ticket.ticket_edit_message()

    def status(self, id) -> tuple:
        request = request_zendesk(f'api/v2/tickets/{id}')
        return (request['status'], request['updated_at'])

    def end_message(self, id) -> None:
        status, updated = self.status(id)
        if status == 'solved':
            slack.send_end(id, updated, 'Resolvido')
        elif status == 'closed':
            slack.send_end(id, updated, 'Fechado')

    def new_tickets(self) -> None:
        tickets = db.check_new_ticket(PERIODS["NEW"])
        for ticket in tickets:
            id, send, message = ticket
            if message == 'None':
                self.queue_first_message(id, send)
            else:
                self.queue_update_message(id)

    def update_new_tickets(self) -> None:
        tickets = db.update_new_ticket(PERIODS["NEW"])
        for ticket in tickets:
            id = ticket[0]
            self.queue_edit_message(id)

    def wait_tickets(self) -> None:
        tickets = db.check_requester_wait(PERIODS["WAIT"])
        for ticket in tickets:
            id, send, message = ticket
            if message == 'None':
                self.queue_first_message(id, send)
            else:
                self.queue_update_message(id)

    def update_wait_tickets(self) -> None:
        tickets = db.update_requester_wait(PERIODS["WAIT"])
        for ticket in tickets:
            id = ticket[0]
            self.queue_edit_message(id)

    def periodic_tickets(self) -> None:
        tickets = db.check_periodic(PERIODS["PERIODIC"])
        for ticket in tickets:
            id, send, message = ticket
            if message == 'None':
                self.queue_first_message(id, send)
            else:
                self.queue_update_message(id)

    def update_periodic_tickets(self) -> None:
        tickets = db.update_periodic(PERIODS["PERIODIC"])
        for ticket in tickets:
            id = ticket[0]
            self.queue_edit_message(id)


queue = MLDTicketQueue()
