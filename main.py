import asyncio

from modules.logger import logger
from modules.queue import ticket_queue


async def check_new():
    task = asyncio.create_task(ticket_queue.check_new_sla())
    await task


async def update_new_():
    task = asyncio.create_task(ticket_queue.update_new())
    await task


async def check_resolution():
    task = asyncio.create_task(ticket_queue.check_resolution_sla())
    await task


async def update_resolution_():
    task = asyncio.create_task(ticket_queue.update_resolution())
    await task


async def check_periodic():
    task = asyncio.create_task(ticket_queue.check_periodic_sla())
    await task


async def update_periodic_():
    task = asyncio.create_task(ticket_queue.update_periodic())
    await task


async def main():
    logger.info('Executando uma repeticao...\n')
    await ticket_queue.get_tickets()
    new = asyncio.create_task(check_new())
    await new
    update_new = asyncio.create_task(update_new_())
    await update_new
    resolution = asyncio.create_task(check_resolution())
    await resolution
    update_resolution = asyncio.create_task(update_resolution_())
    await update_resolution
    periodic = asyncio.create_task(check_periodic())
    await periodic
    update_periodic = asyncio.create_task(update_periodic_())
    await update_periodic
    logger.info('Finalizando uma repeticao...\n')
    await asyncio.sleep(300)

if __name__ == "__main__":

    while True:
        asyncio.run(main())
