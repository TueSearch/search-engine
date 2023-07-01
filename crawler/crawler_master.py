import json
import os

from flask import Flask, jsonify, request

from crawler.priority_queue import PriorityQueue
from crawler.relevance_classification.url_relevance import URL
from crawler.sql_models.document import Document
from crawler.sql_models.job import Job
from crawler.sql_models.server import Server
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


@app.route('/', methods=['GET'])
def index():
    return "Master is running\n"


@app.route('/get_job', methods=['GET'])
def get_job():
    job = get_next_job_from_buffer()
    print(job)
    return jsonify(job)


@app.route('/mark_job_as_fail/<int:job_id>', methods=['POST'])
def mark_job_as_fail(job_id):
    Job.update(done=True, success=False).where(Job.id == job_id).execute()
    return "OK!"


@app.route('/save_crawling_results/<int:parent_job_id>', methods=['POST'])
def save_crawling_results(parent_job_id):
    entry = request.get_json()
    new_document = entry['new_document']
    new_document = json.loads(new_document)
    new_jobs = entry['new_jobs']
    new_jobs = [json.loads(job) for job in new_jobs]

    new_document = Document(**new_document)
    new_document.save()
    LOG.info(f"Created document {new_document}")

    for job in new_jobs:
        server = URL(job["url"]).server_name
        server = Server.get_or_create(name=server)[0]
        LOG.info(f"Created server {server}")
        job["server_id"] = server.id
        job["parent_id"] = new_document.id
        Job.insert(job).on_conflict_ignore().execute()
        LOG.info(f"Created job {job}")
    Job.update(done=True, success=True).where(Job.id == parent_job_id).execute()

    if new_document.relevant:
        LOG.info(f"Relevant document created {len(new_jobs)} new jobs.")
    else:
        LOG.info(f"Irrelevant document created {len(new_jobs)} new jobs.")
    return "OK!"


if __name__ == '__main__':
    app.run(host="localhost", debug=True, port=6000)
