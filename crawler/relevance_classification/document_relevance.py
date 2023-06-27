"""
This module contains the document relevance classification logic.

The document relevance classification is based on the following two criteria:
- The document is relevant if the title or the body or the url contains variations of the word "Tübingen".
and
- The document is relevant if the title or the body contains English words.
"""
import json
import os

from dotenv import load_dotenv

from crawler import utils
from crawler.models import Document
from crawler.relevance_classification.url_relevance import is_url_relevant

load_dotenv()

INVERTED_INDEX_TUEBINGEN_WRITING_STYLES = set(json.loads(
    os.getenv("INVERTED_INDEX_TUEBINGEN_WRITING_STYLES")))
CRAWL_ENGLISH_CLASSIFICATION_THRESHOLD = float(
    os.getenv("CRAWL_ENGLISH_CLASSIFICATION_THRESHOLD"))
CRAWL_ENGLISH_CLASSIFICATION_MULTI_THRESHOLD = float(
    os.getenv("CRAWL_ENGLISH_CLASSIFICATION_MULTI_THRESHOLD"))


def do_tokens_contain_tuebingen(tokens: list[str]):
    """
    Checks if a list of tokens contains variations of the word "Tübingen".

    Args:
        tokens (list): List of tokens.

    Returns:
        bool: True if the word variations of "Tübingen" are present in the tokens, False otherwise.
    """
    for tuebingen in INVERTED_INDEX_TUEBINGEN_WRITING_STYLES:
        for token in tokens:
            if tuebingen in token:
                return True
    return False


def is_document_relevant(document: Document):
    """Classify the relevance of a crawled document.

    Args:
        document (Document): The crawled document to be classified.
    """
    title_is_relevant = do_tokens_contain_tuebingen(document.title_tokens_list)
    body_is_relevant = do_tokens_contain_tuebingen(document.body_tokens_list)
    url_is_relevant = is_url_relevant(document.url)
    is_english = utils.text.do_text_contain_english_content(document.body)
    return (title_is_relevant or body_is_relevant or url_is_relevant) and is_english
