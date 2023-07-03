"""
This module manages the priority queue of URLs to be crawled.
"""
import os
import time

from crawler import utils
from crawler.sql_models.base import execute_query_and_return_objects, DATABASE
from crawler.sql_models.job import Job
import redis

LOG = utils.get_logger(__file__)
# Create a Redis connection
LOCK_REDIS_HOST = os.environ.get('LOCK_REDIS_HOST')
LOCK_REDIS_RETRY = int(os.environ.get('LOCK_REDIS_RETRY'))
LOCK_REDIS_TIMEOUT = int(os.environ.get('LOCK_REDIS_TIMEOUT'))
LOCK_REDIS_KEY = os.environ.get('LOCK_REDIS_KEY', 'lock_key')
LOCK_REDIS_RETRY_INTERVAL = float(os.environ.get('LOCK_REDIS_RETRY_INTERVAL'))
redis_client = redis.Redis(host=LOCK_REDIS_HOST, port=6379)


class PriorityQueue:
    """
    Manage which URL should be crawled as next.
    """

    @staticmethod
    def get_from_random_servers_one_highest_priority_job(n_jobs: int) -> list[Job]:
        """
        Retrieves a list of jobs from the models to be crawled.

        Returns:
            list[Job]: A list of Job objects representing the URLs to be crawled.
        """
        query = f"""
SELECT j.id, j.url FROM jobs j
JOIN servers s ON j.server_id = s.id
WHERE s.is_black_list = 0
  AND j.done = 0
  AND j.being_crawled = 0
  AND j.priority = (
    SELECT MAX(priority)
    FROM jobs
    WHERE server_id = j.server_id
      AND done = 0
      and j.being_crawled = 0
  )
ORDER BY RAND()
LIMIT {n_jobs}
"""
        return execute_query_and_return_objects(query)

    @staticmethod
    def get_one_highest_priority_job_from_each_server(n_jobs: int) -> list[Job]:
        """
        Retrieves a list of jobs from the models to be crawled.

        Returns:
            list[Job]: A list of Job objects representing the URLs to be crawled.
        """
        query = f"""
SELECT id, url
FROM (
    SELECT j.*,
        ROW_NUMBER() OVER (PARTITION BY server_id ORDER BY priority DESC) AS row_num
    FROM jobs j where j.done = 0 and j.being_crawled = 0
) as subquery
WHERE subquery.row_num = 1 
ORDER BY subquery.priority DESC 
LIMIT {n_jobs}
"""
        return execute_query_and_return_objects(query)

    @staticmethod
    def get_highest_priority_jobs(n_jobs: int) -> list[Job]:
        """
        Retrieves a list of jobs from the models to be crawled.

        Returns:
            list[Job]: A list of Job objects representing the URLs to be crawled.
        """
        query = f"""
SELECT id, url
FROM jobs where done = 0 and being_crawled = 0 ORDER BY priority DESC LIMIT {n_jobs}
"""
        return execute_query_and_return_objects(query)

    def get_next_jobs(self, n_jobs: int) -> list[Job]:
        """
        Retrieves a list of jobs from the models to be crawled.

        Returns:
            list[Job]: A list of Job objects representing the URLs to be crawled.
        """
        LOG.info(f"Queue received command to obtain {n_jobs} jobs.")

        retries = 0

        while retries < LOCK_REDIS_RETRY:
            # Attempt to acquire the distributed lock
            lock_acquired = redis_client.set(LOCK_REDIS_KEY, 'locked', nx=True, ex=LOCK_REDIS_TIMEOUT)

            if lock_acquired:
                with DATABASE.atomic() as transaction:
                    try:
                        jobs = list(PriorityQueue.get_highest_priority_jobs(n_jobs))
                        LOG.info(f"Retrieved from database: {jobs}")
                        for job in jobs:
                            Job.update(being_crawled=True).where(Job.id == job.id).execute()
                        return jobs
                    except Exception as exception:
                        LOG.error(f"Error while getting jobs from queue: {exception}")
                        transaction.rollback()
                        raise exception
                    finally:
                        # Release the distributed lock
                        redis_client.delete(LOCK_REDIS_KEY)
            else:
                LOG.info("Failed to acquire lock. Another process is currently accessing the code.")
                retries += 1
                time.sleep(LOCK_REDIS_RETRY_INTERVAL)

        # Maximum retries reached, handle the case when the lock couldn't be acquired
        LOG.error("Failed to acquire lock after maximum retries.")
        # Handle the case when the lock couldn't be acquired (retry logic or error handling)
