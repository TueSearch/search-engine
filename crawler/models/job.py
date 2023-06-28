"""
This module contains the Job model. It represents a job in the crawler's queue.
"""
import peewee
from crawler.models.base import BaseModel, LongTextField, DATABASE
from crawler.models.server import Server


class Job(BaseModel):
    """
    Represents a job in the crawler's queue.
    """
    id = peewee.BigAutoField(primary_key=True)
    url = LongTextField()
    server = peewee.ForeignKeyField(Server, backref="server_id")
    priority = peewee.IntegerField(default=0)
    done = peewee.BooleanField(default=False)
    success = peewee.BooleanField(default=None, null=True)

    def __str__(self):
        return f"Job[server={self.server}, url={self.url}, ]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.url == other.url

    def __neq__(self, other):
        return self.url != other.url

    def __hash__(self):
        return hash(self.url)

    @staticmethod
    def create_job(url: str):
        from crawler import relevance_classification
        from crawler import utils
        server = utils.url.get_server_name_from_url(url)
        server_entity = Server.get_or_create(name=server)[0]
        priority = relevance_classification.get_url_priority(url)
        Job.insert(url=url, server=server_entity, priority=priority).on_conflict_ignore().execute()

    @staticmethod
    def create_jobs(urls: list[str]):
        from crawler import utils
        from crawler import relevance_classification
        servers = list(set([utils.url.get_server_name_from_url(url) for url in urls]))
        servers = [Server.get_or_create(name=server)[0] for server in servers]
        servers = {server.name: server for server in servers}
        urls = {url: servers[utils.url.get_server_name_from_url(url)] for url in urls}
        jobs = []
        for url, server in urls.items():
            jobs.append(Job.get_or_create(url=url,
                                          server=server,
                                          priority=relevance_classification.get_url_priority(url))[0])
        return jobs
