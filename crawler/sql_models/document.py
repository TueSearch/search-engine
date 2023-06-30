"""
This module contains the Document model. It represents a crawled document.
"""
import peewee

from crawler.sql_models.base import BaseModel, LongTextField, JSONField


class Document(BaseModel):
    """
    Represents a crawled document.
    """
    id = peewee.BigAutoField(primary_key=True)
    job = peewee.DeferredForeignKey('jobs', backref="job_id")
    # Raw data field
    html = LongTextField(default="")
    # Raw text Fields
    title = LongTextField(default="")
    meta_description = LongTextField(default="")
    meta_keywords = LongTextField(default="")
    meta_author = LongTextField(default="")
    h1 = LongTextField(default="")
    h2 = LongTextField(default="")
    h3 = LongTextField(default="")
    h4 = LongTextField(default="")
    h5 = LongTextField(default="")
    h6 = LongTextField(default="")
    body = LongTextField(default="")
    # Processed text fields
    title_tokens = JSONField(default=[])
    meta_description_tokens = JSONField(default=[])
    meta_keywords_tokens = JSONField(default=[])
    meta_author_tokens = JSONField(default=[])
    h1_tokens = JSONField(default=[])
    h2_tokens = JSONField(default=[])
    h3_tokens = JSONField(default=[])
    h4_tokens = JSONField(default=[])
    h5_tokens = JSONField(default=[])
    h6_tokens = JSONField(default=[])
    body_tokens = JSONField(default=[])
    # Links
    links = JSONField(default=[])
    relevant_links = JSONField(default=[])
    # Classification
    relevant = peewee.BooleanField(default=True)

    class Meta:
        """
        Meta class for the Document model.
        """
        table_name = 'documents'

    def __str__(self):
        return f"Document[body={self.body[:50]}, title={self.title[:50]}, title_tokens={self.title_tokens[:25]},\
          body_tokens={self.body_tokens[:25]}, relevant={self.relevant}]"
