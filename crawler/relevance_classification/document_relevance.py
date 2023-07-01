"""
This module contains the document relevance classification logic.

The document relevance classification is based on the following two criteria:
- The document is relevant if the title or the body or the url contains variations of the word "Tübingen".
and
- The document is relevant if the title or the body contains English words.
"""
import json
import os
import functools

from dotenv import load_dotenv

from crawler import utils

load_dotenv()

TUEBINGEN_WRITING_STYLES = set(json.loads(
    os.getenv("TUEBINGEN_WRITING_STYLES")))
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
    for tuebingen in TUEBINGEN_WRITING_STYLES:
        for token in tokens:
            if tuebingen in token:
                return True
    return False


@functools.lru_cache(maxsize=1000)
def get_document_approximated_relevance_score_for(document: 'Document'):
    text_fields = [
        document.body,
        document.title,
        document.meta_description,
    ]
    json_fields = [
        document.body_tokens,
        document.title_tokens,
        document.meta_description_tokens,
        document.meta_keywords_tokens,
        document.meta_author_tokens,
        document.h1_tokens,
        document.h2_tokens,
        document.h3_tokens,
        document.h4_tokens,
        document.h5_tokens,
        document.h6_tokens
    ]
    is_english = any([utils.text.do_text_contain_english_content(field) for field in text_fields])
    if not is_english:
        return 0

    score = 1
    for field in text_fields:
        score += utils.text.do_text_contain_english_content(field)
    for field in json_fields:
        score += do_tokens_contain_tuebingen(field)
    return score


@functools.lru_cache(maxsize=1000)
def is_document_relevant(document: 'Document'):
    """Classify the relevance of a crawled document.

    Args:
        document (Document): The crawled document to be classified.
    """
    return get_document_approximated_relevance_score_for(document) > 0
