import peewee
import os
from dotenv import load_dotenv
import json

from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm import tqdm

from backend.streamers import DocumentTitleStringStreamer, DocumentStreamer, DocumentBodyStringStreamer
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


def train():
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
    try:
        vectorizers["title"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["meta_description"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["meta_keywords"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["meta_author"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["h1"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["h2"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["h3"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["h4"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["h5"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["h6"].fit(DocumentTitleStringStreamer())
    except:
        pass
    try:
        vectorizers["body"].fit(DocumentBodyStringStreamer())
    except:
        pass
    utils.io.write_pickle_file(vectorizers, TFIDF_VECTORIZER_FILE)
    LOG.info(f"Wrote TF-IDF file to {TFIDF_VECTORIZER_FILE}")

def transform():
    LOG.info("Start vectorize database's documents with the global TF-IDF to database")
    vectorizers = utils.io.read_pickle_file(TFIDF_VECTORIZER_FILE)
    for document in tqdm(DocumentStreamer()):
        try:
            tfidf, created = Tfidf.get_or_create(id=document.id)
            try:
                tfidf.title = vectorizers["title"].transform([" ".join(document.title_tokens)])[0]
            except:
                pass
            try:
                tfidf.meta_description = vectorizers["meta_description"].transform([" ".join(document.meta_description_tokens)])[
                    0]
            except:
                pass
            try:
                tfidf.meta_keywords = vectorizers["meta_keywords"].transform([" ".join(document.meta_keywords_tokens)])[0]
            except:
                pass
            try:
                tfidf.meta_author = vectorizers["meta_author"].transform([" ".join(document.meta_author_tokens)])[0]
            except:
                pass
            try:
                tfidf.h1 = vectorizers["h1"].transform([" ".join(document.h1_tokens)])[0]
            except:
                pass
            try:
                tfidf.h2 = vectorizers["h2"].transform([" ".join(document.h2_tokens)])[0]
            except:
                pass
            try:
                tfidf.h3 = vectorizers["h3"].transform([" ".join(document.h3_tokens)])[0]
            except:
                pass
            try:
                tfidf.h4 = vectorizers["h4"].transform([" ".join(document.h4_tokens)])[0]
            except:
                pass
            try:
                tfidf.h5 = vectorizers["h5"].transform([" ".join(document.h5_tokens)])[0]
            except:
                pass
            try:
                tfidf.h6 = vectorizers["h6"].transform([" ".join(document.h6_tokens)])[0]
            except:
                pass
            try:
                tfidf.body = vectorizers["body"].transform([" ".join(document.body_tokens)])[0]
            except:
                pass
            tfidf.save()
        except Exception as e:
            LOG.error(f"Can not write results of global TF-IDF of one entry to database: {e}")
    LOG.info("Finished vectorize database's documents with the global TF-IDF to database")
