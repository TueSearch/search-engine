"""
Methods to execute SQL scripts in order. This is useful for database migrations.
"""
import functools
import json
import os

import peewee
from dotenv import load_dotenv

from crawler.worker.url_relevance import URL
from crawler.sql_models.base import BaseModel, DATABASE as db
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


def initialize_seed_jobs():
    """
    Initializes the database.
    """
    LOG.info(f"Starting to insert {get_seed_jobs()} initial jobs.")
    Job.insert_initial_jobs_into_databases([URL(url) for url in get_seed_jobs()])
    LOG.info(f"Finished inserting {get_seed_jobs()} initial jobs.")


def main():
    """
    Main method.
    """
    run_migration_scripts()
    initialize_seed_jobs()


if __name__ == '__main__':
    main()
