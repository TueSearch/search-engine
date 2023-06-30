"""
This module contains the Job model. It represents a job in the crawler's queue.
"""
import peewee
from playhouse.shortcuts import model_to_dict

from crawler import utils
from crawler.sql_models.base import BaseModel, LongTextField, JSONField
from crawler.sql_models.document import Document
from crawler.sql_models.server import Server
from crawler.relevance_classification.job_relevance import get_job_priority
from crawler.relevance_classification.url_relevance import URL

LOG = utils.get_logger(__file__)


class Job(BaseModel):
    """
    Represents a job in the crawler's queue.
    """
    id = peewee.BigAutoField(primary_key=True)
    url = LongTextField()
    server = peewee.ForeignKeyField(Server, backref="server_id")
    parent = peewee.ForeignKeyField(Document, backref="parent_id")
    anchor_texts = JSONField(default=[])
    anchor_texts_tokens = JSONField(default=[[]])
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
    def create_jobs(relevant_links: list[URL], parent: Document = None):
        if len(relevant_links) == 0:
            return
        servers = [link.server_name for link in relevant_links]
        servers = [Server.get_or_create(name=server)[0] for server in servers]
        servers = {server.name: server for server in servers}
        link_to_server = {link: servers[link.server_name] for link in relevant_links}
        jobs_batch = []
        parent_id = None if parent is None else parent.id
        parent_job = None if parent is None else Job.get_or_none(id=parent_id)
        inherited_priority = 0.0 if parent is None else min(10, parent_job.priority / 10.0)
        for link, server in link_to_server.items():
            job = Job(url=link.url, parent=parent_id, server=server.id, priority=get_job_priority(server, link))
            job.priority += inherited_priority
            job_dict = model_to_dict(job)
            job_dict['parent_id'] = parent_id
            job_dict['server_id'] = server.id
            del job_dict['server']
            del job_dict['parent']
            jobs_batch.append(job_dict)
        Job.insert_many(jobs_batch).on_conflict_ignore().execute()
