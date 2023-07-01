import functools
import json
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from crawler.manager.priority_queue import PriorityQueue
from crawler.relevance_classification.url_relevance import URL
from crawler.sql_models.base import connect_to_database, dotdict
from crawler.sql_models.document import Document
from crawler.sql_models.job import Job
from crawler.sql_models.server import Server
from crawler.utils.log import get_logger

load_dotenv()

app = Flask(__name__)
CRAWL_BATCH_SIZE = int(os.getenv("CRAWL_BATCH_SIZE"))
CRAWLER_MANAGER_PORT = int(os.getenv("CRAWLER_MANAGER_PORT"))
CRAWLER_MANAGER_PASSWORD = os.getenv("CRAWLER_MANAGER_PASSWORD")
CRAWLER_MANAGER_PASSWORD_QUERY = os.getenv("CRAWLER_MANAGER_PASSWORD_QUERY")
PRIORITY_QUEUE = PriorityQueue()
LOG = get_logger(__name__)

JOB_BUFFER = []


def get_next_job_from_buffer():
    """
    Get the next job from the buffer.
    """
    global JOB_BUFFER
    if len(JOB_BUFFER) == 0:
        JOB_BUFFER = PRIORITY_QUEUE.get_next_jobs(CRAWL_BATCH_SIZE)
    print(JOB_BUFFER)
    return JOB_BUFFER.pop()


def password(func):
    """
    Check if the password is correct.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        code = request.args.get("pw", '')
        if len(code) > 0:
            if code == CRAWLER_MANAGER_PASSWORD:
                return func(*args, **kwargs)
            return "Wrong password.\n"
        return "Password not found.\n"

    return wrapper


@app.route('/', methods=['GET'])
def index():
    """
    Check if the server is running.
    """
    return "Master is running\n."


@app.route('/get_job', methods=['GET'])
@password
def get_job():
    """
    Get the next job from the priority queue.
    """
    job = get_next_job_from_buffer()
    LOG.info(f"Sending job {job} to worker")
    return jsonify(job)


@app.route('/mark_job_as_fail/<int:job_id>', methods=['POST'])
@password
def mark_job_as_fail(job_id):
    """
    Mark a job as failed.
    """
    Job.update(done=True, success=False).where(Job.id == job_id).execute()
    LOG.info(f"Marked job {job_id} as failed")
    return "Data updated."


@app.route('/save_crawling_results/<int:parent_job_id>', methods=['POST'])
@password
def save_crawling_results(parent_job_id):
    """
    Save the crawling results.
    """
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
    """
    Start the server.
    """
    connect_to_database()
    app.run(host="0.0.0.0", debug=True, port=CRAWLER_MANAGER_PORT)


if __name__ == '__main__':
    main()