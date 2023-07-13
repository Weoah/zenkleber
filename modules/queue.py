from __future__ import annotations
from typing import List

from modules import session, request_api
from modules.slack import send_solved_message
from modules.config import SEARCH_TICKET
from modules.ticket import MLDTicket
from modules.dba import td

NEW_PERIOD = '10 MINUTES'
RESOLUTION_PERIOD = '1 HOUR'
PERIODIC_PERIOD = '30 MINUTES'


class MLDTicketQueue:

    def __init__(self) -> None:
        self.tickets: List[MLDTicket] = []

    def __repr__(self) -> str:
        return f'TicketQueue ({self.tickets})'

    def add_ticket(self, ticket: MLDTicket) -> None:
        if ticket not in self.tickets:
            self.tickets.append(ticket)

    async def get_tickets(self) -> None:
        self.tickets.clear()
        for ticket in session.search(**SEARCH_TICKET):  # type: ignore
            mld_ticket = MLDTicket(ticket, session)  # type: ignore
            self.add_ticket(mld_ticket)
            # break

    async def send_ticket(self, id: str, res: bool = False) -> None:
        ticket = [
            ticket for ticket in self.tickets
            if str(ticket.id_) == str(id)]
        if ticket:
            await ticket[0].send_metrics_message(res)

    async def check_new_sla(self) -> None:
        response = td.new_sla(NEW_PERIOD)
        for ticket in response:
            if ticket[2] is None or ticket[2] == 'None':
                await self.process_ticket(ticket[0], ticket[1])
                continue
            await self.update_unsolved_ticket(ticket[0])

    async def check_resolution_sla(self) -> None:
        response = td.resolution_sla(RESOLUTION_PERIOD)
        for ticket in response:
            if ticket[2] is None or ticket[2] == 'None':
                await self.process_ticket(ticket[0], ticket[1], True)
                continue
            await self.update_unsolved_ticket(ticket[0], True)

    async def check_periodic_sla(self) -> None:
        response = td.periodic_sla(PERIODIC_PERIOD)
        for ticket in response:
            if ticket[2] is None or ticket[2] == 'None':
                await self.process_ticket(ticket[0], ticket[1])
                continue
            await self.update_unsolved_ticket(ticket[0])

    async def process_ticket(self, ticket: str, send: int, res: bool = False):
        td.add_send(ticket)
        if res and send % 8 == 0:
            await self.send_ticket(ticket, res)
        if not res and send % 2 == 0:
            await self.send_ticket(ticket)

    async def update_new(self) -> None:
        response = td.new_sla_update(NEW_PERIOD)
        for ticket in response:
            await self.update_ticket(ticket[0])

    async def update_resolution(self) -> None:
        response = td.resolution_sla_update(RESOLUTION_PERIOD)
        for ticket in response:
            await self.update_ticket(ticket[0])

    async def update_periodic(self) -> None:
        response = td.periodic_sla_update(PERIODIC_PERIOD)
        for ticket in response:
            await self.update_ticket(ticket[0])

    async def update_ticket(self, id) -> None:
        ticket = [
            ticket for ticket in self.tickets
            if str(ticket.id_) == str(id)]
        if not ticket:
            return
        await ticket[0].edit_metrics_message()

    async def update_unsolved_ticket(self, id: str, res: bool = False) -> None:
        ticket = [
            ticket for ticket in self.tickets
            if str(ticket.id_) == str(id)]
        if not ticket:
            url = 'https://mundolivredigital.zendesk.com/api/v2/tickets/'
            request = request_api(f'{url}{id}')
            if request['ticket']['status'] == 'solved':
                send_solved_message(
                    request['ticket']['id'], request['ticket']['updated_at'])
            return
        await ticket[0].edit_unsolved_message(res)


ticket_queue = MLDTicketQueue()
