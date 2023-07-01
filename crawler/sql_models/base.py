"""
Base model class for all models, defines the models connection.
"""
import json
import os

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


# pylint: disable=invalid-name
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def connect_to_database():
    """
    Connects to the database.
    """
    DATABASE.connect()


def execute_query_and_return_objects(query: str):
    """
    Executes a query and returns the results as a list of objects.
    Object are dotdicts, which means that you can access the values like this: object.key
    """
    ret = []
    for row in (cursor := DATABASE.execute_sql(query)).fetchall():
        job = dotdict()
        for column, value in zip(cursor.description, row):
            job[column[0]] = value
        ret.append(job)
    return ret


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
    """
    Store binary blobs in the database.
    """

    def db_value(self, value):
        return pickle.dumps(value)

    def python_value(self, value):
        if value is not None:
            try:
                return pickle.loads(value)
            except Exception as exception:
                LOG.error(f"Error while unpickling: {exception}")
                return None
        return value


class BaseModel(peewee.Model):
    """
    Base model class for all models, defines the models connection.
    """

    class Meta:
        """
        Declares models. Peewee needs this class.
        """
        database = DATABASE
