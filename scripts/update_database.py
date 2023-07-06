"""
This script updates the priority of all jobs in the database.
"""
from playhouse.shortcuts import model_to_dict

from crawler import utils
from crawler.manager.server_importance import server_importance
from crawler.sql_models.job import Job
from crawler.worker.url_relevance import URL

LOG = utils.get_logger(__name__)


def update_priority_of_jobs_in_database():
    """
    Updates the priority of all jobs in the database.
    """
    updated = 0
    LOG.info(f"Starting to update priority of jobs in database.")
    for job in Job.select().where(Job.done == False):
        try:
            before = job.priority
            job.priority = server_importance(job.server_id) + URL(job.url).priority
            LOG.info(f"[{updated}]Updating priority of job: " + job.url + " from " + str(before) + " to " + str(job.priority))
            job.save()
            updated += 1
        except Exception as e:
            LOG.info("Error while updating priority of job: " + str(model_to_dict(job)))
            LOG.info(e)


if __name__ == '__main__':
    update_priority_of_jobs_in_database()
