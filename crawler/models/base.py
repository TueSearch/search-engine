"""
Base model class for all models, defines the models connection.
"""
import os

import datetime

import peewee
from dotenv import load_dotenv
from crawler.utils import log

load_dotenv()

DATABASE_LOG_FILE = os.getenv("DATABASE_LOG_FILE")
LOG = log.get_logger(__name__)

DATABASE = peewee.MySQLDatabase(database=os.getenv("MYSQL_SEARCH_ENGINE_DATABASE"),
                                host=os.getenv("MYSQL_SEARCH_ENGINE_CONNECTION_HOST"),
                                port=int(os.getenv("MYSQL_SEARCH_ENGINE_CONNECTION_PORT")),
                                user=os.getenv("MYSQL_SEARCH_ENGINE_CONNECTION_USER"),
                                password=os.getenv("MYSQL_SEARCH_ENGINE_CONNECTION_PASSWORD"))
DATABASE.connect()
LOG.info("Database connection successes.")


class LongTextField(peewee.TextField):
    """
    https://github.com/coleifer/peewee/issues/1773
    """
    field_type = 'LONGTEXT'


class BaseModel(peewee.Model):
    """
    Base model class for all models, defines the models connection.
    """
    created_date = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        """
        Declares models. Peewee needs this class.
        """
        database = DATABASE
