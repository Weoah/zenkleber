import logging
import sys


def log(name="log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    system_handler = logging.StreamHandler(sys.stdout)
    system_handler.setLevel(logging.DEBUG)
    system_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(f"{name}.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(system_handler)
    logger.addHandler(file_handler)

    return logger


logger = log()
