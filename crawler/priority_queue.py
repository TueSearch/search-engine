"""
This module manages the priority queue of URLs to be crawled.
"""
import os

from dotenv import load_dotenv

from crawler import utils
from crawler.models.base import DATABASE
from crawler.models.job import Job

load_dotenv()
CRAWL_BATCH_SIZE = int(os.getenv("CRAWL_BATCH_SIZE"))

LOG = utils.get_logger(__file__)


class PriorityQueue:
    """
    Manage which URL should be crawled as next.
    """

    def get_highest_priority_jobs(self) -> list[Job]:
        """
        Retrieves a list of jobs from the models to be crawled.

        Returns:
            list[Job]: A list of Job objects representing the URLs to be crawled.
        """
        out_jobs = []
        query = """
        select * from jobs where done = 0 and being_crawled = 0 order by priority desc limit %s;"""
        for row in (cursor := DATABASE.execute_sql(query, (CRAWL_BATCH_SIZE,))).fetchall():
            job = dict()
            for column, value in zip(cursor.description, row):
                job[column[0]] = value
            out_jobs.append(Job(**job))
        return out_jobs
