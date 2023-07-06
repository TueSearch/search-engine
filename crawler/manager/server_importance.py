"""
Module to add additional priority to a job's priority.

Will be done by manager since only manager has access to server.

This could also be done at client side but I decided not to to save time.
"""
from crawler.sql_models.server import Server

SUCCESS_BONUS = 10
RELEVANT_BONUS = 10

SUCCESS_PENALTY = 150
RELEVANT_PENALTY = 100

THRESHOLD = 0.05
MIN_SAMPLE = 5


def rho(x, a, b, c):
    """
    Defined in the report
    a: threshold.
    b: max reward.
    c: min penalty.
    """
    if x >= a:
        return b / (1 - a) ** 2 * (x - a) ** 2
    return -c / a ** 2 * (x - a) ** 2


def server_importance(server_id: int):
    """
    Get the priority of a job.
    """
    priority = 0
    server = Server.select().where(Server.id == server_id).get()
    priority += min(10, server.page_rank * 10)
    if server.total_done_jobs > 0:
        success_ratio = server.success_jobs / server.total_done_jobs
        relevant_ratio = server.relevant_documents / server.total_done_jobs

        # Servers visited often enough
        if server.total_done_jobs > MIN_SAMPLE:
            # Server successful enough
            priority += rho(success_ratio, THRESHOLD, SUCCESS_BONUS, SUCCESS_PENALTY)
            # Server relevant enough
            priority += rho(relevant_ratio, THRESHOLD, SUCCESS_BONUS, RELEVANT_PENALTY)
        # Server visited not often enough, only constant penalty.
        else:
            if success_ratio < THRESHOLD:
                priority -= 5
            if relevant_ratio < THRESHOLD:
                priority -= 5
    return priority
