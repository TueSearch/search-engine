"""
This module contains the TF-IDF vectorizer class and the function to train it.
"""
import json
import os

import numpy as np
import peewee
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

from backend.update_index import read_index_file
from backend.streamers import DocumentTitleStringStreamer, DocumentMetaDescriptionStringStreamer, \
    DocumentMetaKeywordsStringStreamer, DocumentMetaAuthorStringStreamer, DocumentH1StringStreamer, \
    DocumentH2StringStreamer, DocumentH3StringStreamer, DocumentH4StringStreamer, DocumentH5StringStreamer, \
    DocumentH6StringStreamer, DocumentBodyStringStreamer, DocumentStreamer
from crawler import utils
from crawler.sql_models.base import BaseModel, PickleField

load_dotenv()
TFIDF_VECTORIZER_FILE = os.getenv("TFIDF_VECTORIZER_FILE")
TFIDF_NGRAM_RANGE = tuple(json.loads(os.getenv("TFIDF_NGRAM_RANGE")))
LOG = utils.get_logger(__file__)


class Tfidf(BaseModel):
    """
    This class represents a TF-IDF vector for a document.
    The blob field contains vectors for the document.
    """
    id = peewee.IntegerField(primary_key=True)
    title = PickleField()
    meta_description = PickleField()
    meta_keywords = PickleField()
    meta_author = PickleField()
    h1 = PickleField()
    h2 = PickleField()
    h3 = PickleField()
    h4 = PickleField()
    h5 = PickleField()
    h6 = PickleField()
    body = PickleField()

    class Meta:
        """
        This class represents the metadata for the TF-IDF model.
        """
        table_name = 'tfidfs'

    def not_null_vectors(self) -> dict[str, np.array]:
        """
        Returns the vectors that are not null.
        """
        returned_vectors = {}
        if self.title is not None:
            returned_vectors["title"] = self.title
        if self.meta_description is not None:
            returned_vectors["meta_description"] = self.meta_description
        if self.meta_keywords is not None:
            returned_vectors["meta_keywords"] = self.meta_keywords
        if self.meta_author is not None:
            returned_vectors["meta_author"] = self.meta_author
        if self.h1 is not None:
            returned_vectors["h1"] = self.h1
        if self.h2 is not None:
            returned_vectors["h2"] = self.h2
        if self.h3 is not None:
            returned_vectors["h3"] = self.h3
        if self.h4 is not None:
            returned_vectors["h4"] = self.h4
        if self.h5 is not None:
            returned_vectors["h5"] = self.h5
        if self.h6 is not None:
            returned_vectors["h6"] = self.h6
        if self.body is not None:
            returned_vectors["body"] = self.body
        return returned_vectors


def train_tfidf_vectorizer():
    """
    Train the TF-IDF vectorizer using the relevant document tokens.

    The TF-IDF vectorizer is fitted on the concatenated sentences from the relevant documents.
    The fitted vectorizer is then saved as a pickle file.
    """
    LOG.info("Start build global tfidf")
    vectorizers = {
        "title": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "meta_description": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "meta_keywords": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "meta_author": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "h1": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "h2": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "h3": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "h4": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "h5": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "h6": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
        "body": TfidfVectorizer(ngram_range=TFIDF_NGRAM_RANGE),
    }
    _, doc_ids = read_index_file()
    try:
        vectorizers["title"].fit(DocumentTitleStringStreamer(doc_ids))
        LOG.info("Fitted title vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting title vectorizer {exception}")
    try:
        vectorizers["meta_description"].fit(DocumentMetaDescriptionStringStreamer(doc_ids))
        LOG.info("Fitted meta_description vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting meta_description vectorizer {exception}")
    try:
        vectorizers["meta_keywords"].fit(DocumentMetaKeywordsStringStreamer(doc_ids))
        LOG.info("Fitted meta_keywords vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting meta_keywords vectorizer {exception}")
    try:
        vectorizers["meta_author"].fit(DocumentMetaAuthorStringStreamer(doc_ids))
        LOG.info("Fitted meta_author vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting meta_author vectorizer {exception}")
    try:
        vectorizers["h1"].fit(DocumentH1StringStreamer(doc_ids))
        LOG.info("Fitted h1 vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting h1 vectorizer {exception}")
    try:
        vectorizers["h2"].fit(DocumentH2StringStreamer(doc_ids))
        LOG.info("Fitted h2 vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting h2 vectorizer {exception}")
    try:
        vectorizers["h3"].fit(DocumentH3StringStreamer(doc_ids))
        LOG.info("Fitted h3 vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting h3 vectorizer {exception}")
    try:
        vectorizers["h4"].fit(DocumentH4StringStreamer(doc_ids))
        LOG.info("Fitted h4 vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting h4 vectorizer {exception}")
    try:
        vectorizers["h5"].fit(DocumentH5StringStreamer(doc_ids))
        LOG.info("Fitted h5 vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting h5 vectorizer {exception}")
    try:
        vectorizers["h6"].fit(DocumentH6StringStreamer(doc_ids))
        LOG.info("Fitted h6 vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting h6 vectorizer {exception}")
    try:
        vectorizers["body"].fit(DocumentBodyStringStreamer(doc_ids))
        LOG.info("Fitted body vectorizer")
    except Exception as exception:
        LOG.error(f"Error while fitting body vectorizer {exception}")
    utils.io.write_pickle_file(vectorizers, TFIDF_VECTORIZER_FILE)
    LOG.info(f"Wrote TF-IDF file to {TFIDF_VECTORIZER_FILE}")


def read_tfidf_vectorizers() -> dict[str, TfidfVectorizer]:
    """
    Read the TF-IDF vectorizers from the pickle file.
    The structure of the returned dictionary is as follows:
    {
        "title": TfidfVectorizer,
        "meta_description": TfidfVectorizer,
        "meta_keywords": TfidfVectorizer,
        "meta_author": TfidfVectorizer,
        "h1": TfidfVectorizer,
        "h2": TfidfVectorizer,
        "h3": TfidfVectorizer,
        "h4": TfidfVectorizer,
        "h5": TfidfVectorizer,
        "h6": TfidfVectorizer,
        "body": TfidfVectorizer,
    }
    """
    return utils.io.read_pickle_file(TFIDF_VECTORIZER_FILE)


def tfidf_vectorize_indexed_documents():
    """
    Vectorize the indexed documents with the global TF-IDF.
    """
    LOG.info("Start vectorize database's documents with the global TF-IDF to database")
    _, doc_ids = read_index_file()
    vectorizers = read_tfidf_vectorizers()
    for document in tqdm(DocumentStreamer(doc_ids)):
        try:
            tfidf, _ = Tfidf.get_or_create(id=document.id)
            try:
                tfidf.title = vectorizers["title"].transform([" ".join(document.title_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming title {exception}")
            try:
                tfidf.meta_description = \
                    vectorizers["meta_description"].transform([" ".join(document.meta_description_tokens)])[
                        0]
            except Exception as exception:
                LOG.error(f"Error while transforming meta_description {exception}")
            try:
                tfidf.meta_keywords = vectorizers["meta_keywords"].transform([" ".join(document.meta_keywords_tokens)])[
                    0]
            except Exception as exception:
                LOG.error(f"Error while transforming meta_keywords {exception}")
            try:
                tfidf.meta_author = vectorizers["meta_author"].transform([" ".join(document.meta_author_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming meta_author {exception}")
            try:
                tfidf.h1 = vectorizers["h1"].transform([" ".join(document.h1_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming h1 {exception}")
            try:
                tfidf.h2 = vectorizers["h2"].transform([" ".join(document.h2_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming h2 {exception}")
            try:
                tfidf.h3 = vectorizers["h3"].transform([" ".join(document.h3_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming h3 {exception}")
            try:
                tfidf.h4 = vectorizers["h4"].transform([" ".join(document.h4_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming h4 {exception}")
            try:
                tfidf.h5 = vectorizers["h5"].transform([" ".join(document.h5_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming h5 {exception}")
            try:
                tfidf.h6 = vectorizers["h6"].transform([" ".join(document.h6_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming h6 {exception}")
            try:
                tfidf.body = vectorizers["body"].transform([" ".join(document.body_tokens)])[0]
            except Exception as exception:
                LOG.error(f"Error while transforming body {exception}")
            tfidf.save()
        except Exception as exception:
            LOG.error(f"Can not write results of global TF-IDF of one entry to database: {exception}")
    LOG.info("Finished vectorize database's documents with the global TF-IDF to database")
