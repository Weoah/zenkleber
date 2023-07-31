from src._db import _db


class DatabaseAcess:

    def store_ticket(self, id, status, created, periodic, wait) -> None:
        _db.execute(f"""
            INSERT INTO ticket
                (ticket_id, status, created_at,
                sla_periodic, sla_wait, sended,
                edited, chat, ts)
            VALUES
                ('{id}','{status}','{created}',
                '{periodic}','{wait}', '0',
                '0', 'None', 'None')
        """)

    def update_ticket(self, id, status, created, periodic, wait) -> None:
        _db.execute(f"""
            UPDATE ticket SET
                status = '{status}',
                created_at = '{created}',
                sla_periodic = '{periodic}',
                sla_wait = '{wait}'
            WHERE
                ticket_id = '{id}'
        """)

    def check_ticket(self, id) -> bool:
        result = _db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE ticket_id = '{id}'
        """)
        return bool(result)

    def add_sended(self, id) -> None:
        prev = _db.query(f'SELECT sended FROM ticket WHERE ticket_id = "{id}"')
        if prev:
            add = prev[0][0] + 1
            _db.execute(
                f'UPDATE ticket SET sended = "{add}" WHERE ticket_id = "{id}"')

    def check_new_ticket(self, time) -> list:
        result = _db.query(f"""
            SELECT ticket_id, sended, ts FROM ticket
            WHERE
                DATETIME(created_at) >= DATETIME('now', 'localtime', '-{time}')
                AND status = 'New'
        """)
        return result if result else []

    def update_new_ticket(self, time) -> list:
        result = _db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE
                DATETIME(created_at) >= DATETIME('now', 'localtime', '{time}')
            AND
                (status != 'New' AND sended != '0' AND NOT
                created_at >= DATETIME('now', 'localtime', '-{time}'))
        """)
        return result if result else []

    def check_requester_wait(self, time) -> list:
        result = _db.query(f"""
            SELECT ticket_id, sended, ts FROM ticket
            WHERE
                (DATETIME(sla_wait) <=
                DATETIME('now', 'localtime', '{time}'))
        """)
        return result if result else []

    def update_requester_wait(self, time) -> list:
        result = _db.query(f"""
            SELECT ticket_id, sended FROM ticket
            WHERE
                (DATETIME(sla_wait) >=
                DATETIME('now', 'localtime', '{time}'))
            AND
                (sended != '0' AND NOT
                sla_wait <= DATETIME('now', 'localtime', '{time}'))
        """)
        return result if result else []

    def check_periodic(self, time) -> list:
        result = _db.query(f"""
            SELECT ticket_id, sended, ts FROM ticket
            WHERE
                (DATETIME(sla_periodic) <=
                DATETIME('now', 'localtime', '{time}'))
        """)
        return result if result else []

    def update_periodic(self, time) -> list:
        result = _db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE
                (DATETIME(sla_periodic) >=
                DATETIME('now', 'localtime', '{time}'))
            AND
                (sended != '0' AND NOT
                sla_periodic <= DATETIME('now', 'localtime', '{time}'))
        """)
        return result if result else []

    def add_message(self, id, chat, ts) -> None:
        _db.execute(f"""
            UPDATE ticket SET
                chat = '{chat}',
                ts = '{ts}',
                edited = '0'
            WHERE
                ticket_id = '{id}'
        """)

    def edit_message(self, id) -> None:
        _db.execute(f"""
            UPDATE ticket SET
                edited = "1",
                chat = "None",
                ts = "None",
                sended = "0"
            WHERE
                ticket_id = "{id}"
        """)

    def unedit_message(self, id) -> None:
        _db.execute(f'UPDATE ticket SET edited = "0" WHERE ticket_id = "{id}"')

    def get_message(self, id) -> list:
        result = _db.query(f"""
            SELECT chat, ts FROM ticket
            WHERE
                ticket_id = '{id}'
                AND edited = '0'
                AND sended != '0'
        """)
        return result if result else []

    def get_message_sended(self, id) -> list:
        result = _db.query(f"""
            SELECT sended FROM ticket
            WHERE
                ticket_id = '{id}'
                AND sla_wait != DATETIME()
        """)
        return result if result else []

    def get_message_reopen(self, id) -> list:
        result = _db.query(f"""
            SELECT chat, ts FROM ticket
            WHERE
                ticket_id = '{id}'
                AND edited != '0'
        """)
        return result if result else []


db = DatabaseAcess()
