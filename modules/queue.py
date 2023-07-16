from __future__ import annotations
from typing import List

from modules.config import SEARCH_TICKET
from modules import session, request_zendesk_api
from modules.slack import slack_send_solved_message
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
            if ticket.id == 4937:  # type: ignore
                continue
            mld_ticket = MLDTicket(ticket, session)  # type: ignore
            self.add_ticket(mld_ticket)

    async def get_new_tickets(self) -> None:
        response = td.verify_new_tickets(NEW_PERIOD)
        if not response:
            return
        for ticket in response:
            if ticket[2] is None or ticket[2] == 'None':
                await self.ticket_interval(ticket[0], ticket[1])
                continue
            await self.update_unsolved_ticket_message(ticket[0])

    async def update_new_tickets(self) -> None:
        response = td.verify_new_ticket_update(NEW_PERIOD)
        if not response:
            return
        for ticket in response:
            await self.update_ticket_message(ticket[0])

    async def get_resolution_metric_tickets(self) -> None:
        response = td.verify_metric_resolution(RESOLUTION_PERIOD)
        if not response:
            return
        for ticket in response:
            if ticket[2] is None or ticket[2] == 'None':
                await self.ticket_interval(ticket[0], ticket[1], True)
                continue
            await self.update_unsolved_ticket_message(ticket[0], True)

    async def update_resolution_metric_tickets(self) -> None:
        response = td.verify_metric_resolution_update(RESOLUTION_PERIOD)
        if not response:
            return
        for ticket in response:
            await self.update_ticket_message(ticket[0])

    async def get_periodic_metric_tickets(self) -> None:
        response = td.verify_metric_periodic(PERIODIC_PERIOD)
        if not response:
            return
        for ticket in response:
            if ticket[2] is None or ticket[2] == 'None':
                await self.ticket_interval(ticket[0], ticket[1])
                continue
            await self.update_unsolved_ticket_message(ticket[0])

    async def update_periodic_metric_tickets(self) -> None:
        response = td.verify_metric_periodic_update(PERIODIC_PERIOD)
        if not response:
            return
        for ticket in response:
            await self.update_ticket_message(ticket[0])

    async def ticket_interval(self, ticket: str, send: int, res: bool = False):
        td.add_send_message(ticket)
        if res and send % 15 == 0:
            await self.send_ticket_message(ticket, res)
        if not res and send % 3 == 0:
            await self.send_ticket_message(ticket)

    async def send_ticket_message(self, id: str, res: bool = False) -> None:
        ticket = [
            ticket for ticket in self.tickets
            if str(ticket.id_) == str(id)]
        if ticket:
            await ticket[0].send_metrics_message(res)

    async def update_ticket_message(self, id) -> None:
        ticket = [
            ticket for ticket in self.tickets
            if str(ticket.id_) == str(id)]
        if not ticket:
            return
        await ticket[0].edit_metrics_message()

    async def update_unsolved_ticket_message(self,
                                             id: str,
                                             res: bool = False) -> None:
        ticket = [
            ticket for ticket in self.tickets
            if str(ticket.id_) == str(id)]
        if not ticket:
            await self.send_solved_message(str(id))
            return
        await ticket[0].edit_unsolved_message(res)

    async def send_solved_message(self, id: str) -> None:
        url = 'https://mundolivredigital.zendesk.com/api/v2/tickets/'
        request = request_zendesk_api(f'{url}{id}')
        if request['ticket']['status'] == 'solved':
            slack_send_solved_message(
                request['ticket']['id'], request['ticket']['updated_at'])


ticket_queue = MLDTicketQueue()
