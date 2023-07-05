"""
This module contains the LDA vector space model.
"""
import os

import peewee
from dotenv import load_dotenv
from sklearn.decomposition import LatentDirichletAllocation
from tqdm import tqdm

from backend.vector_spaces.tfidf import Tfidf
from crawler import utils
from crawler.sql_models.base import BaseModel, PickleField

load_dotenv()

LOG = utils.get_logger(__name__)


class Lda(BaseModel):
    """
    This class represents a LDA topic probability vector for a document.
    """
    id = peewee.IntegerField(primary_key=True)
    probabilities = PickleField()

    class Meta:
        table_name = 'ldas'


def train_lda_vectorizer():
    """
    This function trains a LDA model on the TF-IDF vectors of the documents.
    """
    lda_model = LatentDirichletAllocation(n_components=7, random_state=42, max_iter=10, learning_method='online')
    LOG.info("Training LDA model...")
    for tfidf in tqdm(Tfidf.select()):
        try:
            lda_model.fit(tfidf.body)
        except Exception as error:
            LOG.error(f"Error while training LDA model: {error}")
    LOG.info("Saving LDA model...")
    utils.io.write_pickle_file(lda_model, os.getenv('LDA_MODEL_FILE'))
    LOG.info(f"Done saving LDA model at {os.getenv('LDA_MODEL_FILE')}.")


def read_lda_model():
    """
    This function reads the LDA model from the file system.
    """
    return utils.io.read_pickle_file(os.getenv('LDA_MODEL_FILE'))


def lda_vectorize_indexed_documents():
    """
    This function vectorizes a document using the LDA model.
    """
    lda_model = read_lda_model()
    for tfidf in tqdm(Tfidf.select()):
        try:
            lda = Lda(probabilities=lda_model.fit(tfidf.vector))
            lda.save()
        except Exception as error:
            LOG.error(f"Error while LDA-vectorizing document: {error}")
