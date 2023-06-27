import argparse
import json
import math
import multiprocessing
import os
import random
import time

import peewee
from dotenv import load_dotenv
from requests.adapters import Retry

from crawler import utils
from crawler.models import DATABASE, Job
from crawler.crawl import Crawler
from crawler.priority_queue import PriorityQueue

load_dotenv()

CRAWL_RANDOM_SLEEP_INTERVAL = list(json.loads(
    os.getenv("CRAWL_RANDOM_SLEEP_INTERVAL")))
CRAWL_REDIRECTION_LIMIT = int(os.getenv("CRAWL_REDIRECTION_LIMIT"))
LOG = utils.get_logger(__file__)
random.seed(1)


class Loop:
    def __init__(self, number_to_crawl: int):
        self.number_to_crawl = number_to_crawl
        self.number_crawled = 0
        self.queue = PriorityQueue()
        LOG.info(f"Proceed to retrieve {number_to_crawl} jobs.")

    def store_results(self, jobs, results):
        for job, (new_document, new_jobs) in zip(jobs, results):
            with DATABASE.atomic() as transaction:
                try:
                    success = new_document is not None
                    if success:
                        new_document.save()
                        Job.insert_many(new_jobs).on_conflict_ignore().execute()
                    Job.update(done=True, success=success).where(Job.id == job.id).execute()
                except peewee.IntegrityError as error:
                    LOG.error(f"Error saving document {new_document.url}: {error}")
                    transaction.rollback()
            self.number_crawled += 1

    def loop(self):
        while len(jobs := self.queue.get_jobs_to_crawl()) > 0 and self.number_crawled < self.number_to_crawl:
            with multiprocessing.Manager() as manager:
                shared_results = manager.list([(None, []) for _ in jobs])
                time.sleep(random.uniform(*CRAWL_RANDOM_SLEEP_INTERVAL))  # Random delay

                def process_job(j_idx, j):
                    shared_results[j_idx] = Crawler(j).crawl()

                processes = [multiprocessing.Process(target=process_job, args=(i, job)) for i, job in enumerate(jobs)]
                for process in processes:
                    process.start()
                for process in processes:
                    process.join()
                self.store_results(jobs, shared_results)


def main():
    """The main function that initiates the crawling process."""
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument("-n", "--number", type=int, default=math.inf,
                        help="How many documents should be crawled")
    args = parser.parse_args()
    Loop(args.number).loop()


if __name__ == '__main__':
    main()
