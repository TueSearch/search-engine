"""
mse/initialize_database.py - Database Initialization

This module is responsible for initializing the database used by the Modern Search Engine. It defines functions to
create jobs and documents in the database based on SERP (Search Engine Results Page) data and manual seeds.

Usage:
    python3 mse/initialize_database.py
"""
import json
import os
import traceback

from playhouse.shortcuts import model_to_dict
import peewee
from dotenv import load_dotenv
from mse.models import DATABASE, Document, Job

from mse import utils

load_dotenv()

SERP_FILE = os.getenv("SERP_FILE")
QUEUE_LOG_FILE = os.getenv("QUEUE_LOG_FILE")
QUEUE_MANUAL_SEEDS = json.loads(os.getenv("QUEUE_MANUAL_SEEDS"))
QUEUE_INITIAL_BLACK_LIST = json.loads(os.getenv("QUEUE_INITIAL_BLACK_LIST"))
LOG = utils.get_logger(__name__, QUEUE_LOG_FILE)


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
        url = utils.normalize_url(entry["link"])
        server = utils.get_domain_name_without_subdomain_and_suffix_from_url(
            url)
        domain = utils.get_domain_name_without_subdomain_from_url(url)
        job = Job(bfs_layer=1, url=url, server=server, domain=domain)
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
        job = Job(
            bfs_layer=0,
            url=url,
            server=utils.get_domain_name_without_subdomain_and_suffix_from_url(
                url),
            domain=utils.get_domain_name_without_subdomain_from_url(url))
        batch.append(model_to_dict(job))
    try:
        Job.insert_many(batch).on_conflict_ignore().execute()
    except peewee.IntegrityError as error:
        LOG.error(f"Error: {str(error)}")
        print(traceback.format_exc())


def main():
    """
    Main function to initialize the database by creating jobs and documents.
    """
    with DATABASE.atomic() as transaction:
        try:
            create_manual_job_batch()
            for serp in utils.read_json_file(SERP_FILE).values():
                batch = create_serper_job_batch(serp)
                Job.insert_many(batch).on_conflict_ignore().execute()
        except Exception as error:
            LOG.error(f"Error while parsing SERP's result. Error: '{str(error)}'.")
            transaction.rollback()
            print(traceback.format_exc())


def reset():
    """
    Resets the database by dropping and recreating the tables.
    """
    DATABASE.drop_tables([Job, Document])
    DATABASE.create_tables([Job, Document])


if __name__ == '__main__':
    reset()
    main()
