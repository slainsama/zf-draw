import logging


def log_init():
    logging.basicConfig(filename="./logs.log", filemode="w", format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        datefmt="%d-%M-%Y %H:%M:%S", level=logging.INFO)
    logging.getLogger('gunicorn.error')