def get_job_priority(server, link):
    priority = link.priority
    if priority < 0:
        return priority

    priority += min(50, server.page_rank * 50)
    if server.total_jobs > 0:
        priority += (server.success_jobs / server.total_jobs) * 10
        priority += (server.relevant_documents / server.total_jobs) * 10 * 2
    return priority
