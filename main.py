from time import sleep

from src import log
from src.ticket_queue import queue


def main():
    log.info('Starting...\n')

    queue.get_tickets()

    queue.new_tickets()
    queue.update_new_tickets()

    queue.wait_tickets()
    queue.update_wait_tickets()

    queue.periodic_tickets()
    queue.update_periodic_tickets()

    log.info('Ending...\n')

    sleep(180)


if __name__ == '__main__':

    while True:
        main()
