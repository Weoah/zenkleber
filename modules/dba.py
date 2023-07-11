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
            resolution_expires)
            VALUES
            ('{id}', '{status}', '{designee}',
            '{policy}','{created_at}', '{periodic_expires}',
            '{resolution_expires}')
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

    def verify_ticket(self, id):
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE ticket_id = '{id}'
        """)
        return bool(result)

    def get_new(self, time: str) -> list | None:
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE created_at <= DATETIME('now', 'localtime', '{time}')
            AND status = 'New'
        """)
        if result:
            return result
        return None

    def get_sla(self, time_p: str, time_r: str) -> list | None:
        result = db.query(f"""
            SELECT ticket_id FROM ticket
            WHERE periodic_expires <= DATETIME('now', 'localtime', '{time_p}')
            AND NOT ticket_id = '4937'
        """)
        # OR resolution_expires <= DATETIME('now', 'localtime', '{time_r}')
        if result:
            return result
        return None


td = TicketData()
