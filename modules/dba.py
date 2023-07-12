# from _db import db
from modules._db import db


class TicketData:

    def store_ticket(self,
                     id,
                     status,
                     designee,
                     policy,
                     created_at,
                     periodic_expires,
                     resolution_expires):
        db.execute(f"""
            INSERT INTO ticket
            (ticket_id, status, designee,
            policy, created_at, periodic_expires,
            resolution_expires, send, edited)
            VALUES
            ('{id}', '{status}', '{designee}',
            '{policy}','{created_at}', '{periodic_expires}',
            '{resolution_expires}', '0', '0')
        """)

    def update_ticket(self,
                      id,
                      status,
                      designee,
                      policy,
                      created_at,
                      periodic_expires,
                      resolution_expires):
        db.execute(f"""
            UPDATE ticket SET
            status = '{status}',
            designee = '{designee}',
            policy = '{policy}',
            created_at = '{created_at}',
            periodic_expires = '{periodic_expires}',
            resolution_expires = '{resolution_expires}'
            WHERE ticket_id = '{id}'
        """)

    def add_send(self, id: str) -> None:
        send = db.query(f'SELECT send FROM ticket WHERE ticket_id = "{id}"')
        if send:
            n_send = send[0][0] + 1
            db.execute(
                f'UPDATE ticket SET send = {n_send} WHERE ticket_id = "{id}"')

    def verify_ticket(self, id):
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE ticket_id = '{id}'
        """)
        return bool(result)

    def new_sla(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id, send FROM ticket
            WHERE created_at >= DATETIME('now', 'localtime', '-{time}')
            AND (status = 'New' OR designee = 'Ninguém')
        """)
        if result:
            return result
        return []

    def new_sla_update(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE created_at >= DATETIME('now', 'localtime', '{time}')
            AND (status != 'New' AND send != '0')
        """)
        if result:
            return result
        return []

    def resolution_sla(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id, send FROM ticket
            WHERE resolution_expires <= DATETIME('now', 'localtime', '{time}')
            AND NOT ticket_id = '4937'
        """)
        if result:
            return result
        return []

    def resolution_sla_update(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE resolution_expires >= DATETIME('now', 'localtime', '-{time}')
            AND (NOT ticket_id = '4937' AND send != '0')
        """)
        if result:
            return result
        return []

    def periodic_sla(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id, send FROM ticket
            WHERE periodic_expires <= DATETIME('now', 'localtime', '{time}')
            AND NOT ticket_id = '4937'
        """)
        if result:
            return result
        return []

    def periodic_sla_update(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE periodic_expires >= DATETIME('now', 'localtime', '-{time}')
            AND (NOT ticket_id = '4937' AND send != '0')
        """)
        if result:
            return result
        return []

    def add_chat(self, id: str, chat: str, ts: str) -> None:
        db.execute(f"""
            UPDATE ticket
            SET chat = '{chat}', ts = '{ts}', edited = '0'
            WHERE ticket_id = '{id}'
        """)

    def edit_message(self, id: str) -> None:
        db.execute(f'UPDATE ticket SET edited = "1" WHERE ticket_id = "{id}"')

    def last_message(self, id: str) -> list:
        result = db.query(f"""
            SELECT chat, ts FROM ticket
            WHERE ticket_id = '{id}'
            AND edited = '0'
            AND send != '0'
        """)
        if result:
            return result
        return []


td = TicketData()
