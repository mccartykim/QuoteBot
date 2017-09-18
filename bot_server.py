#!/bin/usr/python3
"""
Server that wraps around the GoodReads class to search for quotes one at a time, respectful of the server's needs.
Drew HEAVY inspiration from
https://blog.miguelgrinberg.com/post/using-celery-with-flask
where I was able to see how to actually manage long asynchronous requests in http
Kimberly McCarty
"""
import flask
from flask import Flask, request, url_for, jsonify
from celery import Celery
from celery.bin import worker
import quote_bot

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

worker = worker.worker(app=celery)
options =  {'concurrency': 1, 'broker':app.config['CELERY_BROKER_URL']}

@celery.task(bind=True)
def queue_search(self, query, author):
    self.update_state(state="SEARCHING")
    gr = quote_bot.GoodReads()
    return gr.search(query, author)

@app.route('/search_quote', methods=['POST'])
def search_quote():
    error = None
    try:
        query = request.args['query']
        author = request.args['author']
        quote_task = queue_search.delay(query, author)
    except IndexError:
        error = "Invalid parameters, /search_quote?query=query&author=author"

    if error:
        print(error)
        return flask.jsonify({"error": error}), 422
    return flask.jsonify({"result": url_for('taskstatus', task_id=quote_task.id)}), 202, {"location": url_for('taskstatus', task_id=quote_task.id)}

@app.route('/get_result/<task_id>')
def taskstatus(task_id):
    task = queue_search.AsyncResult(task_id)
    if task.state == "PENDING":
        response = {"state": task.state}
    elif task.state != "FAILURE":
        response = {
                'state': task.state}
        response["result"] = task.result
    else:
        response = {"state": task.state}
    return jsonify(response)
