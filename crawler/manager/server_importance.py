"""
Module to add additional priority to a job's priority.

Will be done by manager since only manager has access to server.

This could also be done at client side but I decided not to to save time.
"""
from crawler.sql_models.server import Server

SUCCESS_FACTOR = 3
RELEVANT_FACTOR = 50
THRESHOLD = 0.05
UNDERTHRESHOLD_PENALTY = 5

def server_importance(server_id: int):
    """
    Get the priority of a job.
    """
    priority = 0
    server = Server.select().where(Server.id == server_id).get()
    priority += min(5, server.page_rank * 5)
    if server.total_done_jobs > 0:
        success_ratio = server.success_jobs / server.total_done_jobs
        relevant_ratio = server.relevant_documents / server.total_done_jobs
        priority += SUCCESS_FACTOR * (success_ratio - THRESHOLD) ** 3
        priority += RELEVANT_FACTOR * (relevant_ratio - THRESHOLD) ** 3
        if success_ratio < THRESHOLD:
            priority -= UNDERTHRESHOLD_PENALTY
        if relevant_ratio < THRESHOLD:
            priority -= UNDERTHRESHOLD_PENALTY
    return priority
