from crawler.models.job import Job
from crawler.relevance_classification.url_relevance import URL


def get_job_priority(job: Job, link: URL):
    priority = link.priority
    if priority < 0:
        return priority

    priority += min(50, job.server.page_rank * 50)
    priority += (job.server.success_jobs / job.server.total_jobs) * 10
    priority += (job.server.relevant_jobs / job.server.total_jobs) * 10 * 2
    return priority
