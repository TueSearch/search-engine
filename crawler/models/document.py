"""
This module contains the Document model. It represents a crawled document.
"""
import peewee

from crawler.models.base import BaseModel, LongTextField, JSONField, PickleField


class Document(BaseModel):
    """
    Represents a crawled document.
    """
    from crawler.models.job import Job
    id = peewee.BigAutoField(primary_key=True)
    job = peewee.ForeignKeyField(Job, backref="job_id")
    html = LongTextField()
    title = LongTextField()
    body = LongTextField()
    links = LongTextField()
    title_tokens = JSONField()
    body_tokens = JSONField()
    body_tfidf = PickleField()
    relevant = peewee.BooleanField(default=True)

    class Meta:
        """
        Meta class for the Document model.
        """
        table_name = 'documents'

    def __str__(self):
        return f"Document[body={self.body[:50]}, title={self.title[:50]}, title_tokens={self.title_tokens[:25]},\
          body_tokens={self.body_tokens[:25]}, relevant={self.relevant}]"