from time import sleep

# from modules.slack import send_message
from modules.queue import ticket_queue
from modules.logger import logger


print("#####Testando#####")

if __name__ == "__main__":

    # send_message('#zenkleber', '')
    while True:
        logger.info('Executando uma repeticao...\n')
        ticket_queue.get_tickets()
        ticket_queue.check_tickets_sla()
        logger.info('Finalizando uma repeticao...\n')
        sleep(600)
