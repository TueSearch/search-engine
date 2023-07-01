from crawler.sql_models.server import Server


def get_job_priority(server_id, link):
    """
    Get the priority of a job.
    """
    priority = link.priority
    if priority < 0:
        return priority

    server = Server.select().where(Server.id == server_id).get()
    priority += min(50, server.page_rank * 50)
    if server.total_jobs > 0:
        priority += (server.success_jobs / server.total_jobs) * 10
        priority += (server.relevant_documents / server.total_jobs) * 10 * 2
    return priority
