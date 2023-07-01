"""
This module contains the Document model. It represents a crawled document.
"""

import peewee

from crawler.sql_models.base import BaseModel, LongTextField, JSONField, DATABASE


class Document(BaseModel):
    """
    Represents a crawled document.
    """
    id = peewee.BigAutoField(primary_key=True)
    job_id = peewee.BigIntegerField(default=None)

    @property
    def job(self):
        query = f"select * from jobs where id = {self.job_id}"
        for row in (cursor := DATABASE.execute_sql(query)).fetchall():
            job = {}
            for column, value in zip(cursor.description, row):
                job[column[0]] = value
            return job
        return None

    @job.setter
    def job(self, value):
        self.job_id = value.id

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
    # Classification
    relevant = peewee.BooleanField(default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "html": self.html,
            "title": self.title,
            "meta_description": self.meta_description,
            "meta_keywords": self.meta_keywords,
            "meta_author": self.meta_author,
            "h1": self.h1,
            "h2": self.h2,
            "h3": self.h3,
            "h4": self.h4,
            "h5": self.h5,
            "h6": self.h6,
            "body": self.body,
            "title_tokens": self.title_tokens,
            "meta_description_tokens": self.meta_description_tokens,
            "meta_keywords_tokens": self.meta_keywords_tokens,
            "meta_author_tokens": self.meta_author_tokens,
            "h1_tokens": self.h1_tokens,
            "h2_tokens": self.h2_tokens,
            "h3_tokens": self.h3_tokens,
            "h4_tokens": self.h4_tokens,
            "h5_tokens": self.h5_tokens,
            "h6_tokens": self.h6_tokens,
            "body_tokens": self.body_tokens,
            "relevant": self.relevant
        }

    class Meta:
        """
        Meta class for the Document model.
        """
        table_name = 'documents'

    def __eq__(self, other):
        return self.html == other.html

    def __hash__(self):
        return hash(self.meta_description)

    def __str__(self):
        return f"""Document[
    body={self.body[:50]}, 
    title={self.title[:50]}, 
    title_tokens={self.title_tokens},
    meta_description_tokens={self.meta_description_tokens},
    meta_keywords_tokens={self.meta_keywords_tokens},
    meta_author_tokens={self.meta_author_tokens},
    h1_tokens={self.h1_tokens},
    h2_tokens={self.h2_tokens},
    h3_tokens={self.h3_tokens},
    h4_tokens={self.h4_tokens},
    h5_tokens={self.h5_tokens},
    h6_tokens={self.h6_tokens},
    body_tokens={self.body_tokens}, 
    relevant={self.relevant}
]"""
