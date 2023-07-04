"""
This module contains the Job model. It represents a job in the crawler's queue.
"""

import peewee

from crawler import utils
from crawler.sql_models.base import BaseModel, LongTextField, JSONField, execute_query_and_return_objects, dotdict
from crawler.sql_models.server import Server

LOG = utils.get_logger(__file__)


class Job(BaseModel):
    """
    Represents a job in the crawler's queue.
    """
    id = peewee.BigAutoField(primary_key=True)
    url = LongTextField()
    server_id = peewee.BigIntegerField()

    @property
    def server(self) -> 'Server':
        """
        Returns the server object of the job.
        """
        query = f"select * from servers where id = {self.server_id}"
        return execute_query_and_return_objects(query)[0]

    @server.setter
    def server(self, value):
        """
        Sets the server of the job.
        """
        if isinstance(value, int):
            self.server_id = value
        else:
            self.server_id = value.id

    parent_id = peewee.BigIntegerField()

    @property
    def parent(self) -> 'Document':
        """
        Returns the parent document of the job.
        """
        query = f"select * from documents where id = {self.parent_id}"
        return execute_query_and_return_objects(query)[0]

    @parent.setter
    def parent(self, value):
        """
        Sets the parent document of the job.
        """
        self.parent_id = value.id

    url_tokens = JSONField(default=[])
    anchor_text = LongTextField(default="")
    anchor_text_tokens = JSONField(default=[])
    surrounding_text = LongTextField(default="")
    surrounding_text_tokens = JSONField(default=[])
    title_text = LongTextField(default="")
    title_text_tokens = JSONField(default=[])
    priority = peewee.FloatField(default=0.0)
    done = peewee.BooleanField(default=False)
    success = peewee.BooleanField(default=None, null=True)
    being_crawled = peewee.BooleanField(default=False)

    class Meta:
        """
        Meta class for the Job model.
        """
        table_name = 'jobs'

    def __str__(self):
        return f"Job[priority={self.priority}, server_id={self.server_id}, url={self.url}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.url == other.url

    def __neq__(self, other):
        return self.url != other.url

    def __hash__(self):
        return hash(self.url)

    def should_be_crawled(self) -> bool:
        """
        Returns whether the job should be crawled or not.
        """
        return self.priority > 0
