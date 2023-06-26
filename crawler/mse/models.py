"""
mse/models.py - Models for the Modern Search Engine

This module defines the data models used by the Modern Search Engine for representing jobs
in the crawler's queue and crawled documents.

Usage:
    python3 mse/models.py
"""
import datetime
import functools
import json
import os

import peewee
from dotenv import load_dotenv

from mse import utils

load_dotenv()

DATABASE_LOG_FILE = os.getenv("DATABASE_LOG_FILE")
LOG = utils.get_logger(__name__, DATABASE_LOG_FILE)

DATABASE = peewee.MySQLDatabase(database=os.getenv("DATABASE_DATABASE"),
                                host=os.getenv("DATABASE_HOST"),
                                port=int(os.getenv("DATABASE_PORT")),
                                user=os.getenv("DATABASE_USER"),
                                password=os.getenv("DATABASE_PASSWORD"))


class LongTextField(peewee.TextField):
    """
    https://github.com/coleifer/peewee/issues/1773
    """
    field_type = 'LONGTEXT'


class BaseModel(peewee.Model):
    """
    Base model class for all models, defines the database connection.
    """

    class Meta:
        """
        Declares database. Peewee needs this class.
        """
        database = DATABASE


class Job(BaseModel):
    """
    Represents a job in the crawler's queue.
    """
    bfs_layer = peewee.IntegerField()
    url = LongTextField()
    server = LongTextField()
    domain = LongTextField()
    done = peewee.BooleanField(default=False)
    success = peewee.BooleanField(default=None, null=True)
    created_date = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        """
        Declares indices and constraints. Peewee needs this class.
        """
        indexes = (
            peewee.SQL('create unique index url_index on job (url(750))'),
        )
        constraints = [
            peewee.Check(
                '((done AND success IS NOT NULL) OR (NOT done AND success IS NULL))')
        ]

    def __str__(self):
        return f"Job[bfs_layer={self.bfs_layer}, url={self.url}, server={self.server}, domain={self.domain}, created_date={self.created_date}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.url == other.url

    def __neq__(self, other):
        return self.url != other.url

    def __hash__(self):
        return hash(self.url)


class Document(BaseModel):
    """
    Represents a crawled document.
    """
    bfs_layer = peewee.IntegerField()
    url = LongTextField()
    server = LongTextField()
    domain = LongTextField()
    title = LongTextField()
    text = LongTextField()
    tokens = LongTextField()
    all_harvested_links = LongTextField()
    non_relevant_links = LongTextField()
    relevant_links = LongTextField()
    relevant = peewee.BooleanField(default=True)
    job = peewee.ForeignKeyField(Job, backref="job")
    created_date = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        """Metadata options for the Document model."""
        table_options = {'engine': 'ARCHIVE'}
        indexes = (
            peewee.SQL('create unique index url_index on document (url(750))'),
        )

    @functools.cached_property
    def all_harvested_links_list(self) -> list[str]:
        """Get a list of all harvested links."""
        return json.loads(str(self.all_harvested_links))

    @functools.cached_property
    def non_relevant_links_list(self) -> list[str]:
        """Get a list of non-relevant links."""
        return json.loads(str(self.non_relevant_links))

    @functools.cached_property
    def relevant_links_list(self) -> list[str]:
        """Get a list of relevant links."""
        return json.loads(str(self.relevant_links))

    @functools.cached_property
    def tokens_list(self) -> list[str]:
        """Get a list of tokens."""
        return json.loads(str(self.tokens))

    def __str__(self):
        return f"Document[Job={self.job}, cleaned_text={self.text[:100]}, tokens={self.tokens_list[:100]}, all_harvested_links={self.all_harvested_links_list[:100]}, relevant={self.relevant}]"


DATABASE.connect()
if __name__ == '__main__':
    DATABASE.drop_tables([Job, Document])
    DATABASE.create_tables([Job, Document])
    DATABASE.close()
