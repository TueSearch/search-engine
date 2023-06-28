import argparse
import json
import math
import multiprocessing
import os
import random
import time

import peewee
from dotenv import load_dotenv

from crawler import utils, relevance_classification
from crawler.models.base import DATABASE
from crawler.models.document import Document
from crawler.models.job import Job
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

    def store_results(self, jobs: list[Job], results: list[Document]):
        """
        Store the results of the crawl in the database.
        Args:
            jobs: input jobs.
            results: results of the jobs.
        """
        for job, new_document in zip(jobs, results):
            with DATABASE.atomic() as transaction:
                try:
                    success = new_document is not None
                    if success:
                        new_document.save()
                        Job.create_jobs(new_document.relevant_links_list)
                    Job.update(done=True, success=success).where(Job.id == job.id).execute()
                except peewee.IntegrityError as error:
                    LOG.error(f"Error saving document {new_document.url}: {error}")
                    transaction.rollback()
            self.number_crawled += 1

    def loop(self):
        """
        Run the crawler until the queue is exhausted.
        """
        while len(jobs := self.queue.get_jobs_to_crawl()) > 0 and self.number_crawled < self.number_to_crawl:
            with multiprocessing.Manager() as manager:
                results = manager.list([None for _ in jobs])
                time.sleep(random.uniform(*CRAWL_RANDOM_SLEEP_INTERVAL))  # Random delay

                def process_job(j_idx, j):
                    results[j_idx] = Crawler(j).crawl()

                processes = [multiprocessing.Process(target=process_job, args=(i, job)) for i, job in enumerate(jobs)]
                for process in processes:
                    process.start()
                for process in processes:
                    process.join()
                self.store_results(jobs, results)


def main():
    """The main function that initiates the crawling process."""
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument("-n", "--number", type=int, default=math.inf,
                        help="How many documents should be crawled")
    args = parser.parse_args()
    Loop(args.number).loop()


if __name__ == '__main__':
    main()
