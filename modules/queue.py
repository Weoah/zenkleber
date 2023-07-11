from __future__ import annotations
from typing import List

from modules import session
from modules.config import SEARCH_TICKET
from modules.ticket import MLDTicket
from modules.dba import td


class MLDTicketQueue:

    def __init__(self) -> None:
        self.tickets: List[MLDTicket] = []
        # self.get_tickets()

    def add_ticket(self, ticket: MLDTicket) -> None:
        if ticket not in self.tickets:
            self.tickets.append(ticket)

    def get_tickets(self) -> None:
        self.tickets.clear()
        for ticket in session.search(**SEARCH_TICKET):  # type: ignore
            mld_ticket = MLDTicket(ticket, session)  # type: ignore
            self.add_ticket(mld_ticket)
            # break

    def send_one_ticket(self, id) -> None:
        ticket = [ticket for ticket in self.tickets if str(ticket.id) == id]
        if ticket:
            ticket[0].send_metrics_message()
            ...

    def check_tickets_sla(self) -> None:
        first_check = td.get_sla('30 minutes', '1 hour')
        if first_check is not None:
            for ticket_id in first_check:
                self.send_one_ticket(ticket_id[0])

    def check_tickets_new(self):
        first_check = td.get_new('20 minutes')
        if first_check is not None:
            for ticket_id in first_check:
                self.send_one_ticket(ticket_id[0])


ticket_queue = MLDTicketQueue()
