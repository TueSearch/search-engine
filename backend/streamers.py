"""
Streamers for streaming sentences from relevant documents.
"""
import functools
from numpy.typing import ArrayLike
from crawler.models import Document


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


DocumentTokensStreamer = functools.partial(DocumentStreamer, transform=lambda doc: " ".join(doc.body_tokens_list))
DocumentBodyGlobalTfidfVectorStreamer = functools.partial(DocumentStreamer,
                                                          transform=lambda doc: doc.numpy_body_global_tfidf_vector)
