"""
This module contains the Job model. It represents a job in the crawler's queue.
"""
import peewee
from playhouse.shortcuts import model_to_dict

from crawler import utils
from crawler.models.base import BaseModel, LongTextField, JSONField, URL
from crawler.models.server import Server

LOG = utils.get_logger(__file__)


class Job(BaseModel):
    """
    Represents a job in the crawler's queue.
    """
    id = peewee.BigAutoField(primary_key=True)
    url = LongTextField()
    server = peewee.DeferredForeignKey('servers', backref="server_id")
    parent = peewee.DeferredForeignKey('documents', backref="parent_id")
    anchor_texts = JSONField(default=[])
    anchor_texts_tokens = JSONField(default=[[]])
    priority = peewee.IntegerField(default=0)
    being_crawled = peewee.BooleanField(default=False)
    done = peewee.BooleanField(default=False)
    success = peewee.BooleanField(default=None, null=True)

    class Meta:
        """
        Meta class for the Job model.
        """
        table_name = 'jobs'

    def __str__(self):
        return f"Job[server={self.server}, url={self.url}, priority={self.priority}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.url == other.url

    def __neq__(self, other):
        return self.url != other.url

    def __hash__(self):
        return hash(self.url)

    @staticmethod
    def create_jobs(urls: list[URL]):
        from crawler import relevance_classification
        if len(urls) == 0:
            return
        servers = list(set(utils.url.get_server_name_from_url(url) for url in urls))
        servers = [Server.get_or_create(name=server)[0] for server in servers]
        servers = {server.name: server for server in servers}
        url_to_server = {url: servers[utils.url.get_server_name_from_url(url)] for url in urls}
        jobs_batch = []
        for url, server in url_to_server.items():
            job = Job(url=url,
                      server=server.id,
                      priority=relevance_classification.get_url_priority(url))
            job_dict = model_to_dict(job)
            job_dict["server"] = server.id
            jobs_batch.append(job_dict)
        Job.insert_many(jobs_batch).on_conflict_ignore().execute()
