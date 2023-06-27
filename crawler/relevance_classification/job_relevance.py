"""
Job relevance classification module. Contains the function is_job_relevant.
"""
import os
import json

from dotenv import load_dotenv
from crawler.models import Job
from crawler.relevance_classification.url_relevance import get_url_priority

load_dotenv()

CRAWL_EXCLUDED_EXTENSIONS = set(json.loads(
    os.getenv("CRAWL_EXCLUDED_EXTENSIONS")))
CRAWL_BLACK_LIST = set(json.loads(os.getenv("CRAWL_BLACK_LIST")))


def is_job_relevant(job: Job) -> bool:
    """
    Classifies the relevance of a job based on several criteria. A job is either relevant if
    - It's a seed job and the domain is not blocked.
    - Or the URL is relevant.

    Args:
        job (Job): The job to classify.
    return:
        bool: True if the job is relevant, False otherwise.
    """
    return job.server not in CRAWL_BLACK_LIST or get_url_priority(job.url) > 0
