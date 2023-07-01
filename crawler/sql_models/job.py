"""
This module contains the Job model. It represents a job in the crawler's queue.
"""
import json

import peewee
from playhouse.shortcuts import model_to_dict

from crawler import utils
from crawler.relevance_classification.job_relevance import get_job_priority
from crawler.sql_models.base import BaseModel, LongTextField, JSONField, execute_query_and_return_objects
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
        query = f"select * from servers where id = {self.server_id}"
        return execute_query_and_return_objects(query)[0]

    @server.setter
    def server(self, value):
        self.server_id = value.id

    parent_id = peewee.BigIntegerField()

    @property
    def parent(self) -> 'Document':
        query = f"select * from documents where id = {self.parent_id}"
        return execute_query_and_return_objects(query)[0]

    @parent.setter
    def parent(self, value):
        self.parent_id = value.id

    anchor_text = LongTextField(default="")
    anchor_text_tokens = JSONField(default=[])
    surrounding_text = LongTextField(default="")
    surrounding_text_tokens = JSONField(default=[])
    title_text = LongTextField(default="")
    title_text_tokens = JSONField(default=[])
    priority = peewee.FloatField(default=0.0)
    done = peewee.BooleanField(default=False)
    success = peewee.BooleanField(default=None, null=True)

    def to_dict_from_master_to_worker(self):
        return {
            "id": self.id,
            "url": self.url
        }

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
        return self.priority > 0

    @staticmethod
    def insert_initial_jobs_into_databases(relevant_links: list['URL']):
        if len(relevant_links) == 0:
            return
        link_to_server_id = Server.create_servers_and_return_ids(relevant_links)
        jobs_batch = []
        for link, server_id in link_to_server_id.items():
            job = Job(url=link.url,
                      server=server_id,
                      priority=get_job_priority(server_id, link),
                      anchor_text=link.anchor_text,
                      anchor_text_tokens=link.anchor_text_tokens,
                      surrounding_text=link.surrounding_text,
                      surrounding_text_tokens=link.surrounding_text_tokens,
                      title_text=link.title_text,
                      title_text_tokens=link.title_text_tokens)
            jobs_batch.append(model_to_dict(job))
        Job.insert_many(jobs_batch).on_conflict_ignore().execute()

    @staticmethod
    def create_jobs_from_worker_to_master(relevant_links: list['URL']):
        jobs_batch = []
        for link in relevant_links:
            job = Job(url=link.url,
                      priority=link.priority,
                      anchor_text=link.anchor_text,
                      anchor_text_tokens=link.anchor_text_tokens,
                      surrounding_text=link.surrounding_text,
                      surrounding_text_tokens=link.surrounding_text_tokens,
                      title_text=link.title_text,
                      title_text_tokens=link.title_text_tokens)
            jobs_batch.append(json.dumps(model_to_dict(job)))
        return jobs_batch
