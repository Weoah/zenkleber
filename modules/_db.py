from threading import Lock
import sqlite3


class Database:

    def __init__(self) -> None:
        self.connected: bool = False
        self.lock: Lock = Lock()
        self.__connect()
        self.__first_time()

    def query(self, statement: str):
        self.lock.acquire()
        self.__connect()
        cur = self.__start()
        cur.execute(statement)  # type:ignore
        result = cur.fetchall()  # type:ignore
        cur.close()  # type:ignore
        self.__close()
        self.lock.release()
        if not result:
            return False
        return result

    def execute(self, statement: str):
        self.lock.acquire()
        self.__connect()
        cur = self.__start()
        cur.execute(statement)  # type:ignore
        self.db.commit()
        cur.close()  # type:ignore
        self.__close()
        self.lock.release()
        return True

    def __connect(self):
        self.db = sqlite3.connect('db.sqlite3')
        self.connected = True

    def __close(self):
        self.db.close()
        self.connected = False

    def __cursor(self):
        if self.connected:
            return self.db.cursor()
        return False

    def __start(self):
        if not self.connected:
            return False
        cur = self.__cursor()
        if not cur:
            return False
        return cur

    def __first_time(self):
        self.execute("""
            CREATE TABLE IF NOT EXISTS ticket
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id VARCHAR(255),
                status VARCHAR(255),
                designee VARCHAR(255),
                policy VARCHAR(255),
                created_at DATETIME,
                periodic_expires DATETIME,
                resolution_expires DATETIME,
                send INTEGER,
                edited INTEGER,
                chat VARCHAR(255),
                ts VARCHAR(255)
            )
        """)

    def _drop_table(self):
        self.execute("DROP TABLE ticket")

    def _reset_send(self):
        self.execute("UPDATE ticket SET send = '0' WHERE id >= 1")


db = Database()

if __name__ == '__main__':
    # db._drop_table()
    # db._reset_send()
    ...
