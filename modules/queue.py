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

    async def send_ticket(self, id: str, resolution: bool = False) -> None:
        ticket = [
            ticket for ticket in self.tickets
            if str(ticket.id) == str(id)]
        print('send ticket alcançado')
        print(ticket)
        if ticket:
            ticket[0].send_metrics_message(resolution)

    async def check_new_sla(self) -> None:
        response = td.new_sla('10 minutes')
        for ticket in response:
            await self.process_ticket(ticket[0], ticket[1])

    async def check_resolution_sla(self) -> None:
        response = td.resolution_sla('1 hour')
        for ticket in response:
            await self.process_ticket(ticket[0], ticket[1], True)

    async def check_periodic_sla(self) -> None:
        response = td.periodic_sla('30 minutes')
        for ticket in response:
            await self.process_ticket(ticket[0], ticket[1])

    async def process_ticket(self, ticket: str, send: int, res: bool = False):
        td.add_send(ticket)
        if send % 2 == 0:
            await self.send_ticket(ticket, res)


ticket_queue = MLDTicketQueue()
