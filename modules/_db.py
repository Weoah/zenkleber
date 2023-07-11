from threading import Lock
import sqlite3


class Database:

    def __init__(self) -> None:
        self.connected: bool = False
        self.lock: Lock = Lock()
        self.__connect()
        self.__first_time()

    def query(self, statement: str):
        self.__connect()
        cur = self.__start()
        self.lock.acquire()
        cur.execute(statement)  # type:ignore
        result = cur.fetchall()  # type:ignore
        cur.close()  # type:ignore
        self.lock.release()
        self.__close()
        if not result:
            return False
        return result

    def execute(self, statement: str):
        self.__connect()
        cur = self.__start()
        self.lock.acquire()
        cur.execute(statement)  # type:ignore
        self.db.commit()
        cur.close()  # type:ignore
        self.lock.release()
        self.__close()
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
                id integer primary key autoincrement,
                ticket_id varchar(255),
                status varchar(255),
                designee varchar(255),
                policy varchar(255),
                created_at datetime,
                periodic_expires datetime,
                resolution_expires datetime
            )
        """)

    def _drop_table(self):
        self.execute("""drop table ticket""")


db = Database()

if __name__ == '__main__':
    # db._drop_table()
    ...
