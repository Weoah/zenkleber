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
            resolution_expires, send)
            VALUES
            ('{id}', '{status}', '{designee}',
            '{policy}','{created_at}', '{periodic_expires}',
            '{resolution_expires}', '0')
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
            db.execute(
                f'UPDATE ticket SET send = {send[0][0] + 1} '
                f'WHERE ticket_id = "{id}"')

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

    def periodic_sla(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id, send FROM ticket
            WHERE periodic_expires <= DATETIME('now', 'localtime', '{time}')
            AND NOT ticket_id = '4937'
        """)
        if result:
            return result
        return []


td = TicketData()
