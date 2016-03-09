import logging


def enable_default_log():
    logging.basicConfig(format='%(asctime)s -   %(message)s', datefmt='%I:%M:%S %p', level=logging.DEBUG)
