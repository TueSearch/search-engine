import argparse
import atexit
import json
import math
import multiprocessing
import os
import random
import signal
import time

import peewee
from crawler import utils
from crawler.crawl import Crawler
from crawler.models.document import Document
from crawler.models.job import Job
from crawler.models.server import Server
from crawler.priority_queue import PriorityQueue
from dotenv import load_dotenv

load_dotenv()

CRAWL_RANDOM_SLEEP_INTERVAL = list(json.loads(
    os.getenv("CRAWL_RANDOM_SLEEP_INTERVAL")))
CRAWL_BATCH_SIZE = int(os.getenv("CRAWL_BATCH_SIZE"))
LOG = utils.get_logger(__file__)
random.seed(1)


class Loop:
    def __init__(self, number_to_crawl: int):
        self.number_to_crawl = number_to_crawl
        self.number_crawled = 0
        self.queue = PriorityQueue()
        self.jobs = []
        LOG.info(f"Proceed to retrieve {number_to_crawl} jobs.")

    def store_results(self, results: list[Document]):
        """
        Store the results of the crawl in the database.
        Args:
            results: results of the jobs.
        """
        LOG.info(f"Crawled {len(results)} documents.")
        for job, new_document in zip(self.jobs, results):
            success = new_document is not None
            try:
                if success:  # Save new document
                    new_document.save()
                    if new_document.relevant:
                        LOG.info(f"Relevant {job}. Created {len(new_document.links)} new jobs.")
                    else:
                        LOG.info(f"Irrelevant {job}. Created {len(new_document.links)} new jobs.")
                    Job.create_jobs(new_document.relevant_links)
                else:
                    LOG.info(f"Failed {job}.")
            except peewee.IntegrityError as error:
                LOG.error(f"Error saving document {new_document.url}: {error}")
            finally:
                try:
                    # Mark job as done
                    Job.update(done=True, success=success, being_crawled=False).where(Job.id == job.id).execute()
                except Exception as error_marking_job_as_done:
                    LOG.error(f"Error marking job {job} as finished: {error_marking_job_as_done}")
            self.number_crawled += 1
        self.jobs = []

    def start_processes(self):
        """
        Start the processes to crawl the jobs.
        """
        with multiprocessing.Manager() as manager:
            results = manager.list([None for _ in self.jobs])
            time.sleep(random.uniform(*CRAWL_RANDOM_SLEEP_INTERVAL))  # Random delay

            def process_job(j_idx, job):
                LOG.info(f"Starting to crawl {job}.")
                results[j_idx] = Crawler(job).crawl()

            processes = [multiprocessing.Process(target=process_job, args=(i, job)) for i, job in
                         enumerate(self.jobs)]
            for process in processes:
                process.start()
            for process in processes:
                process.join()
            self.store_results(results)

    def loop(self):
        """
        Run the crawler until the queue is exhausted.
        """
        while self.number_crawled < self.number_to_crawl:
            self.jobs = self.queue.get_next_jobs(min(self.number_to_crawl - self.number_crawled, CRAWL_BATCH_SIZE))
            if len(self.jobs) == 0:
                LOG.info("No more jobs to crawl.")
                break
            LOG.info(f"Starting to crawl {len(self.jobs)} jobs.")
            self.start_processes()

    def handle_exit(self):
        """
        Handle exit by marking all jobs as not being crawled.
        """
        for job in self.jobs:
            if not job.done:
                job.being_crawled = False
                job.save()
                LOG.info(f"Exit handler: marked {job} as not being crawled.")


def main():
    """The main function that initiates the crawling process."""
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument("-n", "--number", type=int, default=math.inf,
                        help="How many documents should be crawled")
    args = parser.parse_args()

    print(f"Found: {Server.select().count()} servers in DB.")
    print(f"Found: {Job.select().count()} jobs in DB.")
    print(f"Found: {Document.select().count()} documents in DB.")

    loop = Loop(args.number)
    atexit.register(loop.handle_exit)
    signal.signal(signal.SIGTERM, loop.handle_exit)
    signal.signal(signal.SIGINT, loop.handle_exit)
    loop.loop()


if __name__ == '__main__':
    main()
