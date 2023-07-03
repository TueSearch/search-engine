from crawler.sql_models.server import Server
from crawler.worker.url_relevance import URL


def additional_priority_of_job_by_consider_server_importance(server_id: int, link: URL):
    """
    Get the priority of a job.
    """
    priority = link.priority
    if priority < 0:
        return priority

    server = Server.select().where(Server.id == server_id).get()
    priority += min(5, server.page_rank * 5)
    if server.total_jobs > 0:
        priority += min(5, (server.success_jobs / server.total_jobs) * 5)
        priority += min(5, (server.relevant_documents / server.total_jobs) * 5)
    return priority
