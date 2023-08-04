import asyncio

from src import log
from src.ticket_queue import queue


async def task():
    await queue.get_tickets()

    asyncio.create_task(queue.new_tickets())
    asyncio.create_task(queue.update_new_tickets())

    asyncio.create_task(queue.wait_tickets())
    asyncio.create_task(queue.update_wait_tickets())

    asyncio.create_task(queue.periodic_tickets())
    asyncio.create_task(queue.update_periodic_tickets())

    asyncio.create_task(queue.solve_ticket())
    log.info('Ending...\n')


async def main():
    log.info('Starting...\n')
    asyncio.create_task(task())
    await asyncio.sleep(120)

if __name__ == '__main__':

    while True:
        asyncio.run(main())
