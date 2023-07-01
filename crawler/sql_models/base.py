"""
Base model class for all models, defines the models connection.
"""
import json
import os

import datetime
import pickle

import peewee
from dotenv import load_dotenv
from crawler.utils import log

load_dotenv()

DATABASE_LOG_FILE = os.getenv("DATABASE_LOG_FILE")
LOG = log.get_logger(__name__)

HOST = os.getenv("MYSQL_SEARCH_ENGINE_CONNECTION_HOST")
PORT = int(os.getenv("MYSQL_SEARCH_ENGINE_CONNECTION_PORT"))
DB = os.getenv("MYSQL_SEARCH_ENGINE_DATABASE")
DATABASE = peewee.MySQLDatabase(database=DB,
                                host=HOST,
                                port=PORT,
                                user=os.getenv("MYSQL_SEARCH_ENGINE_CONNECTION_USER"),
                                password=os.getenv("MYSQL_SEARCH_ENGINE_CONNECTION_PASSWORD"))
DATABASE.connect()


class LongTextField(peewee.TextField):
    """
    https://github.com/coleifer/peewee/issues/1773
    """
    field_type = 'LONGTEXT'


class JSONField(LongTextField):
    """
    https://stackoverflow.com/questions/40553790/peewee-orm-jsonfield-for-mysql
    """

    def db_value(self, value):
        if value is not None:
            if isinstance(value, str):
                return value
            return json.dumps(value)
        raise Exception("None type!")

    def python_value(self, value):
        if value is not None:
            if isinstance(value, str):
                return json.loads(value)
            return value
        raise Exception("None type!")


class PickleField(peewee.BlobField):
    def db_value(self, value):
        return pickle.dumps(value)

    def python_value(self, value):
        if value is not None:
            try:
                return pickle.loads(value)
            except Exception as e:
                LOG.error(f"Error while unpickling: {e}")
                return None
        return value


class BaseModel(peewee.Model):
    """
    Base model class for all models, defines the models connection.
    """
    created_date = peewee.DateTimeField(default=datetime.datetime.now)
    last_time_changed = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        """
        Declares models. Peewee needs this class.
        """
        database = DATABASE
