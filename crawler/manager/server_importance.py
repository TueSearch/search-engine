"""
Module to add additional priority to a job's priority.

Will be done by manager since only manager has access to server.

This could also be done at client side but I decided not to to save time.
"""
from crawler.sql_models.server import Server
import math

SUCCESS_BONUS = 3
RELEVANT_BONUS = 10
THRESHOLD = 0.05
MIN_PRIORITY = -20
MIN_SAMPLE = 5

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

        # Servers visited often enough
        if server.total_done_jobs > MIN_SAMPLE:
            if success_ratio < THRESHOLD:
                priority -= 5
            else:
                priority += SUCCESS_BONUS * (success_ratio - THRESHOLD)**2

            if relevant_ratio < THRESHOLD:
                priority += math.log(success_ratio / (1 - (success_ratio + 0.5 * THRESHOLD)))
            else:
                priority += RELEVANT_BONUS * (relevant_ratio - THRESHOLD)**2
        # Server visited not often enough, only constant penalty.
        else:
            if success_ratio < THRESHOLD:
                priority -= 5
            if relevant_ratio < THRESHOLD:
                priority -= 3
        priority = max(priority, MIN_PRIORITY)
    return priority
