"""Service module to store package loggers"""
import logging
import sys


def configure_logger():
    logger = logging.getLogger(name='lexibot')
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(
        logging.Formatter('%(filename)s:%(lineno)d %(message)s'))
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)


if __name__ == "__main__":
    pass
