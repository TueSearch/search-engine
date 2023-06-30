import peewee
import os
from dotenv import load_dotenv
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

from backend.build_index import read_short_inverted_index
from backend.streamers import *
from crawler import utils
from crawler.sql_models.base import BaseModel
from crawler.sql_models.document import Document

load_dotenv()
TFIDF_VECTORIZER_FILE = os.getenv("TFIDF_VECTORIZER_FILE")
TFIDF_NGRAM_RANGE = tuple(json.loads(os.getenv("TFIDF_NGRAM_RANGE")))
LOG = utils.get_logger(__file__)


class Tfidf(BaseModel):
    id = peewee.BigAutoField(peewee.ForeignKeyField(Document), primary_key=True)
    title = peewee.BlobField()
    meta_description = peewee.BlobField()
    meta_keywords = peewee.BlobField()
    meta_author = peewee.BlobField()
    h1 = peewee.BlobField()
    h2 = peewee.BlobField()
    h3 = peewee.BlobField()
    h4 = peewee.BlobField()
    h5 = peewee.BlobField()
    h6 = peewee.BlobField()
    body = peewee.BlobField()

    class Meta:
        table_name = 'tfidfs'


def train_tf_idf_vectorizer():
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
    _, doc_ids = read_short_inverted_index()
    try:
        vectorizers["title"].fit(DocumentTitleStringStreamer(doc_ids))
        LOG.info("Fitted title vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting title vectorizer {e}")
    try:
        vectorizers["meta_description"].fit(DocumentMetaDescriptionStringStreamer(doc_ids))
        LOG.info("Fitted meta_description vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting meta_description vectorizer {e}")
    try:
        vectorizers["meta_keywords"].fit(DocumentMetaKeywordsStringStreamer(doc_ids))
        LOG.info("Fitted meta_keywords vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting meta_keywords vectorizer {e}")
    try:
        vectorizers["meta_author"].fit(DocumentMetaAuthorStringStreamer(doc_ids))
        LOG.info("Fitted meta_author vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting meta_author vectorizer {e}")
    try:
        vectorizers["h1"].fit(DocumentH1StringStreamer(doc_ids))
        LOG.info("Fitted h1 vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting h1 vectorizer {e}")
    try:
        vectorizers["h2"].fit(DocumentH2StringStreamer(doc_ids))
        LOG.info("Fitted h2 vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting h2 vectorizer {e}")
    try:
        vectorizers["h3"].fit(DocumentH3StringStreamer(doc_ids))
        LOG.info("Fitted h3 vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting h3 vectorizer {e}")
    try:
        vectorizers["h4"].fit(DocumentH4StringStreamer(doc_ids))
        LOG.info("Fitted h4 vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting h4 vectorizer {e}")
    try:
        vectorizers["h5"].fit(DocumentH5StringStreamer(doc_ids))
        LOG.info("Fitted h5 vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting h5 vectorizer {e}")
    try:
        vectorizers["h6"].fit(DocumentH6StringStreamer(doc_ids))
        LOG.info("Fitted h6 vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting h6 vectorizer {e}")
    try:
        vectorizers["body"].fit(DocumentBodyStringStreamer(doc_ids))
        LOG.info("Fitted body vectorizer")
    except Exception as e:
        LOG.error(f"Error while fitting body vectorizer {e}")
    utils.io.write_pickle_file(vectorizers, TFIDF_VECTORIZER_FILE)
    LOG.info(f"Wrote TF-IDF file to {TFIDF_VECTORIZER_FILE}")


def read_tfidf_vectorizer():
    return utils.io.read_pickle_file(TFIDF_VECTORIZER_FILE)


def tfidf_vectorize_indexed_documents():
    LOG.info("Start vectorize database's documents with the global TF-IDF to database")
    _, doc_ids = read_short_inverted_index()
    vectorizers = read_tfidf_vectorizer()
    for document in tqdm(DocumentStreamer(doc_ids)):
        try:
            tfidf, created = Tfidf.get_or_create(id=document.id)
            try:
                tfidf.title = vectorizers["title"].transform([" ".join(document.title_tokens)])[0]
            except Exception as e:
                LOG.error(f"Error while transforming title {e}")
            try:
                tfidf.meta_description = \
                    vectorizers["meta_description"].transform([" ".join(document.meta_description_tokens)])[
                        0]
            except Exception as e:
                LOG.error(f"Error while transforming meta_description {e}")
            try:
                tfidf.meta_keywords = vectorizers["meta_keywords"].transform([" ".join(document.meta_keywords_tokens)])[
                    0]
            except Exception as e:
                LOG.error(f"Error while transforming meta_keywords {e}")
            try:
                tfidf.meta_author = vectorizers["meta_author"].transform([" ".join(document.meta_author_tokens)])[0]
            except Exception as e:
                LOG.error(f"Error while transforming meta_author {e}")
            try:
                tfidf.h1 = vectorizers["h1"].transform([" ".join(document.h1_tokens)])[0]
            except Exception as e:
                LOG.error(f"Error while transforming h1 {e}")
            try:
                tfidf.h2 = vectorizers["h2"].transform([" ".join(document.h2_tokens)])[0]
            except Exception as e:
                LOG.error(f"Error while transforming h2 {e}")
            try:
                tfidf.h3 = vectorizers["h3"].transform([" ".join(document.h3_tokens)])[0]
            except Exception as e:
                LOG.error(f"Error while transforming h3 {e}")
            try:
                tfidf.h4 = vectorizers["h4"].transform([" ".join(document.h4_tokens)])[0]
            except Exception as e:
                LOG.error(f"Error while transforming h4 {e}")
            try:
                tfidf.h5 = vectorizers["h5"].transform([" ".join(document.h5_tokens)])[0]
            except Exception as e:
                LOG.error(f"Error while transforming h5 {e}")
            try:
                tfidf.h6 = vectorizers["h6"].transform([" ".join(document.h6_tokens)])[0]
            except Exception as e:
                LOG.error(f"Error while transforming h6 {e}")
            try:
                tfidf.body = vectorizers["body"].transform([" ".join(document.body_tokens)])[0]
            except Exception as e:
                LOG.error(f"Error while transforming body {e}")
            tfidf.save()
        except Exception as e:
            LOG.error(f"Can not write results of global TF-IDF of one entry to database: {e}")
    LOG.info("Finished vectorize database's documents with the global TF-IDF to database")
