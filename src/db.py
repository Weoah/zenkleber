from tinydb import TinyDB, Query
from datetime import datetime
from pytz import timezone

db = TinyDB('database.json', indent=4, sort_keys=True)
query = Query()


def br_time(iso_time):
    return datetime.fromtimestamp(
        datetime.fromisoformat(iso_time).timestamp(),
        tz=timezone('America/Sao_Paulo'))


def add_message(ticket, message):
    db.upsert(
        {
            "ticket": ticket.id,
            "status": ticket.status,
            "chat": message['channel'],
            "ts": message['ts'],
            "updated_at": br_time(ticket.updated_at).strftime("%H:%M - %d/%m")
        },
        query.ticket == ticket.id
    )


def get_message():
    return db.search(query.ts != 0)


def get_ticket(ticket):
    return db.search((query.ticket == ticket) & (query.ts != 0))


def solved_ticket(ticket):
    db.update({"ts": 0}, query.ticket == ticket)


def add_updated(ticket, value):
    db.update({"updated_at": value}, query.ticket == ticket)


def delete_ticket(ticket_id):
    db.remove(query.ticket == ticket_id)


def _truncate_table():
    db.truncate()
