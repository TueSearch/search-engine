"""
This module contains the Job model. It represents a job in the crawler's queue.
"""
import peewee
from crawler.models.base import BaseModel, LongTextField


class Job(BaseModel):
    """
    Represents a job in the crawler's queue.
    """
    id = peewee.BigAutoField(primary_key=True)
    url = LongTextField()
    server = LongTextField()
    priority = peewee.IntegerField(default=0)
    done = peewee.BooleanField(default=False)
    success = peewee.BooleanField(default=None, null=True)

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
        return f"Job[server={self.server}, url={self.url}, ]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.url == other.url

    def __neq__(self, other):
        return self.url != other.url

    def __hash__(self):
        return hash(self.url)
    
