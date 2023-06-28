"""
This module manages the priority queue of URLs to be crawled.
"""
import os

from dotenv import load_dotenv

from crawler import utils
from crawler.models.job import Job

load_dotenv()
CRAWL_BATCH_SIZE = int(os.getenv("CRAWL_BATCH_SIZE"))

LOG = utils.get_logger(__file__)


class PriorityQueue:
    """
    Manage which URL should be crawled as next.
    """

    def get_jobs_to_crawl(self) -> list[Job]:
        """
        Retrieves a list of jobs from the models to be crawled.

        Returns:
            list[Job]: A list of Job objects representing the URLs to be crawled.
        """
        out = list(Job.select().where(Job.done == False).order_by(Job.priority.desc()).limit(CRAWL_BATCH_SIZE))
        LOG.info(f"Proceed to crawl {len(out)} jobs")
        return out
