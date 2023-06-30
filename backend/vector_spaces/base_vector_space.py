import abc
import functools

import peewee

from crawler.sql_models.document import BaseModel, Document


class BaseVectorSpaceModel(BaseModel):
    """
    Represents a crawled document.
    """
    document = peewee.DeferredForeignKey(Document, backref="document_id", primary_key=True)
    blob = peewee.BlobField()

    def fit_vectorizer(self, cls):
        self.vectorizer.fit(self.generator())
        for document in self.generator():
            cls(blob=self.vectorizer.transform(document), document=document).save()

    @abc.abstractmethod
    def generator(self):
        pass

    @abc.abstractmethod
    @functools.cached_property
    def vectorizer(self):
        pass
