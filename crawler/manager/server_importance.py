"""
Module to add additional priority to a job's priority.

Will be done by manager since only manager has access to server.

This could also be done at client side but I decided not to to save time.
"""
from crawler.sql_models.server import Server


def server_importance(server_id: int):
    """
    Get the priority of a job.
    """
    priority = 0
    server = Server.select().where(Server.id == server_id).get()
    priority += min(5, server.page_rank * 5)
    if server.total_jobs > 0:
        priority += min(1, (server.success_jobs / server.total_jobs) * 1)
        priority += min(3, (server.relevant_documents / server.total_jobs) * 3)
    return priority
