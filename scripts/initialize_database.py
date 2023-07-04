"""
Methods to execute SQL scripts in order. This is useful for database migrations.
"""
import functools
import json
import os

import peewee
from dotenv import load_dotenv
from playhouse.shortcuts import model_to_dict

from crawler.manager.server_importance import server_importance
from crawler.sql_models.server import Server
from crawler.worker.url_relevance import URL
from crawler.sql_models.base import BaseModel, DATABASE as db, DATABASE
from crawler.sql_models.job import Job
from crawler.utils.log import get_logger

load_dotenv()
LOG = get_logger(__name__)

# SQL scripts directory path
SCRIPTS_DIRECTORY = 'scripts'


# Create a model to represent the migration table
class Migration(BaseModel):
    """
    Model to represent the migration table.
    """
    name = peewee.CharField(unique=True)

    class Meta:
        """
        Meta class for the migration model.
        """
        table_name = 'migrations'


def run_migration_scripts():
    """
    Executes SQL scripts in order. This is useful for database migrations.
    """
    # Sort the SQL files based on their filename
    sql_files = sorted([f for f in os.listdir(SCRIPTS_DIRECTORY) if f.endswith('.sql')])

    db.create_tables([Migration])
    # Execute each SQL script in order
    for sql_file in sql_files:
        LOG.info(f'Executing migration: {sql_file}')
        with open(os.path.join(SCRIPTS_DIRECTORY, sql_file), 'r', encoding='utf-8') as file:
            script = file.read()
            migration_name = os.path.splitext(sql_file)[0]

            # Check if the migration has already been executed
            if Migration.select().where(Migration.name == migration_name).exists():
                LOG.info(f'Migration {migration_name} already executed')
                continue

            # Execute the SQL script
            db.execute_sql(script)

            # Add the migration to the migration table
            Migration.create(name=migration_name)

            LOG.info(f'Migration {migration_name} executed successfully')


@functools.lru_cache()
def get_seed_jobs():
    """
    Returns the seed jobs from the seeds.json file.
    """
    with open("scripts/seeds.json") as f:
        return json.loads(f.read())


def insert_initial_jobs_into_databases(relevant_links: list['URL']):
    """
    Inserts the initial jobs into the database.
    """
    if len(relevant_links) == 0:
        return
    link_to_server_id = Server.create_servers_and_return_ids(relevant_links)
    jobs_batch = []
    for link, server_id in link_to_server_id.items():
        job = Job(url=link.url,
                  server=server_id,
                  priority=server_importance(server_id) + URL(link.url).priority,
                  anchor_text=link.anchor_text,
                  anchor_text_tokens=link.anchor_text_tokens,
                  surrounding_text=link.surrounding_text,
                  surrounding_text_tokens=link.surrounding_text_tokens,
                  title_text=link.title_text,
                  title_text_tokens=link.title_text_tokens)
        jobs_batch.append(model_to_dict(job))
    Job.insert_many(jobs_batch).on_conflict_ignore().execute()


def initialize_seed_jobs():
    """
    Initializes the database.
    """
    LOG.info(f"Starting to insert {get_seed_jobs()} initial jobs.")
    insert_initial_jobs_into_databases([URL(url) for url in get_seed_jobs()])
    LOG.info(f"Finished inserting {get_seed_jobs()} initial jobs.")


@functools.lru_cache()
def get_block_patterns():
    """
    Returns the seed jobs from the seeds.json file.
    """
    with open("scripts/blocked_patterns.json") as f:
        return json.loads(f.read())


def mark_blocked_patterns_as_priority_0():
    """
    Initializes the database.
    """
    for block_pattern in get_block_patterns():
        LOG.info(f"Marking job with url pattern {block_pattern} as invalid")
        DATABASE.execute_sql(f"""UPDATE jobs
SET priority = 0
WHERE url like '{block_pattern}';""")
        LOG.info(f"Finished marking useless url pattern {block_pattern}")


def main():
    """
    Main method.
    """
    run_migration_scripts()
    initialize_seed_jobs()
    mark_blocked_patterns_as_priority_0()


if __name__ == '__main__':
    main()
