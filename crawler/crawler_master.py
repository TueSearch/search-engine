import json
import os

from flask import Flask, jsonify, request

from crawler.priority_queue import PriorityQueue
from crawler.relevance_classification.url_relevance import URL
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
    new_jobs = [dotdict(json.loads(job)) for job in new_jobs]

    new_document = Document(**new_document)
    new_document.save()
    LOG.info(f"Created document {new_document}")

    server_names = set()
    for job in new_jobs:
        server_name = URL(job["url"]).server_name
        server_names.add(server_name)
    server_names = list(server_names)
    Server.insert_many([{"name": server_name} for server_name in server_names]).on_conflict_ignore().execute()
    name_to_id = dict()
    for server_name in server_names:
        name_to_id[server_name] = Server.select(Server.id).where(Server.name == server_name).execute()[0].id
    LOG.info(f"Created new servers for incoming jobs {name_to_id}")

    for job in new_jobs:
        job.server_id = name_to_id[URL(job["url"]).server_name]
        job.parent_id = new_document.id
    Job.insert_many(new_jobs).on_conflict_ignore().execute()
    LOG.info(f"Created {len(new_jobs)} new jobs for document {new_document}")

    Job.update(done=True, success=True).where(Job.id == parent_job_id).execute()
    LOG.info("Updated parent job to done")
    return "Done!"


if __name__ == '__main__':
    app.run(host="localhost", debug=True, port=6000)
