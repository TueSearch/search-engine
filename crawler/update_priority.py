"""
This script updates the priority of all jobs in the database.
"""
from playhouse.shortcuts import model_to_dict


from backend.rankers import page_rank

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
    
    Job.update(priority = 0).where(Job.done == False)
    query = Job.select().where(Job.done == False)
    total = query.count()
    for job in query:
        try:
            job.priority = server_importance(job.server_id) + URL(job.url).priority
            LOG.info(f"[{updated}/{total}] Updated priority of {job.url}")
            job.save()
            updated += 1
        except Exception as e:
            LOG.info("Error while updating priority of job: " + str(model_to_dict(job)))
            LOG.info(e)


if __name__ == '__main__':
    page_rank.construct_directed_link_graph_from_crawled_documents()
    page_rank.construct_page_rank_of_servers_from_directed_graph()
    page_rank.update_page_rank_of_servers_in_database()
    update_priority_of_jobs_in_database()
