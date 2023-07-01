"""
Streamers for streaming sentences from relevant documents.
"""
import functools
from numpy.typing import ArrayLike
from crawler.sql_models.document import Document


class DocumentStreamer:
    """
    A class to stream sentences from models to avoid eager loading.
    """

    def stream(self):
        """
        Stream tokens from relevant documents.
        :return: a generator
        """
        if self.ids is None:
            for doc in Document.select().where(Document.relevant == True).iterator():
                yield self.transform(doc)
        else:
            for doc_id in self.ids:
                doc = Document.get_by_id(doc_id)
                yield self.transform(doc)

    def __init__(self, ids: ArrayLike = None, transform=lambda doc: doc):
        """
        Stream sentences from relevant documents.

        Args:
            ids (list[int] | np.array): List of document IDs.
        """
        self.ids = ids
        self.transform = transform
        self.generator = self.stream()

    def __iter__(self):
        """
        Reset the generator and return the iterator object.

        Returns:
            Streams: Iterator object for streaming sentences.
        """
        self.generator = self.stream()
        return self

    def __next__(self):
        """
        Get the next sentence from the generator.

        Returns:
            str: Concatenated sentence from a relevant document.

        Raises:
            StopIteration: If there are no more sentences to yield.
        """
        result = next(self.generator)
        if result is None:
            raise StopIteration
        return result


def partial(func):
    """
    Help function to create more streams.
    """
    # pylint: disable=invalid-name
    DocumentTokensStreamer = functools.partial(DocumentStreamer, transform=func)
    # pylint: disable=invalid-name
    DocumentStringStreamer = functools.partial(DocumentStreamer,
                                               transform=lambda doc: " ".join(func(doc)))
    return DocumentTokensStreamer, DocumentStringStreamer


DocumentTitleTokensStreamer, DocumentTitleStringStreamer = partial(lambda doc: doc.title_tokens)
DocumentMetaDescriptionTokensStreamer, DocumentMetaDescriptionStringStreamer = partial(
    lambda doc: doc.meta_description_tokens)
DocumentMetaKeywordsTokensStreamer, DocumentMetaKeywordsStringStreamer = partial(lambda doc: doc.meta_keywords_tokens)
DocumentMetaAuthorTokensStreamer, DocumentMetaAuthorStringStreamer = partial(lambda doc: doc.meta_author_tokens)
DocumentH1TokensStreamer, DocumentH1StringStreamer = partial(lambda doc: doc.h1_tokens)
DocumentH2TokensStreamer, DocumentH2StringStreamer = partial(lambda doc: doc.h2_tokens)
DocumentH3TokensStreamer, DocumentH3StringStreamer = partial(lambda doc: doc.h3_tokens)
DocumentH4TokensStreamer, DocumentH4StringStreamer = partial(lambda doc: doc.h4_tokens)
DocumentH5TokensStreamer, DocumentH5StringStreamer = partial(lambda doc: doc.h5_tokens)
DocumentH6TokensStreamer, DocumentH6StringStreamer = partial(lambda doc: doc.h6_tokens)
DocumentBodyTokensStreamer, DocumentBodyStringStreamer = partial(lambda doc: doc.body_tokens)
