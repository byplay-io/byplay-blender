import logging

from queue import Queue
import threading


def _sync_post(url, params):
    import requests
    logging.info("Doing async request to {}".format(url))
    res = requests.post(url, **params)
    logging.info("Async response: {}".format(res))


def async_post(url, **params):
    logging.info("Starting async request to {}".format(url))
    thread = threading.Thread(target=_sync_post, args=(url, params))
    thread.setDaemon(True)
    thread.start()
