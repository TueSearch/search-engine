"""
This module contains the Job model. It represents a job in the crawler's queue.
"""
import json

import peewee
import urllib3
from playhouse.shortcuts import model_to_dict

from crawler import utils
from crawler.sql_models.base import BaseModel, LongTextField, JSONField
from crawler.sql_models.document import Document
from crawler.sql_models.server import Server
from crawler.relevance_classification.job_relevance import get_job_priority

LOG = utils.get_logger(__file__)


class Job(BaseModel):
    """
    Represents a job in the crawler's queue.
    """
    id = peewee.BigAutoField(primary_key=True)
    url = LongTextField()
    server = peewee.ForeignKeyField(Server, backref="server_id")
    parent = peewee.ForeignKeyField(Document, backref="parent_id")
    anchor_text = LongTextField(default="")
    anchor_text_tokens = JSONField(default=[])
    surrounding_text = LongTextField(default="")
    surrounding_text_tokens = JSONField(default=[])
    title_text = LongTextField(default="")
    title_text_tokens = JSONField(default=[])
    priority = peewee.FloatField(default=0.0)
    being_crawled = peewee.BooleanField(default=False)
    done = peewee.BooleanField(default=False)
    success = peewee.BooleanField(default=None, null=True)

    class Meta:
        """
        Meta class for the Job model.
        """
        table_name = 'jobs'

    def __str__(self):
        return f"Job[priority={self.priority}, server={self.server}, url={self.url}]"

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
    def create_initial_jobs_and_insert(relevant_links: list['URL']):
        if len(relevant_links) == 0:
            return
        servers = [link.server_name for link in relevant_links]
        servers = [Server.get_or_create(name=server)[0] for server in servers]
        servers = {server.name: server for server in servers}
        link_to_server = {link: servers[link.server_name] for link in relevant_links}
        jobs_batch = []
        for link, server in link_to_server.items():
            job = Job(url=link.url,
                      server=server.id,
                      priority=get_job_priority(server, link),
                      anchor_text=link.anchor_text,
                      anchor_text_tokens=link.anchor_text_tokens,
                      surrounding_text=link.surrounding_text,
                      surrounding_text_tokens=link.surrounding_text_tokens,
                      title_text=link.title_text,
                      title_text_tokens=link.title_text_tokens)
            job_dict = model_to_dict(job)
            job_dict['server_id'] = server.id
            del job_dict['server']
            del job_dict['parent']
            jobs_batch.append(job_dict)
        Job.insert_many(jobs_batch).on_conflict_ignore().execute()

    @staticmethod
    def create_jobs_to_send_to_master(relevant_links: list['URL']):
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
            job_dict = model_to_dict(job)
            del job_dict["created_date"]
            del job_dict["last_time_changed"]
            jobs_batch.append(json.dumps(job_dict))
        return jobs_batch
