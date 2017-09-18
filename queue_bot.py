#!/usr/bin/python3

"""
A helper script that wraps up QuoteBot to run as a queue with a worker on the side.
"""

from queue import Queue
from threading import Thread
import threading
import quote_bot
import random
import string

ID_LEN = 8

request_objs = dict();
worker_count = 1

q = Queue()

def run_queue(q):
    #consider adding a breakpoint or something
    while True:
        query, author, reqId = q.get()
        gr = quote_bot.GoodReads()
        result = gr.search(query, author)
        request_objs[reqId] = result
        q.task_done()

def add_to_queue(query, author):
    reqId = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(ID_LEN))
    request_objs[reqId] = "PENDING"
    q.put((query, author, reqId))
    return reqId

def start_worker():
    worker = threading.Thread(
            target=run_queue,
            args=(q,),
            name="worker-0",
    )
    worker.setDaemon(True)
    worker.start()
