import functools
import os

from dotenv import load_dotenv

from crawler import utils
from crawler.utils import get_logger
from crawler.ml_models.url_relevance_trainer import prepare_urls_for_models

LOG = get_logger(__name__)
load_dotenv()


@functools.lru_cache
def read_model():
    """
    Read the model from
    """

    xgb_classifier, vectorizer = utils.io.read_pickle_file(os.getenv("CRAWLER_URL_ML_CLASSIFIER_FILE"))
    return xgb_classifier, vectorizer


def ml_predict_url_relevance(url: 'URL'):
    """
    Return binary label prediction of url's relevance.
    """
    xgb_classifier, vectorizer = read_model()
    features = prepare_urls_for_models([url.url_tokens], [url.anchor_text_tokens])
    return int(xgb_classifier.predict(vectorizer.transform(features))[0])
