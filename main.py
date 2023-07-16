import asyncio

from modules.logger import logger
from modules.queue import ticket_queue


async def task_check_new():
    task = asyncio.create_task(ticket_queue.get_new_tickets())
    await task


async def task_update_new():
    task = asyncio.create_task(ticket_queue.update_new_tickets())
    await task


async def task_check_resolution():
    task = asyncio.create_task(ticket_queue.get_resolution_metric_tickets())
    await task


async def task_update_resolution():
    task = asyncio.create_task(ticket_queue.update_resolution_metric_tickets())
    await task


async def task_check_periodic():
    task = asyncio.create_task(ticket_queue.get_periodic_metric_tickets())
    await task


async def task_update_periodic():
    task = asyncio.create_task(ticket_queue.update_periodic_metric_tickets())
    await task


async def main():
    logger.info('Executando uma repeticao...\n')
    await ticket_queue.get_tickets()
    new = asyncio.create_task(task_check_new())
    await new
    update_new = asyncio.create_task(task_update_new())
    await update_new
    periodic = asyncio.create_task(task_check_periodic())
    await periodic
    update_periodic = asyncio.create_task(task_update_periodic())
    await update_periodic
    resolution = asyncio.create_task(task_check_resolution())
    await resolution
    update_resolution = asyncio.create_task(task_update_resolution())
    await update_resolution
    logger.info('Finalizando uma repeticao...\n')
    await asyncio.sleep(200)

if __name__ == "__main__":

    while True:
        asyncio.run(main())
