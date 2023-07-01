import json
import os

import time

import flask
from flask import g
from flask import Flask, jsonify, request

from crawler.priority_queue import PriorityQueue
from crawler.relevance_classification.url_relevance import URL
from crawler.sql_models.base import connect_to_database
from crawler.sql_models.document import Document
from crawler.sql_models.job import Job
from crawler.sql_models.server import Server
from crawler.utils import dotdict
from crawler.utils.log import get_logger

app = Flask(__name__)
CRAWL_BATCH_SIZE = int(os.getenv("CRAWL_BATCH_SIZE"))
PRIORITY_QUEUE = PriorityQueue()
LOG = get_logger(__name__)

JOB_BUFFER = []


def get_next_job_from_buffer():
    global JOB_BUFFER
    if len(JOB_BUFFER) == 0:
        JOB_BUFFER = PRIORITY_QUEUE.get_next_jobs(CRAWL_BATCH_SIZE)
    print(JOB_BUFFER)
    return JOB_BUFFER.pop()


@app.before_request
def before_request():
    g.start = time.time()


@app.after_request
def after_request(response):
    diff = time.time() - g.start
    if ((response.response) and
            (200 <= response.status_code < 300) and
            (response.content_type.startswith('text/html'))):
        response.set_data(response.get_data().replace(
            b'__EXECUTION_TIME__', bytes(str(diff), 'utf-8')))
    return response


@app.route('/', methods=['GET'])
def index():
    return "Master is running\n"


@app.route('/get_job', methods=['GET'])
def get_job():
    job = get_next_job_from_buffer()
    LOG.info(f"Sending job {job} to worker")
    return jsonify(job)


@app.route('/mark_job_as_fail/<int:job_id>', methods=['POST'])
def mark_job_as_fail(job_id):
    Job.update(done=True, success=False).where(Job.id == job_id).execute()
    LOG.info(f"Marked job {job_id} as failed")
    return "Data updated."


@app.route('/save_crawling_results/<int:parent_job_id>', methods=['POST'])
def save_crawling_results(parent_job_id):
    entry = dotdict(request.get_json())
    new_document = dotdict(json.loads(entry.new_document))
    new_jobs = [dotdict(json.loads(job)) for job in entry.new_jobs]

    new_document = Document(**new_document)
    new_document.save()
    LOG.info(f"Created document {new_document.id}")

    new_jobs_links = list(set(URL(job.url) for job in new_jobs))
    new_links_to_server_id = Server.create_servers_and_return_ids(new_jobs_links)
    LOG.info(f"Created new servers to save jobs {new_links_to_server_id}")

    for new_job in new_jobs:
        new_job["server_id"] = new_links_to_server_id[URL(new_job.url)]
        new_job["parent_id"] = new_document.id
    Job.insert_many(new_jobs).on_conflict_ignore().execute()
    LOG.info(f"Created {len(new_jobs)} new jobs for document {new_document.id}")

    Job.update(done=True, success=True).where(Job.id == parent_job_id).execute()
    LOG.info("Updated parent job to done")
    return "Data created."


def main():
    connect_to_database()
    app.run(host="localhost", debug=True, port=6000)


if __name__ == '__main__':
    main()
