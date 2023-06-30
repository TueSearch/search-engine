from crawler.models.job import Job
from crawler.relevance_classification.url_relevance import URL


def assign_job_priority(job: Job, link: URL):
    job.priority = link.priority
