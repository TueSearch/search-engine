"""
This script updates the priority of all jobs in the database.
"""
from playhouse.shortcuts import model_to_dict
from tqdm import tqdm

from crawler import utils
from crawler.manager.server_importance import server_importance
from crawler.ml_models import url_relevance_trainer
from crawler.sql_models.job import Job
from crawler.worker.url_relevance import URL

LOG = utils.get_logger(__name__)


def update_priority_of_jobs_in_database():
    """
    Updates the priority of all jobs in the database.
    """
    for job in tqdm(Job.select().where(Job.done == False)):
        try:
            before = job.priority
            job.priority = server_importance(job.server_id) + URL(job.url).priority
            LOG.info("Updating priority of job: " + job.url + " from " + str(before) + " to " + str(job.priority))
            job.save()
        except Exception as e:
            LOG.info("Error while updating priority of job: " + str(model_to_dict(job)))
            LOG.info(e)


if __name__ == '__main__':
    url_relevance_trainer.train_model()
    update_priority_of_jobs_in_database()
