#!/usr/bin/python3

"""
A helper script that wraps up QuoteBot to run as a queue with a worker on the side.
"""

from Queue import Queue
from threading import Thread
import quote_bot
import random

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
        request_obj[reqId] = result
        q.task_done()

def add_to_queue(query, author):
    reqId = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits for _ in range(ID_LEN)))
    q.put(query, author, reqId)
    request_objs[reqId] = "PENDING"
    return reqId

def start_worker():
    worker = threading.Thread(
            target=run_queue,
            args=(q,),
            name="worker-0",
    )
    worker.setDaemon(True)
    worker.start()
