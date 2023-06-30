"""
Drop every table. Only use for development.
"""

from crawler.sql_models.base import DATABASE as db
from crawler.utils.log import get_logger

LOG = get_logger(__name__)


def drop_database():
    """
    Drop every table. Only use for development.
    """
    LOG.info("Dropping tables.")
    db.execute_sql("DROP TABLE IF EXISTS jobs_from_documents;")
    db.execute_sql("DROP TABLE IF EXISTS documents;")
    db.execute_sql("DROP TABLE IF EXISTS jobs;")
    db.execute_sql("DROP TABLE IF EXISTS servers;")
    db.execute_sql("DROP TABLE IF EXISTS migration;")
    LOG.info("All tables dropped.")


def main():
    """
    Drop every table. Only use for development.
    """
    drop_database()


if __name__ == '__main__':
    main()
