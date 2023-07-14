from modules._db import db


class TicketData:

    def __repr__(self) -> str:
        return 'TicketData'

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

    def add_send_message(self, id: str) -> None:
        send = db.query(f'SELECT send FROM ticket WHERE ticket_id = "{id}"')
        if send:
            n_send = send[0][0] + 1
            db.execute(
                f'UPDATE ticket SET send = {n_send} WHERE ticket_id = "{id}"')

    def verify_ticket_stored(self, id):
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE ticket_id = '{id}'
        """)
        return bool(result)

    def verify_new_tickets(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id, send, ts FROM ticket
            WHERE DATETIME(created_at)
                    >= DATETIME('now', 'localtime', '-{time}')
            AND (status = 'New' OR designee = 'Ninguém')
        """)
        if result:
            return result
        return []

    def verify_new_ticket_update(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE DATETIME(created_at)
                    >= DATETIME('now', 'localtime', '{time}')
            AND (status != 'New' AND send != '0' AND NOT
                created_at >= DATETIME('now', 'localtime', '-{time}'))
        """)
        if result:
            return result
        return []

    def verify_metric_resolution(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id, send, ts FROM ticket
            WHERE DATETIME(resolution_expires)
                    <= DATETIME('now', 'localtime', '{time}')
            AND NOT ticket_id = '4937'
        """)
        if result:
            return result
        return []

    def verify_metric_resolution_update(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE DATETIME(resolution_expires)
                    >= DATETIME('now', 'localtime', '{time}')
            AND (NOT ticket_id = '4937' AND send != '0' AND NOT
                resolution_expires <= DATETIME('now', 'localtime', '{time}'))
        """)
        if result:
            return result
        return []

    def verify_metric_periodic(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id, send, ts FROM ticket
            WHERE DATETIME(periodic_expires)
                    <= DATETIME('now', 'localtime', '{time}')
            AND NOT ticket_id = '4937'
        """)
        if result:
            return result
        return []

    def verify_metric_periodic_update(self, time: str) -> list:
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE DATETIME(periodic_expires)
                    >= DATETIME('now', 'localtime', '{time}')
            AND (NOT ticket_id = '4937' AND send != '0' AND NOT
                 periodic_expires <= DATETIME('now', 'localtime', '{time}'))
        """)
        if result:
            return result
        return []

    def add_message_data(self, id: str, chat: str, ts: str) -> None:
        db.execute(f"""
            UPDATE ticket
            SET chat = '{chat}', ts = '{ts}', edited = '0'
            WHERE ticket_id = '{id}'
        """)

    def switch_edit(self, id: str, switch: bool) -> None:
        if switch:
            db.execute(f"""
                UPDATE ticket
                SET edited = "1", chat = "{None}", ts = "{None}", send = "0"
                WHERE ticket_id = "{id}"
            """)
            return
        db.execute(f'UPDATE ticket SET edited = "0" WHERE ticket_id = "{id}"')

    def get_message_data(self, id: str) -> list:
        result = db.query(f"""
            SELECT chat, ts FROM ticket
            WHERE ticket_id = '{id}'
            AND edited = '0'
            AND send != '0'
        """)
        if result:
            return result
        return []

    def get_message_data_reopen(self, id: str) -> list:
        result = db.query(f"""
            SELECT chat, ts FROM ticket
            WHERE ticket_id = '{id}'
            AND edited != '0'
        """)
        if result:
            return result
        return []

    def get_send_message(self, id: str, res: bool = False) -> list:
        if res:
            result = db.query(f"""
                SELECT send FROM ticket WHERE ticket_id = '{id}'
                AND resolution_expires != DATETIME()
            """)
        else:
            result = db.query(
                f"SELECT send FROM ticket WHERE ticket_id = '{id}'")
        if result:
            return result
        return []


td = TicketData()
