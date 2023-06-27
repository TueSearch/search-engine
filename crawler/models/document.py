"""
This module contains the Document model. It represents a crawled document.
"""
import functools
import json
import pickle

import numpy as np
import peewee

from crawler.models.base import BaseModel, LongTextField


class Document(BaseModel):
    """
    Represents a crawled document.
    """
    id = peewee.BigAutoField(primary_key=True)
    url = LongTextField()
    server = LongTextField()
    title = LongTextField()
    body = LongTextField()
    title_tokens = LongTextField()
    body_tokens = LongTextField()
    all_harvested_links = LongTextField()
    relevant_links = LongTextField()
    body_global_tfidf_vector = peewee.BlobField()
    relevant = peewee.BooleanField(default=True)

    class Meta:
        """Metadata options for the Document model."""
        table_options = {'engine': 'RocksDB'}
        indexes = (
            peewee.SQL('create unique index url_index on document (url(750))'),
        )

    @functools.cached_property
    def all_harvested_links_list(self) -> list[str]:
        """Get a list of all harvested links."""
        return json.loads(str(self.all_harvested_links))

    @functools.cached_property
    def relevant_links_list(self) -> list[str]:
        """Get a list of relevant links."""
        return json.loads(str(self.relevant_links))

    @functools.cached_property
    def body_tokens_list(self) -> list[str]:
        """Get a list of tokens."""
        return json.loads(str(self.body_tokens))

    @functools.cached_property
    def title_tokens_list(self) -> list[str]:
        """Get a list of tokens."""
        return json.loads(str(self.title_tokens))

    @property
    def numpy_body_global_tfidf_vector(self) -> np.array:
        return pickle.loads(self.body_global_tfidf_vector)

    def __str__(self):
        return f"Document[body={self.body[:50]}, title={self.title[:50]}, title_tokens={self.title_tokens_list[:25]},\
          body_tokens={self.body_tokens_list[:25]}, all_harvested_links={self.all_harvested_links_list[:10]}, relevant={self.relevant}]"
