"""
Methods to execute SQL scripts in order. This is useful for database migrations.
"""
import json
import os

import peewee
from dotenv import load_dotenv

from crawler.models.base import BaseModel, DATABASE as db
from crawler.models.document import Document
from crawler.models.job import Job
from crawler.models.server import Server
from crawler.utils.log import get_logger

load_dotenv()
LOG = get_logger(__name__)

# SQL scripts directory path
SCRIPTS_DIRECTORY = 'scripts'
QUEUE_MANUAL_SEEDS = json.loads(os.getenv('QUEUE_MANUAL_SEEDS'))


# Create a model to represent the migration table
class Migration(BaseModel):
    """
    Model to represent the migration table.
    """
    name = peewee.CharField(unique=True)


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


def initialize_seed_jobs():
    """
    Initializes the database.
    """
    LOG.info(f"Starting to insert {QUEUE_MANUAL_SEEDS} initial jobs.")
    Job.create_jobs(QUEUE_MANUAL_SEEDS)
    LOG.info(f"Finished inserting {QUEUE_MANUAL_SEEDS} initial jobs.")


def initialize_documents():
    LOG.info("Starting to insert initial documents.")
    server = Server(name="an-example-server", is_black_list=False)
    server.save()
    job = Job(url="https://www.an-example-server.com/en/tubingen",
              server=server,
              priority=1,
              done=True,
              success=True)
    job.save()
    document = Document(
        job=job,
        html="<p>An example Tübingen document.</p>",
        title="Tübingen",
        body="Tübingen is a city in Germany.",
        links="[]",
        title_tokens='["tubingen"]',
        body_tokens='["tubingen", "is", "a", "city", "in", "germany"]',
        relevant=True)
    document.save()
    LOG.info("Finished inserting initial documents.")


def main():
    """
    Executes SQL scripts in order. This is useful for database migrations.
    """
    run_migration_scripts()
    initialize_seed_jobs()
    initialize_documents()


if __name__ == '__main__':
    main()
