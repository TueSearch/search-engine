"""
This module contains functions to check if a URL is relevant for the crawler.
"""
import json
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
import validators

from crawler import utils
from tldextract import extract

load_dotenv()

CRAWL_EXCLUDED_EXTENSIONS = set(json.loads(
    os.getenv("CRAWL_EXCLUDED_EXTENSIONS")))
CRAWL_BLACK_LIST = set(json.loads(os.getenv("CRAWL_BLACK_LIST")))
QUEUE_MANUAL_SEEDS = json.loads(os.getenv('QUEUE_MANUAL_SEEDS'))
CRAWL_PRIORITY_LIST = json.loads(os.getenv('CRAWL_PRIORITY_LIST'))

def get_url_extension(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    _, file_extension = os.path.splitext(path)
    return file_extension


def is_url_media_link(url):
    """
    Check if a URL is a "normal" text URL.

    Args:
        url (str): The URL to check.

    Returns:
        bool: True if the URL is a "normal" text URL, False otherwise.
    """
    ext = get_url_extension(url)
    for exclued_extension in CRAWL_EXCLUDED_EXTENSIONS:
        if exclued_extension in ext:
            return True
    return False


def get_url_priority(url: str) -> int:
    """
    Get the priority of a URL.
    Args:
        url: The URL to get the priority of.

    Returns: The priority of the URL. The higher the number, the higher the priority.

    """
    if not is_url(url):
        return -1

    if is_url_media_link(url):
        return -1

    if utils.url.get_server_name_from_url(url) in CRAWL_BLACK_LIST:
        return -1

    tokens = utils.url.tokenize_url(
        "https://tuebingenresearchcampus.com/en/research-in-tuebingen/tnc/neuro-campus-initiatives/")
    priority = 1
    has_tuebingen = has_bingen = False
    for token in tokens:
        if "tübingen" in token or "tuebingen" in token or "tubingen" in token:
            has_tuebingen = True
        if "bingen" in token:
            has_bingen = True
    is_english = "en" in tokens or "/en/" in url or "en." in url or utils.text.do_text_contain_english_content(
        " ".join(tokens))
    for priority_url in CRAWL_PRIORITY_LIST:
        if priority_url in url:
            priority += 20
    if has_bingen:
        priority += 3
    if has_tuebingen:
        priority += 5
    if is_english:
        priority += 3
    if is_english and has_bingen:
        priority += 10
    if is_english and has_tuebingen:
        priority += 15
    if url in QUEUE_MANUAL_SEEDS:
        priority += 100
    if extract(url).suffix == "com":
        priority += 1
    return priority


def is_url(text: str) -> bool:
    """
    Check if a text is a URL.
    """

    def test1():
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc])
        except:
            return False

    def test2():
        result = validators.url(text)
        if isinstance(result, validators.ValidationFailure):
            return False
        return result

    return test1() and test2()


def is_url_relevant(url: str) -> bool:
    """
    Check if a URL is relevant for the crawler.
    Args:
        url: The URL to check.
    Returns: True if the URL is relevant, False otherwise.
    """
    return get_url_priority(url) > 0
