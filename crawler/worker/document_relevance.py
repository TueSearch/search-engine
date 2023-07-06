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

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from crawler import utils

load_dotenv()

TUEBINGEN_WRITING_STYLES = utils.io.read_json_file("data/tuebingen_writing_styles.json")
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


def does_text_contain_tuebingen(text: str):
    """
    Checks if a list of tokens contains variations of the word "Tübingen".

    Args:
        tokens (list): List of tokens.

    Returns:
        bool: True if the word variations of "Tübingen" are present in the tokens, False otherwise.
    """
    text = text.lower()
    for tuebingen in TUEBINGEN_WRITING_STYLES:
        if tuebingen in text:
            return True
    return False


@functools.lru_cache(maxsize=1)
def get_always_keep_documents():
    with open("data/always_keep_documents.json", "r", encoding="utf-8") as file:
        return set(json.load(file))


def has_lang_en(html_content: str) -> bool:
    """
    Checks if the html content has the lang attribute set to "en".
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        lang_attribute = soup.html.get('lang')
        return "en" in lang_attribute
    except:
        return False


def is_document_relevant(url: 'URL', document: 'Document'):
    """Classify the relevance of a crawled document.

    Args:
        document (Document): The crawled document to be classified.
    """
    for always_keep_document in get_always_keep_documents():
        if always_keep_document in str(url):
            return True

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

    # Must contain english content.
    english_score = int(has_lang_en(document.html))
    if english_score == 0:
        for field in text_fields:
            english_score += utils.text.do_text_contain_english_content(field)
        if english_score == 0:
            return False

    # Must contain Tübingen.
    tubingen_score = 0
    for field in json_fields:
        tubingen_score += do_tokens_contain_tuebingen(field)
        if tubingen_score > 0:
            break
    if tubingen_score == 0:
        tubingen_score += int(does_text_contain_tuebingen(document.body))
    if tubingen_score == 0:
        return False

    # Should not be blocked.
    if isinstance(url, str):
        from crawler.worker.url_relevance import URL
        url = URL(url)
    if url.contains_blocked_patterns:
        return False
    return True
