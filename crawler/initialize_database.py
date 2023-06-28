"""
crawler/initialize_database.py - Database Initialization

This module is responsible for initializing the models used by the Modern Search Engine. It defines functions to
create jobs and documents in the models based on SERP (Search Engine Results Page) data and manual seeds.

Usage:
    python3 -m crawler.initialize_database
"""
import json
import os
import sys
import traceback

from playhouse.shortcuts import model_to_dict
import peewee
from dotenv import load_dotenv
from crawler.models import DATABASE, Document, Job

from crawler import utils

load_dotenv()

SERP_FILE = os.getenv("SERP_FILE")
QUEUE_MANUAL_SEEDS = json.loads(os.getenv("QUEUE_MANUAL_SEEDS"))
QUEUE_INITIAL_BLACK_LIST = json.loads(os.getenv("QUEUE_INITIAL_BLACK_LIST"))
LOG = utils.get_logger(__file__)


def create_serper_job_batch(result) -> list[dict]:
    """
    Creates a batch of jobs based on SERP data.

    Args:
        result (dict): SERP data containing search results.

    Returns:
        list[dict]: List of dictionaries representing job models.

    """
    batch = []
    for entry in result[("news" if "news" in result else "organic")]:
        url = utils.url.normalize_url(entry["link"])
        server = utils.url.get_server_name_from_url(url)
        job = Job(url=url, server=server, priority=sys.maxsize)
        if server not in QUEUE_INITIAL_BLACK_LIST:
            batch.append(model_to_dict(job))
            LOG.info(f"Added {job}")
        else:
            LOG.info(f"Skipped {job}")
    return batch


def create_manual_job_batch():
    """
    Creates a batch of jobs based on manual seeds.
    """
    batch = []
    for url in QUEUE_MANUAL_SEEDS:
        job = Job(url=url, server=utils.url.get_server_name_from_url(url), priority=sys.maxsize)
        batch.append(model_to_dict(job))
    try:
        Job.insert_many(batch).on_conflict_replace().execute()
    except peewee.IntegrityError as error:
        LOG.error(f"Error: {str(error)}")
        print(traceback.format_exc())


def main():
    """
    Main function to initialize the models by creating jobs and documents.
    """
    with DATABASE.atomic() as transaction:
        try:
            create_manual_job_batch()
            for serp in utils.io.read_json_file(SERP_FILE).values():
                batch = create_serper_job_batch(serp)
                Job.insert_many(batch).on_conflict_replace().execute()
        except Exception as error:
            LOG.error(f"Error while parsing SERP's result. Error: '{str(error)}'.")
            transaction.rollback()
            print(traceback.format_exc())


if __name__ == '__main__':
    main()
